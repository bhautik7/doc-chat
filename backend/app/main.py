from fastapi import FastAPI
from app.api import auth, documents, chat
from fastapi.middleware.cors import CORSMiddleware
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
@app.get("/health")
def health_check():
    return {"status":"ok"}