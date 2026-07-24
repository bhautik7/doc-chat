from fastapi import FastAPI
from app.api import auth,documents
app = FastAPI(title="Doc Chat API", version="0.1.0")

app.include_router(auth.router)
app.include_router(documents.router)


@app.get("/health")
def health_check():
    return {"status":"ok"}