from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from database import get_depth_chart_by_position, save_depth_chart, get_standings, get_league_id, get_league
from fastapi import Form
from config import SERVER_HOST

app = FastAPI()

# Set up Jinja2 templates directory
templates = Jinja2Templates(directory="templates")

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# for testing purposes
team_id = 2


@app.get("/depth_chart_offense", response_class=HTMLResponse)
async def get_depth_chart(request: Request):

    depth_qb = get_depth_chart_by_position(team_id, "QB")
    depth_rb = get_depth_chart_by_position(team_id, "RB")
    depth_wr = get_depth_chart_by_position(team_id, "WR")
    depth_ol = get_depth_chart_by_position(team_id, "OL")

    return templates.TemplateResponse("depth_chart_offense.html", {"request": request, "depth_qb": depth_qb, "depth_rb": depth_rb, "depth_wr": depth_wr, "depth_ol": depth_ol})

# save depth chart changes to the database
@app.post("/depth_chart_offense")
async def save_depth_chart_offense_changes(request: Request):
    form = await request.form()
    depth_qb = form.get("qb_order")
    depth_rb = form.get("rb_order")
    depth_wr = form.get("wr_order")
    depth_ol = form.get("ol_order")

    save_depth_chart(team_id, "QB", depth_qb)
    save_depth_chart(team_id, "RB", depth_rb)
    save_depth_chart(team_id, "WR", depth_wr)
    save_depth_chart(team_id, "OL", depth_ol)

    return RedirectResponse(url="/depth_chart_offense", status_code=303)


@app.get("/depth_chart_defense", response_class=HTMLResponse)
async def get_depth_chart_defense(request: Request):

    depth_dl = get_depth_chart_by_position(team_id, "DL")
    depth_lb = get_depth_chart_by_position(team_id, "LB")
    depth_db = get_depth_chart_by_position(team_id, "DB")
    
    return templates.TemplateResponse("depth_chart_defense.html", {"request": request, "depth_dl": depth_dl, "depth_lb": depth_lb, "depth_db": depth_db})

# save depth chart changes to the database
@app.post("/depth_chart_defense")
async def save_depth_chart_defense_changes(request: Request):
    form = await request.form()
    depth_dl = form.get("dl_order")
    depth_lb = form.get("lb_order")
    depth_db = form.get("db_order")

    save_depth_chart(team_id, "DL", depth_dl)
    save_depth_chart(team_id, "LB", depth_lb)
    save_depth_chart(team_id, "DB", depth_db)

    return RedirectResponse(url="/depth_chart_defense", status_code=303)


@app.get("/standings", response_class=HTMLResponse)
async def get_league_table(request: Request):

    league_id = get_league_id(team_id)

    league = get_league(league_id)
    standings = get_standings(league_id)

    return templates.TemplateResponse("standings.html", {"request": request, "standings": standings, "league": league})

@app.get("/home", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("server:app", host=SERVER_HOST, port=8080, reload=True)