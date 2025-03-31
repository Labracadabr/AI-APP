import json
from pprint import pprint

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

from config import config
from app import ai, dao


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
        content = r.get('choices')[0]['message']['content']
        result = {
            "message": content,  # todo text formatting
            "passed": True,  # todo determine passed or not based on llm response
            "error": None,
        }
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

