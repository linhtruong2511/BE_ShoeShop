import uuid, time
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        with logger.contextualize(request_id=request_id):
            response = await call_next(request)
            duration = round((time.time() - start_time) * 1000, 2)
            logger.info(f"{request.method} {request.url.path} {response.status_code} {duration}ms")
        response.headers["X-Request-Id"] = request_id
        return response
