from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, FileResponse


router = APIRouter(prefix='', tags=['frontend'])
templates = Jinja2Templates(directory='templates')
title = "App"

# favicon
@router.get("images/favicon.ico")
async def _():
    return FileResponse("images/favicon.ico")

# главная страница
@router.get("/", response_class=HTMLResponse)
async def _(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": title})

# рисовалка
@router.get("/draw", response_class=HTMLResponse)
async def _(request: Request):
    return templates.TemplateResponse("draw.html", {"request": request, "title": title})

# user registration
@router.get("/auth")
def _(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})

