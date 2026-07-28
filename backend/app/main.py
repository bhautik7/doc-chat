import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api import auth, documents, chat
from app.utils.exceptions import AppError
from app.utils.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Doc Chat API", version="0.1.0")


app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning(
        "%s on %s %s: %s",
        type(exc).__name__,
        request.method,
        request.url.path,
        exc.message,
        exc_info=exc.__cause__ is not None,
    )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception("Database error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=503, content={"detail": "Database is currently unavailable"})


@app.get("/health")
def health_check():
    return {"status": "ok"}
