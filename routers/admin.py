from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
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
from simulator import get_match_report, game_details_to_json, json_to_game_details
from dependencies import require_admin, get_current_user, require_team_owner
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/admin", response_class=HTMLResponse)
async def get_admin(request: Request, auth: bool = Depends(require_admin)):
    leagues = get_all_leagues()
    teams = get_all_teams()
    return templates.TemplateResponse("admin.html", {"request": request, "leagues": leagues, "teams": teams})

@router.get("/age_league_players/{league_id}", response_class=HTMLResponse)
async def age_league(request: Request, league_id: int, auth: bool = Depends(require_admin)):
    age_league_players(league_id)
    return RedirectResponse(url="/admin", status_code=303)

@router.get("/create_draft_class/{league_id}")
async def add_draft_class(request: Request, league_id: int, auth: bool = Depends(require_admin)):
    create_draft_class(league_id)
    return RedirectResponse(url="/admin", status_code=303)

@router.get("/generate_schedule/{league_id}")
async def generate_league_schedule(request: Request, league_id: int, auth: bool = Depends(require_admin)):
    generate_schedule(league_id)
    return RedirectResponse(url="/admin", status_code=303)

@router.get("/new_season/{league_id}")
async def start_new_season(request: Request, league_id: int, auth: bool = Depends(require_admin)):
    record_new_champion(league_id)
    new_season(league_id)
    age_league_players(league_id)
    create_draft_class(league_id)
    wipe_league_records(league_id)
    generate_schedule(league_id)
    schedule_draft(league_id)
    order_depth_charts(league_id)
    return RedirectResponse(url="/admin", status_code=303)

@router.get("/wipe_league_records/{league_id}")
async def wipe_the_league_records(request: Request, league_id: int, auth: bool = Depends(require_admin)):
    wipe_league_records(league_id)
    return RedirectResponse(url="/admin", status_code=303)

@router.get("/match_report/{home_team_id}/{away_team_id}")
async def match_report(request: Request, home_team_id: int, away_team_id: int, auth: bool = Depends(require_admin)):
    GameDetails = get_match_report(home_team_id, away_team_id)
    league_id = get_team_league_id(home_team_id)
    details_json = game_details_to_json(GameDetails)
    game_id = save_game(league_id, home_team_id, away_team_id, details_json)
    game_record = get_game_by_id(game_id)
    game_details = json_to_game_details(game_record[5])
    homeScore = game_details["home_score"]
    awayScore = game_details["away_score"]
    add_result_to_team(home_team_id, homeScore, awayScore)
    add_result_to_team(away_team_id, awayScore, homeScore)
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/create_league")
async def create_new_league(request: Request, auth: bool = Depends(require_admin)):
    form = await request.form()
    league_name = form.get("league_name")
    league_year = form.get("league_year")
    is_public = 1 if form.get("is_public") == "on" else 0
    max_teams = form.get("max_teams")
    league_code = form.get("league_code") if is_public == 0 else None
    create_league(league_name, league_year, is_public, max_teams, league_code)
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/start_new_league")
async def start_new_league(request: Request, auth: bool = Depends(require_admin)):
    form = await request.form()
    league_id = form.get("league_id")
    generate_schedule(league_id)
    schedule_draft(league_id)
    create_draft_class(league_id)
    order_depth_charts(league_id)
    make_league_active(league_id)
    return RedirectResponse(url="/admin", status_code=303)