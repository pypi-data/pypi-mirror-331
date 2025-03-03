from fastapi import Request
from fastapi.responses import JSONResponse

from gamr_backend_api_service.auth.exceptions import (
    TokenNotDecoded,
    UserNotExists,
)
from gamr_backend_api_service.model_services.hugging_face.errors import HuggingFaceException
from gamr_backend_api_service.models.errors import UserBlank


def user_not_exists_exception_handler(request: Request, exc: UserNotExists):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.message})


def user_blank_incorrect_exception_handler(request: Request, exc: UserBlank):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.message})


def token_not_decoded_exception_handler(request: Request, exc: TokenNotDecoded):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.message})


def hugging_face_api_exception_handler(request: Request, exc: HuggingFaceException):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.message})
