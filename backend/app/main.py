import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

_DEFAULT_ORIGINS = "http://localhost:5173,http://localhost:3000"
_allowed_origins = [
    o for o in (o.strip() for o in os.getenv("ALLOWED_ORIGINS", _DEFAULT_ORIGINS).split(",")) if o
]
_allow_credentials = "*" not in _allowed_origins

app = FastAPI(title="Interactive Story API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
