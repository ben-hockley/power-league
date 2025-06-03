from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from dependencies import get_current_user, require_team_owner, require_league_owner
from fastapi import HTTPException

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

router = APIRouter()

@router.post("/delete_team/{team_id}")
async def delete_user_team(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    delete_team(team_id)
    user_id = get_current_user(request)
    return RedirectResponse(url=f"/home/{user_id}", status_code=303)

@router.post("/depth_chart_offense/{team_id}")
async def save_depth_chart_offense_changes(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
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

@router.post("/sort_depth_chart_offense/{team_id}")
async def sort_depth_chart_offense(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    order_depth_charts_offense_by_team(team_id)
    return RedirectResponse(url=f"/depth_chart_offense/{team_id}", status_code=303)

@router.post("/depth_chart_defense/{team_id}")
async def save_depth_chart_defense_changes(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    form = await request.form()
    depth_dl = form.get("dl_order")
    depth_lb = form.get("lb_order")
    depth_db = form.get("db_order")
    save_depth_chart(team_id, "DL", depth_dl)
    save_depth_chart(team_id, "LB", depth_lb)
    save_depth_chart(team_id, "DB", depth_db)
    return RedirectResponse(url=f"/depth_chart_defense/{team_id}", status_code=303)

@router.post("/sort_depth_chart_defense/{team_id}")
async def sort_depth_chart_defense(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    order_depth_charts_defense_by_team(team_id)
    return RedirectResponse(url=f"/depth_chart_defense/{team_id}", status_code=303)

@router.post("/cut_player/{team_id}")
async def roster_cut_player(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    form = await request.form()
    player_id = form.get("player_id")
    cut_player(player_id)
    return RedirectResponse(url=f"/roster/{team_id}", status_code=303)

@router.post("/add_to_trade_list/{team_id}")
async def add_player_to_trade_list(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    form = await request.form()
    player_id = form.get("player_id")
    trade_list_player(player_id)
    return RedirectResponse(url=f"/roster/{team_id}", status_code=303)

@router.post("/remove_from_trade_list/{team_id}")
async def remove_player_from_trade_list(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    form = await request.form()
    player_id = form.get("player_id")
    untrade_list_player(player_id)
    return RedirectResponse(url=f"/roster/{team_id}", status_code=303)

@router.post("/sign_player/{team_id}")
async def sign_player_to_team(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    form = await request.form()
    player_id = form.get("player_id")
    sign_player(player_id, team_id)
    return RedirectResponse(url=f"/freeagents/{team_id}", status_code=303)

@router.post("/delete_trade/{team_id}")
async def delete_trade_endpoint(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    form = await request.form()
    trade_id = form.get("trade_id")
    delete_trade(trade_id)
    return RedirectResponse(url=f"/team/{team_id}", status_code=303)

@router.post("/make_trade/{team_id}")
async def make_trade(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    form = await request.form()
    trade_id = form.get("trade_id")
    accept_trade(trade_id)
    return RedirectResponse(url=f"/team/{team_id}", status_code=303)

@router.post("/create_team/{user_id}")
async def post_create_team(request: Request, user_id: int, auth: bool = Depends(get_current_user)):
    form = await request.form()
    team_name = form.get("team_name")
    primary_color = form.get("team_primary_color")
    secondary_color = form.get("team_secondary_color")
    badge_option: str = form.get("badge_option")
    badge_upload = form.get("team_logo")
    badge_generated = form.get("badge_svg_data")
    private_league = form.get("join_private_league") == "on"
    if private_league:
        league_code = form.get("private_league_code")
        if not get_league_by_code(league_code):
            raise HTTPException(status_code=400, detail="Invalid league code")
        league_id = get_league_by_code(league_code)[0]
    else:
        league_id = form.get("league_id")
    if badge_option == "url" and badge_upload:
        badge_path = badge_upload
    elif badge_option == "default" and badge_generated:
        svg_filename = f"static/badges/{team_name.replace(' ', '_')}_badge.svg"
        with open(svg_filename, "w", encoding="utf-8") as svg_file:
            svg_file.write(badge_generated)
        badge_path = svg_filename
    else:
        badge_path = "static/badges/default_badge.svg"
    team_id = create_new_team(user_id, team_name, league_id, primary_color, secondary_color, badge_path)
    return RedirectResponse(url=f"/home/{user_id}", status_code=303)

@router.post("/create_new_league/{user_id}")
async def post_create_new_league(request: Request, user_id: int, auth: bool = Depends(get_current_user)):
    form = await request.form()
    league_name = form.get("league_name")
    league_year = form.get("league_year")
    is_public = True if form.get("is_public") == "on" else False
    save_new_league(league_name, league_year, is_public, user_id)
    return RedirectResponse(url=f"/home/{user_id}", status_code=303)

@router.post("/submit_trade/{team_id}")
async def submit_trade(request: Request, team_id: int, auth: bool = Depends(require_team_owner)):
    form = await request.form()
    proposing_team_id = team_id
    receiving_team_id = int(form.get("other_team_id"))
    players_offered = form.get("offered_players")
    players_requested = form.get("requested_players")
    save_trade(proposing_team_id, receiving_team_id, players_offered, players_requested)
    return RedirectResponse(url=f"/trade/{team_id}", status_code=303)

@router.post("/make_draft_pick/{team_id}/{player_id}")
async def draft_player(request: Request, team_id: int, player_id: int, auth: bool = Depends(require_team_owner)):
    from repositories.league_repository import get_league_id, get_league_year
    from repositories.draft_repository import make_draft_pick, check_draft_active, delete_draft
    from server import start_new_season_no_link, manager
    league_id = get_league_id(team_id)
    draft_year = get_league_year(league_id)
    make_draft_pick(league_id, draft_year, player_id)
    await manager.broadcast("reload")
    if not check_draft_active(league_id, draft_year):
        delete_draft(league_id, draft_year)
        start_new_season_no_link(league_id)
    return RedirectResponse(url=f"/draft/{team_id}", status_code=303)

@router.post("/activate_league/{league_id}")
async def activate_league(request: Request, league_id: int, auth: bool = Depends(require_league_owner)):
    generate_schedule(league_id)
    schedule_draft(league_id)
    create_draft_class(league_id)
    order_depth_charts(league_id)
    make_league_active(league_id)

    return RedirectResponse(url=f"/manage_league/{league_id}", status_code=303)


