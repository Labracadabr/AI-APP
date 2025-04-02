from dataclasses import dataclass
from environs import Env


@dataclass
class Config:
    site: str = None

    # LLM API
    GROQ_API_KEY: str = None
    GEMINI_API_KEY: str = None

    # DB
    host: str = None                # хост
    dbname: str = None              # имя базы данных
    user: str = None                # пользователь
    password: str = None            # пароль
    port: int = None                # порт


# загрузить конфиг из переменных окружения
env = Env()
env.read_env()
config = Config(
    site=env('site'),
    GROQ_API_KEY=env('GROQ_API_KEY'),
    GEMINI_API_KEY=env('GEMINI_API_KEY'),
    host=env('host'),
    dbname=env('dbname'),
    user=env('user'),
    password=env('password'),
    port=env.int('port'),

)

