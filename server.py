from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()

# Set up Jinja2 templates directory
templates = Jinja2Templates(directory="templates")

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/depth_chart_offense", response_class=HTMLResponse)
async def get_depth_chart(request: Request):
    return templates.TemplateResponse("depth_chart_offense.html", {"request": request})

@app.get("/depth_chart_defense", response_class=HTMLResponse)
async def get_depth_chart_defense(request: Request):
    return templates.TemplateResponse("depth_chart_defense.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8080, reload=True)