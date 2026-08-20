# app/main.py
from fastapi import FastAPI
from api.chat import router as chat_router

app = FastAPI(
    title="AI Agent Memory System"
)
app.include_router(
    chat_router
)
@app.get("/")
def root():
    return {
        "message": "AI Agent Memory System is running"
    }