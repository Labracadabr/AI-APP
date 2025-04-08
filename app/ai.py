import asyncio
import requests
import httpx
import random

from app.utils import save_json, encode_image
from config import config

session = requests.Session()


class LlamaVisionLLM:
    """Class for handling Groq LLM requests."""

    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
    API_KEY = config.GROQ_API_KEY
    model = "llama-3.2-90b-vision-preview"

    def _prepare_request(self, conversation: list, ):
        headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {"messages": conversation, "model": self.model}
        save_json(payload, "./llm_last_request.json")
        return self.BASE_URL, headers, payload

    async def send_chat_request(self, conversation: list) -> dict:
        url, headers, payload = self._prepare_request(conversation)
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                r = await client.post(url, headers=headers, json=payload)
                response_dict = r.json()
                response_dict['status_code'] = r.status_code
            except Exception as e:
                return {"error": str(e), "status_code": r.status_code if 'r' in locals() else 500}
        save_json(response_dict, "./llm_last_response.json")
        return response_dict

    async def parse_answer(self, conversation: list) -> str:
        response = await self.send_chat_request(conversation)
        return response.get("choices", [{}])[0].get("message", {}).get("content", "Error: no response")


class GeminiLLM:
    """Class for handling Google Gemini API requests."""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    API_KEY = config.GEMINI_API_KEY
    models = [
        'gemini-1.5-flash-8b',
        'gemini-1.5-flash',
        'gemini-2.0-flash-lite',
        'gemini-2.0-flash',
    ]

    def _prepare_request(self, conversation: list):
        """Formats request for Gemini API."""
        messages = []
        for msg in conversation:
            parts = []
            if isinstance(msg["content"], str):
                parts.append({"text": msg["content"]})
            elif isinstance(msg["content"], list):
                for item in msg["content"]:
                    if "text" in item:
                        parts.append({"text": item["text"]})
                    elif "image_url" in item:
                        parts.append({
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": item["image_url"]["url"].split(",")[-1]
                            }
                        })
            messages.append({"parts": parts})

        payload = {"contents": messages}
        headers = {"Content-Type": "application/json"}
        save_json(payload, "./llm_last_request.json")
        return f"{self.BASE_URL}?key={self.API_KEY}", headers, payload

    async def send_chat_request(self, conversation: list) -> dict:
        url, headers, payload = self._prepare_request(conversation)

        # pick random model for even distribution of api usage
        model = random.choice(self.models)
        print(f'{model = }')
        url = url.format(model=model)

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                r = await client.post(url, headers=headers, json=payload)
                response_dict = r.json()
                response_dict['status_code'] = r.status_code
            except Exception as e:
                return {"error": str(e), "status_code": r.status_code if 'r' in locals() else 500}
        save_json(response_dict, "./llm_last_response.json")
        return response_dict

    async def parse_answer(self, conversation: list) -> str:
        response = await self.send_chat_request(conversation)
        return response.get('candidates', [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Error: no response")


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


# засчитала ли нейросеть прохождение задания
def has_user_passed_task(llm_response: str) -> bool | None:
    llm_response = llm_response.lower().rstrip('.\n ')
    if llm_response.startswith('❌'):
        return False
    elif llm_response.startswith('✅'):
        return True
    else:
        return None


if __name__ == '__main__':
    # example
    async def example():
        file = "doodle_car.png"
        prompt = open('../prompt.txt', 'r', encoding='utf-8').read().format(item_name='car')
        prompt = 'describe picture'
        encoded_img = encode_image(file)
        user_msg = user_message(prompt, encoded_image=encoded_img)
        conv = [user_msg]

        # Groq LLM
        groq_llm = LlamaVisionLLM()
        groq_response = await groq_llm.parse_answer(conv)
        print("Groq Response:", groq_response)

        # Gemini LLM
        gemini_llm = GeminiLLM()
        gemini_response = await gemini_llm.parse_answer(conv)
        print("Gemini Response:", gemini_response)

    asyncio.run(example())
