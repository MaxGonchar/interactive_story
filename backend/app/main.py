import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.api.routers import scenes, stories, choice_driven
from app.exceptions import DomainError, LLMError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

load_dotenv()

_testing_enabled = os.getenv("TESTING", "").strip().lower() in {"1", "true", "yes", "on"}

if not _testing_enabled and not os.getenv("VENICE_API_KEY"):
    raise RuntimeError(
        "VENICE_API_KEY environment variable is required but not set. "
        "Copy backend/.env.example to backend/.env and supply a valid key."
    )

_DEFAULT_ORIGINS = "http://localhost:5173,http://localhost:3000"
_parsed_origins = [
    o for o in (o.strip() for o in os.getenv("ALLOWED_ORIGINS", _DEFAULT_ORIGINS).split(",")) if o
]
_allowed_origins = ["*"] if "*" in _parsed_origins else _parsed_origins
_allow_credentials = _allowed_origins != ["*"]

app = FastAPI(title="Interactive Story API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stories.router, prefix="/api")
app.include_router(scenes.router, prefix="/api")
app.include_router(choice_driven.router, prefix="/api")


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    logging.getLogger("app").warning(
        "Domain error %s: %s %s", exc.error_code, request.method, request.url
    )
    return JSONResponse(
        status_code=exc.http_status,
        content={"error": {"code": exc.error_code, "message": exc.message}},
    )


@app.exception_handler(LLMError)
async def llm_error_handler(request: Request, exc: LLMError) -> JSONResponse:
    logging.getLogger("app").exception("LLM error: %s %s", request.method, request.url)
    return JSONResponse(
        status_code=502,
        content={"error": {"code": "llm_error", "message": "LLM request failed"}},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "http_error", "message": str(exc.detail)}},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.getLogger("app").exception(
        "Unhandled exception: %s %s", request.method, request.url
    )
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "An unexpected error occurred"}},
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}
