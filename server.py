import os
import datetime
import uvicorn

from fastapi import FastAPI, Request, Depends
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routers import accounts, user_actions, user_views, admin
from slowapi import Limiter
from slowapi.util import get_remote_address
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from repositories.league_repository import get_league_id, get_league_year, get_today_fixtures, \
delete_fixture
from repositories.draft_repository import add_draft

from services.game_service import match_report_no_link
from services.draft_service import do_auto_draft_picks

from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from config import SECRET_KEY
from config import SERVER_HOST

from fastapi import WebSocket, WebSocketDisconnect
from typing import List

from dependencies import require_admin

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