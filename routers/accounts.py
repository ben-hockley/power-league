from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from repositories.user_repository import create_user, check_password, get_user_id, get_user_by_id
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    request.session.clear()
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def post_login(request: Request):
    request.session.clear()
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    if check_password(username, password):
        user = get_user_by_id(get_user_id(username))
        request.session["user_id"] = user[0]
        request.session["role"] = user[4]
        return RedirectResponse(url=f"/home/{user[0]}", status_code=303)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})

@router.get("/create_account", response_class=HTMLResponse)
async def get_create_account(request: Request):
    return templates.TemplateResponse("create_account.html", {"request": request})

@router.post("/create_account")
async def create_account(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    avatar = form.get("avatarUrl")
    create_user(username, password, avatar)
    return RedirectResponse(url="/login", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)