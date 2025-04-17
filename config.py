from dataclasses import dataclass
from environs import Env


@dataclass
class Config:
    site: str
    max_drawing_size_kb: int
    crypt_key: str           # ключ шифрования

    # LLM API
    GROQ_API_KEY: str
    GEMINI_API_KEY: str

    # DB
    host: str                # хост
    dbname: str              # имя базы данных
    user: str                # пользователь
    password: str            # пароль
    port: int                # порт


# загрузить конфиг из переменных окружения
env = Env()
env.read_env()
config = Config(
    site=env('site'),
    max_drawing_size_kb=int(env('max_drawing_size_kb')),
    crypt_key=env('crypt_key'),
    GROQ_API_KEY=env('GROQ_API_KEY'),
    GEMINI_API_KEY=env('GEMINI_API_KEY'),
    host=env('host'),
    dbname=env('dbname'),
    user=env('user'),
    password=env('password'),
    port=env.int('port'),

)

