import asyncio
import requests
import httpx

from app.utils import save_json, encode_image
from config import config

session = requests.Session()

# параметры запроса
def _prepare_request(conversation: list, model):
    # model endpoint & api key
    url = "https://api.groq.com/openai/v1/chat/completions"
    api_key = config.GROQ_API_KEY

    # request
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    payload = {"messages": conversation, "model": model}

    save_json(payload, f'./llm_last_request.json')
    return url, headers, payload


async def send_chat_request(conversation: list, model="llama-3.2-11b-vision-preview") -> dict:
    # request
    url, headers, payload = _prepare_request(conversation, model)

    # response - 60 sec timeout
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            r = await client.post(url, headers=headers, json=payload)
            print(f'{r.status_code = }')
            response_dict: dict = r.json()
            response_dict['status_code'] = r.status_code
        except Exception as e:
            return {'error': e, 'status_code': r.status_code}

    save_json(response_dict, f'./llm_last_response.json')
    return response_dict


# подготовить сообщение от юзера для LLM
def user_message(prompt: str, encoded_image=None) -> dict:
    # если сообщение с изображением
    if encoded_image:
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
             }
        ]
        msg_dict = {"role": "user", "content": content, }

    # если только текст
    else:
        msg_dict = {"role": "user", "content": prompt, }
    return msg_dict


if __name__ == '__main__':
    # example
    file = r'doodle_car.png'
    prompt = 'what is drawn here'
    user_msg = user_message(prompt=prompt, encoded_image=encode_image(file))
    conv = [user_msg]
    r: dict = asyncio.run(send_chat_request(conversation=conv))
    print(r.get('choices')[0]['message']['content'])
    pass
