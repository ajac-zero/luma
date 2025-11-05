from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

# Import routers
from .routers.files import router as files_router
from .routers.vectors import router as vectors_router
from .routers.chunking import router as chunking_router
from .core.config import settings
# from routers.ai import router as ai_router  #  futuro con Azure OpenAI

# Import config


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="File Manager API",
    description=" DoRa",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # URLs del frontend React
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

# Manejador global de excepciones
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled Exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Error interno del servidor",
            "status_code": 500
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API"""
    return {
        "status": "healthy",
        "message": "File Manager API está funcionando correctamente",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Endpoint raíz con información básica de la API"""
    return {
        "message": "File Manager API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Incluir routers
app.include_router(
    files_router,
    prefix="/api/v1/files",
    tags=["files"]
)

app.include_router(
    vectors_router,
    prefix="/api/v1",
    tags=["vectors"]
)

app.include_router(
    chunking_router,
    prefix="/api/v1",
    tags=["chunking"]
)

# Router para IA
# app.include_router(
#     ai_router,
#     prefix="/api/v1/ai",
#     tags=["ai"]
# )

# Evento de startup
@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando File Manager API...")
    logger.info(f"Conectando a Azure Storage Account: {settings.AZURE_STORAGE_ACCOUNT_NAME}")
    logger.info(f"Conectando a Qdrant: {settings.QDRANT_URL}")
    #  validaciones de conexión a Azure
    

# Evento de shutdown
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Cerrando File Manager API...")
    # Cleanup de recursos si es necesario


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )