import json
from pprint import pprint

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

from app import ai, dao


router = APIRouter(prefix='/api', tags=['backend'])


class SubmitDrawing(BaseModel):
    image: str
    item_name: str


@router.post("/submit-drawing")
async def submit_drawing(data: SubmitDrawing):
    result = {"message": '', "passed": False, "error": None}

    # prepare request to llm-provider
    prompt = open('prompt.txt', 'r', encoding='utf-8').read().format(item_name=data.item_name)
    user_msg = ai.user_message(prompt=prompt, encoded_image=data.image)

    try:
        while True:
            r: dict = await ai.send_chat_request(conversation=[user_msg])
            llm_response = r.get('choices')[0]['message']['content']
            passed = ai.has_user_passed_task(llm_response=llm_response)
            if passed is None:
                print(f'fail {llm_response = }')
                continue
            break

        result['message'] = llm_response
        result['passed'] = passed
        status_code = 200

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
        result['error'] = str(e)
        status_code = 500

    return JSONResponse(result, status_code=status_code)


