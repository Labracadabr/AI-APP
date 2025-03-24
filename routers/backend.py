import json
from pprint import pprint

from fastapi import APIRouter, Form, File, UploadFile, Cookie, Response, Header
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

from config import config
from app import ai


router = APIRouter(prefix='/api', tags=['backend'])


class SubmitDrawing(BaseModel):
    image: str
    item_name: str


@router.post("/submit-drawing")
async def submit_drawing(data: SubmitDrawing):
    prompt = config.prompt.format(item_name=data.item_name)
    user_msg = ai.user_message(prompt=prompt, encoded_image=data.image)
    try:
        r: dict = await ai.send_chat_request(conversation=[user_msg])
        return r
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

