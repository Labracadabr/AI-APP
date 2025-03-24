from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

from routers import frontend, backend, static


app = FastAPI()

# request rate global limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# include routers
app.include_router(frontend.router)
app.include_router(backend.router)
app.include_router(static.router)
app.mount('/static', StaticFiles(directory='static'), name='static')


if __name__ == "__main__":
    pass
    # uvicorn main:app --host 127.0.0.1 --port 8000 --reload
