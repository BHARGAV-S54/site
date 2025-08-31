from dotenv import load_dotenv
load_dotenv()

# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat  # assuming your router file is named chat.py

app = FastAPI(title="Unified Chatbot Backend")

# CORS setup for WordPress frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your chat router
app.include_router(chat.router)

# Optional health check
@app.get("/health")
def health():
    return {"status": "ok"}
