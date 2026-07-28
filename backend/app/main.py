from fastapi import FastAPI
from app.api import auth, documents, chat
from fastapi.middleware.cors import CORSMiddleware
from app.utils.config import settings

app = FastAPI(
    title="Doc Chat API",
    version="0.1.0",
    docs_url="/docs" if settings.enable_api_docs else None,
    redoc_url="/redoc" if settings.enable_api_docs else None,
    openapi_url="/openapi.json" if settings.enable_api_docs else None,
)


app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
@app.get("/health")
def health_check():
    return {"status":"ok"}
