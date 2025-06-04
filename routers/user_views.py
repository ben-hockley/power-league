from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from repositories.user_repository import get_user_by_id
from repositories.player_repository import get_depth_chart_by_position, get_players_by_team, get_draft_class, get_free_agents,\
get_star_players, get_all_players_by_league
from repositories.league_repository import get_standings, get_league, get_league_id,\
get_public_leagues, get_league_year, get_fixtures,\
get_reverse_standings, get_owned_leagues, get_league_owner_id, get_reigning_champion_name, get_number_of_championships, get_user_championships_won, \
get_last_seasons_retirements
from repositories.team_repository import get_teams_by_user_id, get_team_by_id, get_team_owner_id,\
get_team_league_id, get_standings, get_teams_by_league_id, get_manager_id
from repositories.game_repository import get_game_by_id, get_games_by_team_id, get_next_fixture
from repositories.draft_repository import get_players_drafted, check_draft_active, get_picking_team_id, get_time_on_clock, get_draft_date
from repositories.trade_repository import get_trades_proposed, get_trades_received
from dependencies import get_current_user, require_team_owner, require_league_owner
from fastapi.templating import Jinja2Templates
import datetime
import string

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def login(request: Request):
    return RedirectResponse(url="/login", status_code=303)

@router.get("/depth_chart_offense/{team_id}", response_class=HTMLResponse)
async def get_depth_chart(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    team = get_team_by_id(team_id)
    depth_qb = get_depth_chart_by_position(team_id, "QB")
    depth_rb = get_depth_chart_by_position(team_id, "RB")
    depth_wr = get_depth_chart_by_position(team_id, "WR")
    depth_ol = get_depth_chart_by_position(team_id, "OL")
    return templates.TemplateResponse(
        request,
        "depth_chart_offense.html",
        {
            "request": request,
            "depth_qb": depth_qb,
            "depth_rb": depth_rb,
            "depth_wr": depth_wr,
            "depth_ol": depth_ol,
            "team_id": team_id,
            "team": team
        }
    )

@router.get("/depth_chart_defense/{team_id}", response_class=HTMLResponse)
async def get_depth_chart_defense(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    team = get_team_by_id(team_id)
    depth_dl = get_depth_chart_by_position(team_id, "DL")
    depth_lb = get_depth_chart_by_position(team_id, "LB")
    depth_db = get_depth_chart_by_position(team_id, "DB")
    return templates.TemplateResponse(
        request,
        "depth_chart_defense.html",
        {
            "request": request,
            "depth_dl": depth_dl,
            "depth_lb": depth_lb,
            "depth_db": depth_db,
            "team_id": team_id,
            "team": team
        }
    )

@router.get("/roster/{team_id}", response_class=HTMLResponse)
async def get_roster(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    team = get_team_by_id(team_id)
    players = get_players_by_team(team_id)
    roster_size = len(players)
    return templates.TemplateResponse(
        request,
        "roster.html",
        {
            "request": request,
            "players": players,
            "team_id": team_id,
            "team": team
        }
    )

@router.get("/standings/{team_id}", response_class=HTMLResponse)
async def get_league_table(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    team = get_team_by_id(team_id)
    league_id = get_league_id(team_id)
    league = get_league(league_id)
    standings = get_standings(league_id)
    return templates.TemplateResponse(
        request,
        "standings.html",
        {
            "request": request,
            "standings": standings,
            "league": league,
            "team_id": team_id,
            "team": team
        }
    )

@router.get("/players/{team_id}", response_class=HTMLResponse)
async def get_league_players(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    team = get_team_by_id(team_id)
    league_id = get_league_id(team_id)
    league = get_league(league_id)
    teams = get_teams_by_league_id(league_id)
    teams.remove(team)
    players = get_all_players_by_league(league_id)
    players_and_teams = []
    for player in players:
        if player[8] != team_id:
            player_card = [player, get_team_by_id(player[8])]
            players_and_teams.append(player_card)
    return templates.TemplateResponse(
        request,
        "players.html",
        {
            "request": request,
            "players": players_and_teams,
            "league": league,
            "team_id": team_id,
            "team": team,
            "teams": teams
        }
    )

@router.get("/freeagents/{team_id}", response_class=HTMLResponse)
async def get_league_free_agents(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    team = get_team_by_id(team_id)
    league_id = get_team_league_id(team_id)
    free_agents = get_free_agents(league_id)
    return templates.TemplateResponse(
        request,
        "free_agents.html",
        {
            "request": request,
            "players": free_agents,
            "team_id": team_id,
            "team": team
        }
    )

@router.get("/home/{user_id}", response_class=HTMLResponse)
async def get_home(request: Request, user_id: int, auth: bool = Depends(get_current_user)):
    user = get_user_by_id(user_id)
    teams = get_teams_by_user_id(user_id)
    leagues = []
    for team in teams:
        league_id = get_league_id(team[0])
        league = get_league(league_id)
        leagues.append(league)
    owned_leagues = get_owned_leagues(user_id)
    user_championships = get_user_championships_won(user_id)
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "request": request,
            "teams": teams,
            "leagues": leagues,
            "user_id": user_id,
            "owned_leagues": owned_leagues,
            "user": user,
            "user_championships": user_championships
        }
    )

@router.get("/manage_league/{league_id}", response_class=HTMLResponse)
async def get_league_management(request: Request, league_id: int, auth: bool = Depends(require_league_owner)):
    user_id = get_current_user(request)
    league = get_league(league_id)
    teams = get_teams_by_league_id(league_id)
    user_id = get_league_owner_id(league_id)
    draft_date = get_draft_date(league_id)
    return templates.TemplateResponse(
        request,
        "manage_league.html",
        {
            "request": request,
            "league": league,
            "league_id": league_id,
            "user_id": user_id,
            "teams": teams,
            "draft_date": draft_date
        }
    )

@router.get("/team/{team_id}", response_class=HTMLResponse)
async def get_team(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    team = get_team_by_id(team_id)
    most_recent_game = get_games_by_team_id(team_id)[0] if get_games_by_team_id(team_id) else None
    most_recent_home_team = get_team_by_id(most_recent_game[2]) if most_recent_game else None
    most_recent_away_team = get_team_by_id(most_recent_game[3]) if most_recent_game else None
    game_details = most_recent_game[5] if most_recent_game else None
    if game_details:
        from simulator import json_to_game_details
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
    league_admin = get_user_by_id(league[5])
    reigning_champion = get_reigning_champion_name(league[0])
    if reigning_champion:
        reigning_champion = ''.join(c for c in str(reigning_champion) if c not in string.punctuation)
    else:
        reigning_champion = reigning_champion
    svg_content = None
    if team[17] and team[17].endswith('.svg'):
        import os
        if os.path.exists(team[17]):
            with open(team[17], "r", encoding="utf-8") as f:
                svg_content = f.read()
    trades_proposed = get_trades_proposed(team_id)
    trades_received = get_trades_received(team_id)
    number_of_championships = get_number_of_championships(team_id)
    user_championships = get_user_championships_won(manager_id)
    draft_date = get_draft_date(get_team_league_id(team_id))
    last_season_retirements = get_last_seasons_retirements(league_id)
    return templates.TemplateResponse(
        request,
        "team_home.html",
        {
            "request": request,
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
            "league_admin": league_admin,
            "reigning_champion": reigning_champion,
            "number_of_championships": number_of_championships,
            "user_championships": user_championships,
            "svg_content": svg_content,
            "draft_date": draft_date,
            "trades_proposed": trades_proposed,
            "trades_received": trades_received,
            "last_season_retirements": last_season_retirements
        }
    )

@router.get("/create_team/{user_id}", response_class=HTMLResponse)
async def get_create_team(request: Request, user_id: int, auth: bool = Depends(get_current_user)):
    public_leagues = get_public_leagues()
    public_leagues_no_teams = []
    for league in public_leagues:
        no_of_teams = len(get_teams_by_league_id(league[0]))
        public_leagues_no_teams.append((league, no_of_teams))
    return templates.TemplateResponse(
        request,
        "create_team.html",
        {
            "request": request,
            "user_id": user_id,
            "public_leagues": public_leagues_no_teams
        }
    )

@router.get("/create_new_league/{user_id}", response_class=HTMLResponse)
async def get_create_new_league(request: Request, user_id: int, auth: bool = Depends(get_current_user)):
    return templates.TemplateResponse(
        request,
        "create_new_league.html",
        {
            "request": request,
            "user_id": user_id
        }
    )

@router.get("/game_details/{game_id}", response_class=HTMLResponse)
async def game_details(request: Request, game_id: int):
    game_record = get_game_by_id(game_id)
    from simulator import json_to_game_details
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
    if get_team_owner_id(home_team_id) == get_current_user(request):
        team_id = home_team_id
    else:
        team_id = away_team_id
    return templates.TemplateResponse(
        request,
        "match_report.html",
        {
            "request": request,
            "report": report,
            "game_id": game_id,
            "team_id": team_id,
            "team": home_team,
            "home_team": home_team,
            "away_team": away_team,
            "homeScore": homeScore,
            "awayScore": awayScore,
            "passingStats": passingStats,
            "rushingStats": rushingStats,
            "receivingStats": receivingStats,
        }
    )

@router.get("/team_report/{team_id}/{opponent_team_id}", response_class=HTMLResponse)
async def get_team_report(request: Request, team_id: int, opponent_team_id: int, auth: bool = Depends(require_team_owner)):
    team = get_team_by_id(team_id)
    opponent = get_team_by_id(opponent_team_id)
    op_star_players = get_star_players(opponent_team_id)
    op_manager_id = get_manager_id(opponent_team_id)
    op_manager = get_user_by_id(op_manager_id)
    return templates.TemplateResponse(
        request,
        "team_report.html",
        {
            "request": request,
            "team": team,
            "team_id": team_id,
            "opponent": opponent,
            "op_manager": op_manager,
            "op_star_players": op_star_players,
        }
    )

@router.get("/results/{team_id}", response_class=HTMLResponse)
async def get_results(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    team = get_team_by_id(team_id)
    results = get_games_by_team_id(team_id)
    results = sorted(results, key=lambda x: x[4], reverse=True)
    list_game_headers = []
    for game in results:
        game_id = game[0]
        game_record = get_game_by_id(game_id)
        from simulator import json_to_game_details
        game_details = game_record[5]
        game_details = json_to_game_details(game_details)
        home_team_id = game_record[2]
        away_team_id = game_record[3]
        home_team_name = get_team_by_id(home_team_id)[1]
        away_team_name = get_team_by_id(away_team_id)[1]
        homeScore = game_details["home_score"]
        awayScore = game_details["away_score"]
        game_date = game_record[4]
        game_date = game_date.strftime("%Y-%m-%d %H:%M:%S")
        import datetime
        game_date = datetime.datetime.strptime(game_date, "%Y-%m-%d %H:%M:%S")
        game_headers = [game_id, home_team_id, away_team_id, home_team_name, away_team_name,
                        homeScore, awayScore, game_date]
        list_game_headers.append(game_headers)
    return templates.TemplateResponse(
        request,
        "results.html",
        {
            "request": request,
            "results": results,
            "game_headers": list_game_headers,
            "team_id": team_id,
            "team": team
        }
    )

@router.get("/draft/{team_id}", response_class=HTMLResponse)
async def get_draft(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    team = get_team_by_id(team_id)
    league_id = get_team_league_id(team_id)
    league = get_league(league_id)
    league_year = get_league_year(league_id)
    draft_order = get_reverse_standings(league_id)
    draft_class = get_draft_class(league_id, league_year)
    players_drafted = get_players_drafted(league_id, league_year)
    draft_active = check_draft_active(league_id, league_year)
    if draft_active:
        time_on_clock: datetime.timedelta = get_time_on_clock(league_id, league_year)
        time_on_clock = int(time_on_clock.total_seconds())
    else:
        time_on_clock = None
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
    return templates.TemplateResponse(
        request,
        "draft.html",
        {
            "request": request,
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
            "draft_date": draft_date
        }
    )

@router.get("/trade/{team_id}", response_class=HTMLResponse)
async def get_trade(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
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
        request,
        "trade.html",
        {
            "request": request,
            "team": team,
            "league": league,
            "teams": teams,
            "team_id": team_id,
            "user_players": user_players,
            "other_teams": other_teams,
            "requested_players": requested_players
        }
    )

@router.get("/fixtures/{team_id}", response_class=HTMLResponse)
async def load_fixtures(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
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
    return templates.TemplateResponse(
        request,
        "fixtures.html",
        {
            "request": request,
            "fixtures": fixtureInfo,
            "team_id": team_id,
            "team": team,
            "league": league,
            "draft_date": draft_date
        }
    )