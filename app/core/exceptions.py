from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class BusinessException(Exception):
    def __init__(self, code: str, message: str, http_status: int = 422, details: dict = None):
        self.code       = code
        self.message    = message
        self.http_status = http_status
        self.details    = details or {}

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(status_code=404, content={"success": False, "error": {"code": "NOT_FOUND", "message": "Không tìm thấy tài nguyên"}})
