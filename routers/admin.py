from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from repositories.player_repository import age_league_players, create_draft_class, add_passing_stats, add_rushing_stats, add_receiving_stats, reset_season_stats
from repositories.league_repository import get_all_leagues, generate_schedule, new_season, create_league,\
make_league_active, record_new_champion, get_league_year
from repositories.team_repository import get_team_league_id, add_result_to_team, get_all_teams, wipe_league_records,\
order_depth_charts
from repositories.game_repository import save_game, get_game_by_id
from repositories.draft_repository import schedule_draft, add_draft
from simulator import get_match_report, game_details_to_json, json_to_game_details
from dependencies import require_admin
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/admin", response_class=HTMLResponse)
async def get_admin(request: Request, auth: bool = Depends(require_admin)):
    leagues = get_all_leagues()
    teams = get_all_teams()
    return templates.TemplateResponse(request, "admin.html", {"request": request, "leagues": leagues, "teams": teams})

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
    reset_season_stats(league_id)
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
    GameDetails: dict = get_match_report(home_team_id, away_team_id)

    passing_stats: dict = GameDetails.get("passing_stats")
    rushing_stats: dict = GameDetails.get("rushing_stats")
    receiving_stats: dict = GameDetails.get("receiving_stats")

    # get the box score stats for each player, and add them to their player stats profile.
    if passing_stats:
        for player in passing_stats.keys():
            player_id = player.id
            player_stats = passing_stats[player]
            attempts = player_stats.attempts
            completions = player_stats.completions
            yards = player_stats.yards
            td = player_stats.td

            add_passing_stats(player_id, attempts, completions, yards, td)
    
    if rushing_stats:
        for player in rushing_stats.keys():
            player_id = player.id
            player_stats = rushing_stats[player]
            attempts = player_stats.attempts
            yards = player_stats.yards
            td = player_stats.td

            add_rushing_stats(player_id, attempts, yards, td)
    
    if receiving_stats:
        for player in receiving_stats.keys():
            player_id = player.id
            player_stats = receiving_stats[player]
            receptions = player_stats.receptions
            yards = player_stats.yards
            td = player_stats.td

        add_receiving_stats(player_id, receptions, yards, td)





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

@router.post("/start_draft_admin")
async def start_draft_admin(request: Request, auth: bool = Depends(require_admin)):
    form = await request.form()
    league_id = form.get("league_id")
    draft_year = get_league_year(league_id)
    add_draft(league_id, draft_year)
    from server import manager
    await manager.broadcast("reload")
    return RedirectResponse(url="/admin", status_code=303)