from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

import json
import datetime

from repositories.user_repository import create_user, check_password, get_user_id
from repositories.player_repository import get_depth_chart_by_position, save_depth_chart, get_players_by_team
from repositories.league_repository import get_standings, get_league, get_league_id, get_public_leagues
from repositories.team_repository import get_teams_by_user_id, get_team_by_id, get_team_owner_id, create_new_team, get_team_league_id
from repositories.game_repository import save_game, get_game_by_id

from starlette.middleware.sessions import SessionMiddleware
from config import SECRET_KEY
from config import SERVER_HOST

from simulator import get_match_report, game_details_to_json, json_to_game_details
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

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
        


@app.get("/")
async def login(request: Request):
    return RedirectResponse(url="/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    request.session.clear()  # Clear any existing session data
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def post_login(request: Request):
    request.session.clear()  # Clear any existing session data
    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    # Check if the user exists and the password is correct
    if check_password(username, password):
        request.session["user_id"] = get_user_id(username)
        
        user_id = request.session.get("user_id")
        return RedirectResponse(url=f"/home/{user_id}", status_code=303)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})

@app.get("/create_account", response_class=HTMLResponse)
async def get_create_account(request: Request):
    return templates.TemplateResponse("create_account.html", {"request": request})

@app.post("/create_account")
async def create_account(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    # Check if the user already exists
    create_user(username, password)
    return RedirectResponse(url="/login", status_code=303)

@app.get("/depth_chart_offense/{team_id}", response_class=HTMLResponse)
async def get_depth_chart(request: Request, team_id: int):

    if not check_user_ownership(request, team_id):
        return RedirectResponse(url="/login", status_code=303)

    team = get_team_by_id(team_id)

    depth_qb = get_depth_chart_by_position(team_id, "QB")
    depth_rb = get_depth_chart_by_position(team_id, "RB")
    depth_wr = get_depth_chart_by_position(team_id, "WR")
    depth_ol = get_depth_chart_by_position(team_id, "OL")

    return templates.TemplateResponse("depth_chart_offense.html", {"request": request, "depth_qb": depth_qb, "depth_rb": depth_rb, "depth_wr": depth_wr, "depth_ol": depth_ol, "team_id": team_id, "team": team})

# save depth chart changes to the database
@app.post("/depth_chart_offense/{team_id}")
async def save_depth_chart_offense_changes(request: Request, team_id: int):

    if not check_user_ownership(request, team_id):
        return RedirectResponse(url="/login", status_code=303)
    
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
async def get_depth_chart_defense(request: Request, team_id: int):

    if not check_user_ownership(request, team_id):
        return RedirectResponse(url="/login", status_code=303)

    team = get_team_by_id(team_id)

    depth_dl = get_depth_chart_by_position(team_id, "DL")
    depth_lb = get_depth_chart_by_position(team_id, "LB")
    depth_db = get_depth_chart_by_position(team_id, "DB")
    
    return templates.TemplateResponse("depth_chart_defense.html", {"request": request, "depth_dl": depth_dl, "depth_lb": depth_lb, "depth_db": depth_db, "team_id": team_id, "team": team})

# save depth chart changes to the database
@app.post("/depth_chart_defense/{team_id}")
async def save_depth_chart_defense_changes(request: Request, team_id: int):

    if not check_user_ownership(request, team_id):
        return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    depth_dl = form.get("dl_order")
    depth_lb = form.get("lb_order")
    depth_db = form.get("db_order")

    save_depth_chart(team_id, "DL", depth_dl)
    save_depth_chart(team_id, "LB", depth_lb)
    save_depth_chart(team_id, "DB", depth_db)

    return RedirectResponse(url=f"/depth_chart_defense/{team_id}", status_code=303)

@app.get("/roster/{team_id}", response_class=HTMLResponse)
async def get_roster(request: Request, team_id: int):
    if not check_user_ownership(request, team_id):
        return RedirectResponse(url="/login", status_code=303)

    team = get_team_by_id(team_id)

    players = get_players_by_team(team_id)

    return templates.TemplateResponse("roster.html", {"request": request, "players": players, "team_id": team_id, "team": team})

@app.get("/standings/{team_id}", response_class=HTMLResponse)
async def get_league_table(request: Request, team_id: int):

    if not check_user_ownership(request, team_id):
        return RedirectResponse(url="/login", status_code=303)

    team = get_team_by_id(team_id)

    league_id = get_league_id(team_id)

    league = get_league(league_id)
    standings = get_standings(league_id)

    return templates.TemplateResponse("standings.html", {"request": request, "standings": standings, "league": league, "team_id": team_id, "team": team})

@app.get("/home/{user_id}", response_class=HTMLResponse)
async def get_home(request: Request, user_id: int):

    # Check if the user is logged in
    if user_id != get_current_user(request):
        return RedirectResponse(url="/login", status_code=303)
    
    teams = get_teams_by_user_id(user_id)
    leagues = []
    for team in teams:
        league_id = get_league_id(team[0])
        league = get_league(league_id)
        leagues.append(league)
    
    return templates.TemplateResponse("home.html", {"request": request, "teams": teams, "leagues": leagues, "user_id": user_id})

@app.get("/team/{team_id}", response_class=HTMLResponse)
async def get_team(request: Request, team_id: int):

    if not check_user_ownership(request, team_id):
        return RedirectResponse(url="/login", status_code=303)
    
    team = get_team_by_id(team_id)
    return templates.TemplateResponse("team_home.html", {"request": request, "team_id": team_id, "team": team})

@app.get("/create_team/{user_id}", response_class=HTMLResponse)
async def get_create_team(request: Request, user_id: int):
    # Check if the user is logged in
    if user_id != get_current_user(request):
        return RedirectResponse(url="/login", status_code=303)
    
    public_leagues = get_public_leagues()
    
    return templates.TemplateResponse("create_team.html", {"request": request, "user_id": user_id, "public_leagues": public_leagues})

@app.post("/create_team/{user_id}")
async def post_create_team(request: Request, user_id: int):
    # Check if the user is logged in
    if user_id != get_current_user(request):
        return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    team_name = form.get("team_name")
    league_id = form.get("league_id")

    # Create a new team in the database
    create_new_team(user_id, team_name, league_id)
    
    return RedirectResponse(url=f"/home/{user_id}", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


# this endpoint is used to simulate a game between two teams, the user will be redirected to the game details page after the game is simulated
@app.get("/match_report/{home_team_id}/{away_team_id}")
async def match_report(request:Request, home_team_id: int, away_team_id: int):
    GameDetails = get_match_report(home_team_id, away_team_id)

    # save data to the database
    league_id = get_team_league_id(home_team_id)
    details_json = game_details_to_json(GameDetails)

    game_id = save_game(league_id, home_team_id, away_team_id, details_json)

    game_record = get_game_by_id(game_id)
    game_details = game_record[5]
    game_details = json_to_game_details(game_details)

    # load the game details
    GameDetails = game_details

    homeScore = GameDetails["home_score"]
    awayScore = GameDetails["away_score"]

    passingStats: dict = GameDetails["passing_stats"]
    rushingStats = GameDetails["rushing_stats"]
    receivingStats = GameDetails["receiving_stats"]

    report = GameDetails["report"]

    home_team = get_team_by_id(home_team_id)
    away_team = get_team_by_id(away_team_id)

    return RedirectResponse(url=f"/game_details/{game_id}", status_code=303)

@app.get("/game_details/{game_id}", response_class=HTMLResponse)
async def game_details(request: Request, game_id: int):
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

    home_team_id = game_record[1]
    away_team_id = game_record[2]

    home_team = get_team_by_id(home_team_id)
    away_team = get_team_by_id(away_team_id)

    
    return templates.TemplateResponse("match_report.html", {"request": request, 
                                                            "report": report,
                                                            "game_id":game_id,
                                                            "team_id":home_team_id, # this is a bit of a workaround, as is the team object passed through, fix this later.
                                                            "team":home_team,
                                                            "home_team": home_team, 
                                                            "away_team": away_team,
                                                            "homeScore": homeScore,
                                                            "awayScore": awayScore,
                                                            "passingStats": passingStats,
                                                            "rushingStats": rushingStats,
                                                            "receivingStats": receivingStats,
                                                            })

if __name__ == "__main__":
    uvicorn.run("server:app", host=SERVER_HOST, port=8080, reload=True)