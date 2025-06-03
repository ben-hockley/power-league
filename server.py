from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from routers import accounts, user_actions, user_views, admin

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from typing import Annotated
from pydantic import BaseModel, StringConstraints, constr
import os

import datetime
import string

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from repositories.user_repository import create_user, check_password, get_user_id, get_user_by_id
from repositories.player_repository import get_depth_chart_by_position, save_depth_chart,\
get_players_by_team, age_league_players, create_draft_class, get_draft_class, get_free_agents,\
cut_player, sign_player, get_star_players, get_all_players_by_league
from repositories.league_repository import get_standings, get_league, get_league_id,\
get_public_leagues, get_all_leagues, get_league_year, generate_schedule, get_fixtures,\
get_today_fixtures, delete_fixture, new_season, get_reverse_standings, create_league,\
get_owned_leagues, get_league_owner_id, save_new_league, make_league_active, record_new_champion, \
get_reigning_champion_name, get_number_of_championships, get_user_championships_won, \
get_last_seasons_retirements, get_league_by_code
from repositories.team_repository import get_teams_by_user_id, get_team_by_id, get_team_owner_id,\
create_new_team, get_team_league_id, add_result_to_team, get_all_teams, wipe_league_records,\
delete_team, get_standings, order_depth_charts, get_teams_by_league_id, get_manager_id, \
order_depth_charts_defense_by_team, order_depth_charts_offense_by_team
from repositories.game_repository import save_game, get_game_by_id, get_games_by_team_id, get_next_fixture
from repositories.draft_repository import get_players_drafted, add_draft, make_draft_pick,\
check_draft_active, get_picking_team_id, get_time_on_clock, schedule_draft, get_draft_date, \
auto_draft_pick, delete_draft, get_done_drafts
from repositories.trade_repository import get_trades_proposed, get_trades_received, save_trade, \
delete_trade, accept_trade, trade_list_player, untrade_list_player

from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from config import SECRET_KEY
from config import SERVER_HOST

from simulator import get_match_report, game_details_to_json, json_to_game_details

from fastapi import WebSocket, WebSocketDisconnect
from typing import List

from dependencies import get_current_user, require_team_owner, require_league_owner, require_admin


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

def simulate_todays_fixtures(today: datetime.date = None):
    """
    Simulate today's fixtures and save the results to the database.
    """
    # Get today's date
    if today is None:
        today = datetime.date.today()

    # Get all fixtures for today
    fixtures = get_today_fixtures()

    # Simulate each fixture
    for fixture in fixtures:
        # if the fixture is a draft (home and away team are 0), start the draft
        if fixture[2] == 0 and fixture[3] == 0:
            league_id = fixture[1]
            start_draft_no_link(league_id)
        else:
            home_team_id = int(fixture[2])
            print(home_team_id)
            away_team_id = int(fixture[3])
            print(away_team_id)
            match_report_no_link(home_team_id, away_team_id)
        # Delete the fixture from the database
        delete_fixture(fixture[0])

def start_new_season_no_link(league_id: int):
    # this is the process of initializing a new league season
    # 1 . record the new champion of the league
    record_new_champion(league_id)
    # 1. increase the league year and season number by 1
    new_season(league_id)
    # 2. age the players (includes retirements and skill changes)
    age_league_players(league_id)
    # 3. create a draft class
    create_draft_class(league_id)
    # 4.wipe the league records
    wipe_league_records(league_id)
    # 5. generate a new schedule
    generate_schedule(league_id)
    # 6. schedule the draft by saving it as a fixture where home and away team ids are 0.
    schedule_draft(league_id)
    # 7. order the depth charts in order of skill
    order_depth_charts(league_id)

app = FastAPI()
app.include_router(accounts.router)
app.include_router(user_actions.router)
app.include_router(user_views.router)
app.include_router(admin.router)


app.add_middleware(SessionMiddleware,
                   secret_key=SECRET_KEY,
                   session_cookie="session_id",
                   #https_only=True,
                   https_only=False, # for development only, set to True in production.
                   same_site="lax",
                   #secure=True, # requires HTTPS, should be used in production.
                   )

# Setup rate limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

# Setup exception handling
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("error/404.html", {"request": request}, status_code=exc.status_code)
    elif exc.status_code == 500:
        return templates.TemplateResponse("error/500.html", {"request": request}, status_code=exc.status_code)
    elif exc.status_code == 403:
        return templates.TemplateResponse("error/403.html", {"request": request}, status_code=exc.status_code)
    elif exc.status_code == 401:
        return templates.TemplateResponse("error/401.html", {"request": request}, status_code=exc.status_code)
    else:
        return templates.TemplateResponse("error/generic_error.html", {
            "request": request,
            "error_code": exc.status_code,
            "error_detail": getattr(exc, "detail", None)
            }, status_code=exc.status_code)

# Initialize the background scheduler
@app.websocket("/ws/draft")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection open
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Ensure the scheduler shuts down properly on application exit.
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    scheduler.shutdown()

# Set up Jinja2 templates directory
templates = Jinja2Templates(directory="templates")

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def login(request: Request):
    return RedirectResponse(url="/login", status_code=303)

def get_svg_content(svg_path):
    # Make sure svg_path is a safe path and exists
    if svg_path and svg_path.endswith('.svg') and os.path.exists(svg_path):
        with open(svg_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

# this is an endpoint purely for development purposes, it will be removed from the final version
@app.post("/start_draft/{team_id}")
async def start_draft(request: Request, team_id: int, auth: bool = Depends(require_admin)):
    league_id = get_league_id(team_id)
    draft_year = get_league_year(league_id)
    add_draft(league_id, draft_year)
    await manager.broadcast("reload")
    return RedirectResponse(url=f"/draft/{team_id}", status_code=303)

def start_draft_no_link(league_id: int):
    draft_year = get_league_year(league_id)
    # start the draft
    add_draft(league_id, draft_year)
    # Notify all clients to reload
    manager.broadcast("reload")

def match_report_no_link(home_team_id: int, away_team_id: int):
    GameDetails = get_match_report(home_team_id, away_team_id)

    # save data to the database
    league_id = get_team_league_id(home_team_id)
    details_json = game_details_to_json(GameDetails)

    game_id = save_game(league_id, home_team_id, away_team_id, details_json)

    game_record = get_game_by_id(game_id)
    game_details = game_record[5]
    game_details = json_to_game_details(game_details)

    # get the home score and away score for the game
    homeScore = game_details["home_score"]
    awayScore = game_details["away_score"]

    # add the result to the teams
    add_result_to_team(home_team_id, homeScore, awayScore)
    add_result_to_team(away_team_id, awayScore, homeScore)

    # load the game details
    GameDetails = game_details

    return None


def do_auto_draft_picks():
    auto_draft_pick()

    # get each draft that has no finished
    done_drafts = get_done_drafts()

    for draft in done_drafts:
        league_id = draft[1]
        draft_year = draft[2]
        if check_draft_active(league_id, draft_year) == False:
        # start a new season
            delete_draft(league_id, draft_year) # delete the draft from the database.
            start_new_season_no_link(league_id)


# Only start the scheduler in the main process (not in the reload watcher)
# this is to guard against multiple schedulers loading
if __name__ == "__main__" or os.environ.get("RUN_MAIN") == "true":
    scheduler = BackgroundScheduler()
    trigger = CronTrigger(hour=12, minute=00) # simulate games every day at midday
    scheduler.add_job(simulate_todays_fixtures, trigger, misfire_grace_time=3600)
    # add a job to check the draft clock every 10 seconds and make any picks that are yet to be made.
    scheduler.add_job(do_auto_draft_picks, 'interval', seconds=10)
    print("Scheduler started")
    scheduler.start()

if __name__ == "__main__":
    uvicorn.run("server:app", host=SERVER_HOST, port=8080, reload=True)


# BEN HOCKLEY 2025