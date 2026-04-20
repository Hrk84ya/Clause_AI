import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.api.analyses import router as analyses_router
from src.api.auth import limiter, router as auth_router
from src.api.documents import router as documents_router
from src.api.health import router as health_router
from src.api.jobs import router as jobs_router
from src.api.queries import router as queries_router
from src.config import settings
from src.middleware.logging import RequestLoggingMiddleware

# Configure structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
        if settings.app_env == "development"
        else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        structlog.get_level_from_name(settings.log_level.lower())
        if hasattr(structlog, "get_level_from_name")
        else 0
    ),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

app = FastAPI(
    title="Legal Document Analyzer API",
    description="AI-Powered Legal Document Analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(queries_router, prefix="/api/v1")
app.include_router(analyses_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return 422 with detailed field errors."""
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": 422,
                "message": "Validation error",
                "details": exc.errors(),
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Return 500 with generic message, log full traceback."""
    logger = structlog.get_logger()
    logger.error("unhandled_exception", exc_info=exc, path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
            }
        },
    )


@app.on_event("startup")
async def startup_event():
    """Validate environment and log startup info."""
    logger = structlog.get_logger()

    # Validate OpenAI API key
    if not settings.openai_api_key or settings.openai_api_key == "sk-...":
        logger.warning("OPENAI_API_KEY is not set or is a placeholder. AI features will not work.")

    # Log startup info
    logger.info(
        "startup",
        app="Legal Document Analyzer API",
        version="1.0.0",
        environment=settings.app_env,
        docs_url="http://localhost:8000/docs",
    )


@app.get("/")
async def root():
    return {"message": "Legal Document Analyzer API", "version": "1.0.0"}
