from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import asyncio

from app.routes import pais, estado, cidade
from app.config.database import init_db

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar aplicação FastAPI
app = FastAPI(
    title="Funntour API",
    description="API de gerenciamento de dados do sistema Funntour",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Evento de inicialização do aplicativo para configurar o banco de dados
@app.on_event("startup")
async def startup_db_client():
    try:
        logger.info("Inicializando banco de dados...")
        await init_db()
        logger.info("Banco de dados inicializado com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
        raise

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar as origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para logs de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"Método: {request.method} | URL: {request.url.path} | "
        f"Status: {response.status_code} | Tempo: {process_time:.4f}s"
    )
    
    return response

# Tratamento de exceções
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Exceção não tratada: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno no servidor"},
    )

# Incluir rotas
app.include_router(pais.router)
app.include_router(estado.router)
app.include_router(cidade.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
