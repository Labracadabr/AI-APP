from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, FileResponse


router = APIRouter(prefix='', tags=['frontend'])
templates = Jinja2Templates(directory='templates')
title = "App"


# главная страница
@router.get("/", response_class=HTMLResponse)
async def _(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": title})

# рисовалка
@router.get("/draw", response_class=HTMLResponse)
async def _(request: Request):
    return templates.TemplateResponse("draw.html", {"request": request, "title": title})
