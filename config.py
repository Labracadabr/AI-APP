from dataclasses import dataclass
from environs import Env


@dataclass
class Config:
    site: str = None
    # LLM API
    GROQ_API_KEY: str = None
    prompt: str = None


# загрузить конфиг из переменных окружения
env = Env()
env.read_env()
config = Config(
    site=env('site'),
    GROQ_API_KEY=env('GROQ_API_KEY'),
    prompt=env('prompt'),

)

