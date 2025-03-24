from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter(prefix='', tags=['static'])


# favicon
@router.get("images/favicon.ico")
async def _():
    return FileResponse("images/favicon.ico")

# css
@router.get("static/css/base.css")
async def _():
    return FileResponse("css/base.css")
