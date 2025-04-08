import json
from pprint import pprint

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

from app import ai, dao
from logger import logger


router = APIRouter(prefix='/api', tags=['backend'])
llm = ai.GeminiLLM()

class SubmitDrawing(BaseModel):
    image: str
    item_name: str
    language: str = 'EN'


@router.post("/submit-drawing")
async def submit_drawing(data: SubmitDrawing):
    logger.info(f"/submit-drawing item_name = {data.item_name}, size = {round(len(data.image) * 3 // 4 / 1024, 2)}kb")
    result = {"message": '', "passed": False, "error": None}

    # prepare request to llm-provider
    prompt = open('prompt.txt', 'r', encoding='utf-8').read().format(item_name=data.item_name, language=data.language)
    user_msg = ai.user_message(prompt=prompt, encoded_image=data.image)

    try:
        while True:
            llm_response: str = await llm.parse_answer(conversation=[user_msg])
            passed = ai.has_user_passed_task(llm_response=llm_response)
            if passed is None:
                print(f'fail {llm_response = }')
                continue
            break

        result['message'] = llm_response
        result['passed'] = passed
        status_code = 200

    except Exception as e:
        result['error'] = str(e)
        status_code = 500

    logger.info(f"/submit-drawing {result = }")
    return JSONResponse(result, status_code=status_code)


