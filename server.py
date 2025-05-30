from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

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
get_last_seasons_retirements
from repositories.team_repository import get_teams_by_user_id, get_team_by_id, get_team_owner_id,\
create_new_team, get_team_league_id, add_result_to_team, get_all_teams, wipe_league_records,\
delete_team, get_standings, order_depth_charts, get_teams_by_league_id, get_manager_id
from repositories.game_repository import save_game, get_game_by_id, get_games_by_team_id, get_next_fixture
from repositories.draft_repository import get_players_drafted, add_draft, make_draft_pick,\
check_draft_active, get_picking_team_id, get_time_on_clock, schedule_draft, get_draft_date, \
auto_draft_pick, delete_draft
from repositories.trade_repository import get_trades_proposed, get_trades_received, save_trade, \
delete_trade, accept_trade, trade_list_player, untrade_list_player

from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from config import SECRET_KEY
from config import SERVER_HOST

from simulator import get_match_report, game_details_to_json, json_to_game_details

from fastapi import WebSocket, WebSocketDisconnect
from typing import List


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
        return templates.TemplateResponse("error/generic_error.html", {"request": request}, status_code=exc.status_code)

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

# for testing purposes
#user_id = 1
#team_id = 2

def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user_id

def check_user_ownership(request: Request, team_id: int):
    user_id = get_current_user(request)
    team_owner_id = get_team_owner_id(team_id)
    if user_id == team_owner_id:
        return True
    else:
        return False        
        
def require_team_owner(request: Request, team_id: int, user_id: int = Depends(get_current_user)):
    team_owner_id = get_team_owner_id(team_id)
    if user_id != team_owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return True

def require_league_owner(request: Request, league_id: int, user_id: int = Depends(get_current_user)):
    league_owner_id = get_league_owner_id(league_id)
    if user_id != league_owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return True

def require_admin(request: Request):
    role = request.session.get("role")
    if role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return True

@app.get("/")
async def login(request: Request):
    return RedirectResponse(url="/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    request.session.clear()  # Clear any existing session data
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
#@limiter.limit("5/minute")  # Limit login attempts to 10 per minute
async def post_login(request: Request):
    request.session.clear()  # Clear any existing session data
    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    # Check if the user exists and the password is correct
    if check_password(username, password):
        user = get_user_by_id(get_user_id(username))
        request.session["user_id"] = user[0]
        request.session["role"] = user[4]  # Make sure get_user_by_id returns a dict or access by index
        return RedirectResponse(url=f"/home/{user[0]}", status_code=303)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})

@app.get("/create_account", response_class=HTMLResponse)
async def get_create_account(request: Request):
    return templates.TemplateResponse("create_account.html", {"request": request})

@app.post("/create_account")
@limiter.limit("3/minute")  # Limit account creation attempts to 3 per minute
async def create_account(request: Request):
    form = await request.form()
    # Extract the data from the form
    username = form.get("username")
    password = form.get("password")
    avatar = form.get("avatarUrl")

    # Check if the user already exists
    create_user(username, password, avatar)
    return RedirectResponse(url="/login", status_code=303)

@app.get("/delete_team/{team_id}", response_class=HTMLResponse)
async def delete_user_team(
    request: Request,
    team_id: int,
    auth: bool = Depends(require_team_owner)):
    # if not check_user_ownership(request, team_id):
        #return RedirectResponse(url="/login", status_code=303)

    # delete the team from the database
    delete_team(team_id)

    # redirect to the home page
    user_id = get_current_user(request)
    return RedirectResponse(url=f"/home/{user_id}", status_code=303)

@app.get("/depth_chart_offense/{team_id}", response_class=HTMLResponse)
async def get_depth_chart(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):

    # # if not check_user_ownership(request, team_id):
    #     return RedirectResponse(url="/login", status_code=303)

    team = get_team_by_id(team_id)

    depth_qb = get_depth_chart_by_position(team_id, "QB")
    depth_rb = get_depth_chart_by_position(team_id, "RB")
    depth_wr = get_depth_chart_by_position(team_id, "WR")
    depth_ol = get_depth_chart_by_position(team_id, "OL")

    return templates.TemplateResponse("depth_chart_offense.html", {"request": request,
                                                                    "depth_qb": depth_qb,
                                                                    "depth_rb": depth_rb,
                                                                    "depth_wr": depth_wr,
                                                                    "depth_ol": depth_ol,
                                                                    "team_id": team_id,
                                                                    "team": team})

# save depth chart changes to the database
@app.post("/depth_chart_offense/{team_id}")
async def save_depth_chart_offense_changes(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):

    ## if not check_user_ownership(request, team_id):
    #     return RedirectResponse(url="/login", status_code=303)
    
    form = await request.form()
    depth_qb = form.get("qb_order")
    depth_rb = form.get("rb_order")
    depth_wr = form.get("wr_order")
    depth_ol = form.get("ol_order")

    save_depth_chart(team_id, "QB", depth_qb)
    save_depth_chart(team_id, "RB", depth_rb)
    save_depth_chart(team_id, "WR", depth_wr)
    save_depth_chart(team_id, "OL", depth_ol)

    return RedirectResponse(url=f"/depth_chart_offense/{team_id}", status_code=303)


@app.get("/depth_chart_defense/{team_id}", response_class=HTMLResponse)
async def get_depth_chart_defense(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):

    ## if not check_user_ownership(request, team_id):
    #    return RedirectResponse(url="/login", status_code=303)

    team = get_team_by_id(team_id)

    depth_dl = get_depth_chart_by_position(team_id, "DL")
    depth_lb = get_depth_chart_by_position(team_id, "LB")
    depth_db = get_depth_chart_by_position(team_id, "DB")
    
    return templates.TemplateResponse("depth_chart_defense.html", {"request": request,
                                                                   "depth_dl": depth_dl,
                                                                   "depth_lb": depth_lb, 
                                                                   "depth_db": depth_db, 
                                                                   "team_id": team_id, 
                                                                   "team": team})

# save depth chart changes to the database
@app.post("/depth_chart_defense/{team_id}")
async def save_depth_chart_defense_changes(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):

    # if not check_user_ownership(request, team_id):
        #return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    depth_dl = form.get("dl_order")
    depth_lb = form.get("lb_order")
    depth_db = form.get("db_order")

    save_depth_chart(team_id, "DL", depth_dl)
    save_depth_chart(team_id, "LB", depth_lb)
    save_depth_chart(team_id, "DB", depth_db)

    return RedirectResponse(url=f"/depth_chart_defense/{team_id}", status_code=303)

@app.get("/roster/{team_id}", response_class=HTMLResponse)
async def get_roster(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    # if not check_user_ownership(request, team_id):
        #return RedirectResponse(url="/login", status_code=303)

    team = get_team_by_id(team_id)

    players = get_players_by_team(team_id)

    roster_size = len(players)

    return templates.TemplateResponse("roster.html", {"request": request, 
                                                      "players": players, 
                                                      "team_id": team_id, 
                                                      "team": team})

@app.post("/cut_player/{team_id}")
async def roster_cut_player(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    form = await request.form()
    player_id = form.get("player_id")

    # cut the player from the team
    cut_player(player_id)

    return RedirectResponse(url=f"/roster/{team_id}", status_code=303)

@app.post("/add_to_trade_list/{team_id}")
async def add_player_to_trade_list(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    # if not check_user_ownership(request, team_id):
        #return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    player_id = form.get("player_id")

    # save the player to the trade list
    trade_list_player(player_id)

    return RedirectResponse(url=f"/roster/{team_id}", status_code=303)

@app.post("/remove_from_trade_list/{team_id}")
async def remove_player_from_trade_list(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    # if not check_user_ownership(request, team_id):
        #return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    player_id = form.get("player_id")

    # remove the player from the trade list
    untrade_list_player(player_id)

    return RedirectResponse(url=f"/roster/{team_id}", status_code=303)

@app.get("/standings/{team_id}", response_class=HTMLResponse)
async def get_league_table(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):

    # if not check_user_ownership(request, team_id):
        #return RedirectResponse(url="/login", status_code=303)

    team = get_team_by_id(team_id)

    league_id = get_league_id(team_id)

    league = get_league(league_id)
    standings = get_standings(league_id)

    return templates.TemplateResponse("standings.html", {"request": request, 
                                                         "standings": standings, 
                                                         "league": league, 
                                                         "team_id": team_id, 
                                                         "team": team})

@app.get("/players/{team_id}", response_class=HTMLResponse)
async def get_league_players(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    team = get_team_by_id(team_id)
    league_id = get_league_id(team_id)
    league = get_league(league_id)
    teams = get_teams_by_league_id(league_id)
    teams.remove(team)  # remove the user's team from the list of teams
    players = get_all_players_by_league(league_id)
    players_and_teams = []
    for player in players:
        if player[8] != team_id: # do not include user teams own players
            player_card = [player, get_team_by_id(player[8])]  # player[8] is the team_id
            players_and_teams.append(player_card)
    return templates.TemplateResponse("players.html", {"request": request,
                                                        "players": players_and_teams, 
                                                        "league": league, 
                                                        "team_id": team_id,
                                                        "team": team,
                                                        "teams": teams})

@app.get("/freeagents/{team_id}", response_class=HTMLResponse)
async def get_league_free_agents(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    # if not check_user_ownership(request, team_id):
        #return RedirectResponse(url="/login", status_code=303)

    team = get_team_by_id(team_id)

    league_id = get_team_league_id(team_id)
    free_agents = get_free_agents(league_id)

    return templates.TemplateResponse("free_agents.html", {"request": request, 
                                                           "players": free_agents, 
                                                           "team_id": team_id, 
                                                           "team": team})

# sign a free agent to the team
@app.post("/sign_player/{team_id}")
async def sign_player_to_team(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):

    # if not check_user_ownership(request, team_id):
        #return RedirectResponse(url="/login", status_code=303)
    
    form = await request.form()
    player_id = form.get("player_id")

    # sign the player to the team
    sign_player(player_id, team_id)

    return RedirectResponse(url=f"/freeagents/{team_id}", status_code=303)

@app.get("/home/{user_id}", response_class=HTMLResponse)
async def get_home(request: Request, user_id: int, auth: bool = Depends(get_current_user)):

    # Check if the user is logged in
    #if user_id != get_current_user(request):
     #   return RedirectResponse(url="/login", status_code=303)
    
    user = get_user_by_id(user_id)
    teams = get_teams_by_user_id(user_id)
    leagues = []
    for team in teams:
        league_id = get_league_id(team[0])
        league = get_league(league_id)
        leagues.append(league)

    owned_leagues = get_owned_leagues(user_id)

    user_championships = get_user_championships_won(user_id)
    
    return templates.TemplateResponse("home.html", {"request": request, 
                                                    "teams": teams, 
                                                    "leagues": leagues, 
                                                    "user_id": user_id, 
                                                    "owned_leagues": owned_leagues, 
                                                    "user": user,
                                                    "user_championships": user_championships})

@app.get("/manage_league/{league_id}", response_class=HTMLResponse)
async def get_league_management(request: Request, league_id: int, auth: bool = Depends(require_league_owner)):
    # Check if the user is logged in
    user_id = get_current_user(request)
    
    # Check if the user owns the league
    #if user_id != get_league_owner_id(league_id):
     #   return RedirectResponse(url="/login", status_code=303)

    league = get_league(league_id)
    teams = get_teams_by_league_id(league_id)

    user_id = get_league_owner_id(league_id)

    draft_date = get_draft_date(league_id)
    return templates.TemplateResponse("manage_league.html", {"request": request, 
                                                             "league": league, 
                                                             "league_id": league_id, 
                                                             "user_id": user_id, 
                                                             "teams": teams,
                                                             "draft_date": draft_date})

@app.post("/activate_league/{league_id}")
async def activate_league(request: Request, league_id: int, auth: bool = Depends(require_league_owner)):
    # Check if the user is logged in
    user_id = get_current_user(request)
    
    # Check if the user owns the league
    #if user_id != get_league_owner_id(league_id):
     #   return RedirectResponse(url="/login", status_code=303)

    # Activate the league
    generate_schedule(league_id)
    schedule_draft(league_id)
    create_draft_class(league_id)
    order_depth_charts(league_id)
    make_league_active(league_id)

    return RedirectResponse(url=f"/manage_league/{league_id}", status_code=303)

def get_svg_content(svg_path):
    # Make sure svg_path is a safe path and exists
    if svg_path and svg_path.endswith('.svg') and os.path.exists(svg_path):
        with open(svg_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

@app.get("/team/{team_id}", response_class=HTMLResponse)
async def get_team(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):

    # if not check_user_ownership(request, team_id):
        #return RedirectResponse(url="/login", status_code=303)
    
    team = get_team_by_id(team_id)

    most_recent_game = get_games_by_team_id(team_id)[0] if get_games_by_team_id(team_id) else None
    most_recent_home_team = get_team_by_id(most_recent_game[2]) if most_recent_game else None
    most_recent_away_team = get_team_by_id(most_recent_game[3]) if most_recent_game else None
    game_details = most_recent_game[5] if most_recent_game else None
    if game_details:
        game_details = json_to_game_details(game_details)
    else:
        game_details = None
    most_recent_home_score = game_details["home_score"] if game_details else None
    most_recent_away_score = game_details["away_score"] if game_details else None

    next_fixture = get_next_fixture(team_id)
    next_home_team = get_team_by_id(next_fixture[2]) if next_fixture else None
    next_away_team = get_team_by_id(next_fixture[3]) if next_fixture else None

    star_players = get_star_players(team_id)

    manager_id = get_manager_id(team_id)
    manager = get_user_by_id(manager_id)

    league_id = get_team_league_id(team_id)

    league = get_league(league_id)

    reigning_champion = get_reigning_champion_name(league[0])
    if reigning_champion:
        reigning_champion = ''.join(c for c in str(reigning_champion) if c not in string.punctuation)
    else:
        reigning_champion = reigning_champion

    svg_content = None
    if team[17] and team[17].endswith('.svg'):
        svg_content = get_svg_content(team[17])
    
    trades_proposed = get_trades_proposed(team_id)
    trades_received = get_trades_received(team_id)

    number_of_championships = get_number_of_championships(team_id)
    user_championships = get_user_championships_won(manager_id)
    draft_date = get_draft_date(get_team_league_id(team_id))

    last_season_retirements  = get_last_seasons_retirements(league_id)
    return templates.TemplateResponse("team_home.html", {"request": request, 
                                                         "team_id": team_id, 
                                                         "team": team, 
                                                         "most_recent_game": most_recent_game, 
                                                         "most_recent_home_team": most_recent_home_team, 
                                                         "most_recent_away_team": most_recent_away_team, 
                                                         "most_recent_home_score": most_recent_home_score, 
                                                         "most_recent_away_score": most_recent_away_score, 
                                                         "next_fixture": next_fixture, 
                                                         "next_home_team": next_home_team, 
                                                         "next_away_team": next_away_team, 
                                                         "star_players": star_players, 
                                                         "manager": manager,
                                                         "league": league,
                                                         "reigning_champion": reigning_champion,
                                                         "number_of_championships": number_of_championships,
                                                         "user_championships": user_championships,
                                                         "svg_content": svg_content,
                                                         "draft_date": draft_date,
                                                         "trades_proposed": trades_proposed,
                                                         "trades_received": trades_received,
                                                         "last_season_retirements":last_season_retirements})

@app.post("/delete_trade/{team_id}")
async def delete_trade_endpoint(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    # if not check_user_ownership(request, team_id):
        #return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    trade_id = form.get("trade_id")

    # delete the trade from the database
    delete_trade(trade_id)

    return RedirectResponse(url=f"/team/{team_id}", status_code=303)

@app.post("/make_trade/{team_id}")
async def make_trade(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    # if not check_user_ownership(request, team_id):
        #return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    trade_id = form.get("trade_id")

    # save the trade proposal to the database
    accept_trade(trade_id)

    return RedirectResponse(url=f"/team/{team_id}", status_code=303)
@app.get("/create_team/{user_id}", response_class=HTMLResponse)
async def get_create_team(request: Request, user_id: int, auth: bool = Depends(get_current_user)):
    # Check if the user is logged in
    #if user_id != get_current_user(request):
     #   return RedirectResponse(url="/login", status_code=303)
    
    public_leagues = get_public_leagues()
    
    return templates.TemplateResponse("create_team.html", {"request": request, 
                                                           "user_id": user_id, 
                                                           "public_leagues": public_leagues})

@app.post("/create_team/{user_id}")
async def post_create_team(request: Request, user_id: int, auth: bool = Depends(get_current_user)):
    # Check if the user is logged in
    #if user_id != get_current_user(request):
     #   return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    team_name = form.get("team_name")
    league_id = form.get("league_id")
    primary_color = form.get("team_primary_color")
    secondary_color = form.get("team_secondary_color")
    badge_option: str = form.get("badge_option")
    badge_upload = form.get("team_logo")
    badge_generated = form.get("badge_svg_data")

    print(f"Badge option: {badge_option}")

    if badge_option == "url" and badge_upload :
        badge_path = badge_upload
    elif badge_option == "default" and badge_generated:
        # save svg to a file
        svg_filename = f"static/badges/{team_name.replace(' ', '_')}_badge.svg"
        with open(svg_filename, "w", encoding="utf-8") as svg_file:
            svg_file.write(badge_generated)
        badge_path = svg_filename
    else:
        badge_path = "static/badges/default_badge.svg"  # Default badge if none is provided
    # Create a new team in the database
    team_id = create_new_team(user_id, team_name, league_id, primary_color, secondary_color, badge_path)
    # Redirect to the home page
    return RedirectResponse(url=f"/home/{user_id}", status_code=303)

@app.get("/create_new_league/{user_id}", response_class=HTMLResponse)
async def get_create_new_league(request: Request, user_id: int, auth: bool = Depends(get_current_user)):
    # Check if the user is logged in
    #if user_id != get_current_user(request):
     #   return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse("create_new_league.html", {"request": request, 
                                                                 "user_id": user_id})

@app.post("/create_new_league/{user_id}")
async def post_create_new_league(request: Request, user_id: int, auth: bool = Depends(get_current_user)):
    # Check if the user is logged in
    #if user_id != get_current_user(request):
     #   return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    league_name = form.get("league_name")
    league_year = form.get("league_year")
    is_public = True if form.get("is_public") == "on" else False
    # Create a new league in the database
    save_new_league(league_name, league_year, is_public, user_id) 
    # will set the league to inactive until the admin activates it.
    return RedirectResponse(url=f"/home/{user_id}", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.get("/game_details/{game_id}", response_class=HTMLResponse)
async def game_details(request: Request, game_id: int):

    # this endpoint does not need to check for user ownership, as it is only used to view the game details.
    # this will allow users to share a link of a game with friends, who are not logged in.
    game_record = get_game_by_id(game_id)
    game_details = game_record[5]
    game_details = json_to_game_details(game_details)

    GameDetails = game_details

    homeScore = GameDetails["home_score"]
    awayScore = GameDetails["away_score"]

    passingStats: dict = GameDetails["passing_stats"]
    rushingStats = GameDetails["rushing_stats"]
    receivingStats = GameDetails["receiving_stats"]

    report = GameDetails["report"]

    home_team_id = game_record[2]
    away_team_id = game_record[3]

    home_team = get_team_by_id(home_team_id)
    away_team = get_team_by_id(away_team_id)

    # if the home team is owned by the current user, then they are the home team.
    if get_team_owner_id(home_team_id) == get_current_user(request):
        team_id = home_team_id
    else:
        team_id = away_team_id

    
    return templates.TemplateResponse("match_report.html", {"request": request, 
                                                            "report": report,
                                                            "game_id":game_id,
                                                            "team_id": team_id, # this is a bit of a workaround, as is the team object passed through, fix this later.
                                                            "team":home_team,
                                                            "home_team": home_team, 
                                                            "away_team": away_team,
                                                            "homeScore": homeScore,
                                                            "awayScore": awayScore,
                                                            "passingStats": passingStats,
                                                            "rushingStats": rushingStats,
                                                            "receivingStats": receivingStats,
                                                            })

@app.get("/results/{team_id}", response_class=HTMLResponse)
async def get_results(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    # if not check_user_ownership(request, team_id):
        #return RedirectResponse(url="/login", status_code=303)
    
    team = get_team_by_id(team_id)

    results = get_games_by_team_id(team_id)
    # display the results latest first
    results = sorted(results, key=lambda x: x[4], reverse=True)

    list_game_headers = []

    # get the home score and away score for each game
    for game in results:
        game_id = game[0]
        game_record = get_game_by_id(game_id)
        game_details = game_record[5]
        game_details = json_to_game_details(game_details)
        
        home_team_id = game_record[2] # index 1
        away_team_id = game_record[3] # index 2

        home_team_name = get_team_by_id(home_team_id)[1] # index 3
        away_team_name = get_team_by_id(away_team_id)[1] # index 4
        homeScore = game_details["home_score"] # index 5
        awayScore = game_details["away_score"] # index 6
        game_date = game_record[4] # index 7
        game_date = game_date.strftime("%Y-%m-%d %H:%M:%S")
        game_date = datetime.datetime.strptime(game_date, "%Y-%m-%d %H:%M:%S")

        game_headers = [game_id, home_team_id, away_team_id, home_team_name, away_team_name,
                        homeScore, awayScore, game_date]
        list_game_headers.append(game_headers)

    return templates.TemplateResponse("results.html", {"request": request, 
                                                       "results": results, 
                                                       "game_headers": list_game_headers, 
                                                       "team_id": team_id, 
                                                       "team": team})

@app.get("/draft/{team_id}", response_class=HTMLResponse)
async def get_draft(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    # if not check_user_ownership(request, team_id):
        #return RedirectResponse(url="/login", status_code=303)

    team = get_team_by_id(team_id)

    league_id = get_team_league_id(team_id)
    league = get_league(league_id)
    league_year = get_league_year(league_id)

    # get the draft order for the league
    draft_order = get_reverse_standings(league_id)

    # get the draft class for the team
    draft_class = get_draft_class(league_id, league_year)

    players_drafted = get_players_drafted(league_id, league_year)

    draft_active = check_draft_active(league_id, league_year)

    if draft_active:
        time_on_clock: datetime.timedelta = get_time_on_clock(league_id, league_year)
        # convert the time on clock to a string
        time_on_clock = int(time_on_clock.total_seconds())
    else:
        time_on_clock = None

    # get the team that is currently picking
    if draft_active:
        picking_team_id = get_picking_team_id(league_id, league_year)
        if picking_team_id:
            team_obj = get_team_by_id(picking_team_id)
            if team_obj:
                picking_team_name = team_obj[1]
            else:
                picking_team_name = None
        else:
            picking_team_name = None
    else:
        picking_team_id = None
        picking_team_name = None
    
    draft_date = get_draft_date(league_id)
    return templates.TemplateResponse("draft.html", {"request": request, 
                                                     "draft_class": draft_class, 
                                                     "team_id": team_id, 
                                                     "team": team, 
                                                     "league": league, 
                                                     "draft_order": draft_order, 
                                                     "league_year": league_year, 
                                                     "players_drafted": players_drafted, 
                                                     "draft_active": draft_active, 
                                                     "picking_team_id": picking_team_id, 
                                                     "picking_team_name": picking_team_name, 
                                                     "time_on_clock": time_on_clock,
                                                     "draft_date": draft_date})

# this is an endpoint purely for development purposes, it will be removed from the final version
@app.post("/start_draft/{team_id}")
async def start_draft(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    # if not check_user_ownership(request, team_id):
        #return RedirectResponse(url="/login", status_code=303)

    league_id = get_league_id(team_id)
    draft_year = get_league_year(league_id)

    # start the draft
    add_draft(league_id, draft_year)

    # Notify all clients to reload
    await manager.broadcast("reload")

    return RedirectResponse(url=f"/draft/{team_id}", status_code=303)

def start_draft_no_link(league_id: int):
    draft_year = get_league_year(league_id)
    # start the draft
    add_draft(league_id, draft_year)
    # Notify all clients to reload
    manager.broadcast("reload")

@app.post("/make_draft_pick/{team_id}/{player_id}")
async def draft_player(request: Request, team_id: int, player_id: int, auth: bool = Depends(require_team_owner)):
    # if not check_user_ownership(request, team_id):
        #return RedirectResponse(url="/login", status_code=303)

    league_id = get_league_id(team_id)
    draft_year = get_league_year(league_id)

    # make the draft pick
    make_draft_pick(league_id, draft_year, player_id)

    # Notify all clients to reload
    await manager.broadcast("reload")

    # if the draft is over, start a new season
    if check_draft_active(league_id, draft_year) == False:
        # start a new season
        delete_draft(league_id, draft_year) # delete the draft from the database.
        start_new_season_no_link(league_id)

@app.get("/trade/{team_id}", response_class=HTMLResponse)
async def get_trade(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    # if not check_user_ownership(request, team_id):
        #return RedirectResponse(url="/login", status_code=303)

    team = get_team_by_id(team_id)

    league_id = get_team_league_id(team_id)
    league = get_league(league_id)

    # get all teams in the league
    teams = get_teams_by_league_id(league_id)

    user_players = get_players_by_team(team_id)
    user_players = sorted(user_players, key=lambda x: x[6], reverse=True)  # sort by skill
    other_teams = get_teams_by_league_id(league_id)
    other_teams.remove(team)  # remove the user's team from the list of other teams

    requested_players = get_all_players_by_league(league_id)
    requested_players = sorted(
    [player for player in requested_players if player[8] != team_id],
    key=lambda x: x[6],
    reverse=True) # sort by skill, excluding the user's own players

    return templates.TemplateResponse("trade.html", {"request": request, 
                                                     "team": team, 
                                                     "league": league, 
                                                     "teams": teams, 
                                                     "team_id": team_id,
                                                     "user_players": user_players,
                                                     "other_teams": other_teams,
                                                     "requested_players": requested_players})

@app.post("/submit_trade/{team_id}")
async def submit_trade(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    # if not check_user_ownership(request, team_id):
        #return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    proposing_team_id = team_id  # the team that is proposing the trade
    receiving_team_id = int(form.get("other_team_id")) # the team that is receiving the trade
    players_offered = form.get("offered_players")
    players_requested = form.get("requested_players")

    # submit the trade
    save_trade(proposing_team_id, receiving_team_id, players_offered, players_requested)

    # Show a success message after submitting the trade
    team = get_team_by_id(team_id)
    league_id = get_team_league_id(team_id)
    league = get_league(league_id)
    teams = get_teams_by_league_id(league_id)
    user_players = get_players_by_team(team_id)
    user_players = sorted(user_players, key=lambda x: x[6], reverse=True)
    other_teams = get_teams_by_league_id(league_id)
    other_teams.remove(team)
    requested_players = get_all_players_by_league(league_id)
    requested_players = sorted(
        [player for player in requested_players if player[8] != team_id],
        key=lambda x: x[6],
        reverse=True
    )
    return templates.TemplateResponse(
        "trade.html",
        {
            "request": request,
            "team": team,
            "league": league,
            "teams": teams,
            "team_id": team_id,
            "user_players": user_players,
            "other_teams": other_teams,
            "requested_players": requested_players,
            "trade_success": True  # Pass a flag to show the message
        }
    )

# pick best available player if the pick clock expires.
@app.get("/fixtures/{team_id}", response_class=HTMLResponse)
async def load_fixtures(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    # if not check_user_ownership(request, team_id):
        #return RedirectResponse(url="/login", status_code=303)

    team = get_team_by_id(team_id)

    league_id = get_team_league_id(team_id)
    league = get_league(league_id)

    fixtures = get_fixtures(team_id)
    fixtureInfo = []
    for fixture in fixtures:
        home_team_name = get_team_by_id(fixture[2])
        away_team_name = get_team_by_id(fixture[3])
        date = fixture[4]
        fixtureInfo.append([home_team_name[1], away_team_name[1], date])
    
    draft_date = get_draft_date(league_id)

    return templates.TemplateResponse("fixtures.html", {"request": request, 
                                                        "fixtures": fixtureInfo, 
                                                        "team_id": team_id, 
                                                        "team": team, 
                                                        "league": league,
                                                        "draft_date": draft_date})

### ADMIN PAGES ###

@app.get("/admin", response_class=HTMLResponse)
async def get_admin(request: Request, auth: bool = Depends(require_admin)):
    # add authentification for admin users here, do this later.
    # for now, just return the admin page
    

    # get all leagues from the database
    leagues = get_all_leagues()
    # get all teams from the database
    teams = get_all_teams()
    return templates.TemplateResponse("admin.html", {"request": request, 
                                                     "leagues": leagues, 
                                                     "teams": teams})

# ages a league by by one year and updates their skill accordingly
# this is one step in the process of initializing a new league season
@app.get("/age_league_players/{league_id}", response_class=HTMLResponse)
async def age_league(request: Request, league_id: int, auth: bool = Depends(require_admin)):
    age_league_players(league_id)
    return RedirectResponse(url="/admin", status_code=303)

# this is one step in the process of initializing a new league season
@app.get("/create_draft_class/{league_id}")
async def add_draft_class(request: Request, league_id: int, auth: bool = Depends(require_admin)):
    create_draft_class(league_id)
    return RedirectResponse(url="/admin", status_code=303)

# this is also one step in the process of initializing a new league season
@app.get("/generate_schedule/{league_id}")
async def generate_league_schedule(request: Request, league_id: int, auth: bool = Depends(require_admin)):
    generate_schedule(league_id)
    return RedirectResponse(url="/admin", status_code=303)

# you should do the draft before, as this will make a new draft class.
@app.get("/new_season/{league_id}")
async def start_new_season(request: Request, league_id: int, auth: bool = Depends(require_admin)):
    # this is the process of initializing a new league season
    # 1. increase the league year and season number by 1
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

    return RedirectResponse(url="/admin", status_code=303)

# this is also one step in the process of initializing a new league season
@app.get("/wipe_league_records/{league_id}")
async def wipe_the_league_records(request: Request, league_id: int, auth: bool = Depends(require_admin)):
    # wipe the league records

    wipe_league_records(league_id)

    return RedirectResponse(url="/admin", status_code=303)

# simulates a game between two teams, applies the results to the teams, and saves the game to the database.
@app.get("/match_report/{home_team_id}/{away_team_id}")
async def match_report(request:Request, home_team_id: int, away_team_id: int, auth: bool = Depends(require_admin)):
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

    return RedirectResponse(url="/admin", status_code=303)

@app.post("/create_league")
async def create_new_league(request: Request, auth: bool = Depends(require_admin)):
    form = await request.form()
    league_name = form.get("league_name")
    league_year = form.get("league_year")
    is_public = 1 if form.get("is_public") == "on" else 0  # 1 for True, 0 for False

    # create a new league in the database
    create_league(league_name, league_year, is_public)

    return RedirectResponse(url="/admin", status_code=303)

# use this to trigger the start of a new league after teams have been added to a new league setup.
@app.post("/start_new_league")
async def start_new_league(request: Request, auth: bool = Depends(require_admin)):
    form = await request.form()
    league_id = form.get("league_id")
    generate_schedule(league_id)
    schedule_draft(league_id)
    create_draft_class(league_id)
    order_depth_charts(league_id)
    make_league_active(league_id)
    return RedirectResponse(url="/admin", status_code=303)

### END OF ADMIN PAGES ###

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

# Only start the scheduler in the main process (not in the reload watcher)
# this is to guard against multiple schedulers loading
if __name__ == "__main__" or os.environ.get("RUN_MAIN") == "true":
    scheduler = BackgroundScheduler()
    trigger = CronTrigger(hour=12, minute=00) # simulate games every day at midday
    scheduler.add_job(simulate_todays_fixtures, trigger, misfire_grace_time=3600)
    # add a job to check the draft clock every 10 seconds
    scheduler.add_job(auto_draft_pick, 'interval', seconds=10)
    print("Scheduler started")
    scheduler.start()

if __name__ == "__main__":
    uvicorn.run("server:app", host=SERVER_HOST, port=8080, reload=True)