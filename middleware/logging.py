import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from logger import logger


# log each http request
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # skip logging for certain paths
        if "/static/" in request.url.path:
            return await call_next(request)

        start_time = time.time()
        client_ip = request.client.host if request.client else None
        method = request.method
        path = request.url.path
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"{method} {path}\tfrom: {client_ip}\terror: {type(e).__name__}('{str(e)}')", exc_info=False)
            raise

        # log str
        t = (time.time() - start_time) * 1000
        logger.debug(f"{method} {path}\tfrom: {client_ip}\tStatus: {response.status_code}\tTook: {t:.2f}ms")
        return response
