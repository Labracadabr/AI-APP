from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import frontend, backend, static


app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')

app.include_router(frontend.router)
app.include_router(backend.router)
app.include_router(static.router)


if __name__ == "__main__":
    pass
    # uvicorn main:app --host 127.0.0.1 --port 8000 --reload
