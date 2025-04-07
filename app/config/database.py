from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do banco de dados
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# URL de conexão com o banco de dados para async (usando aiomysql)
DATABASE_URL = f"mysql+aiomysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    # Criação do engine assíncrono
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        poolclass=NullPool  # Importante para aplicações web
    )
    logger.info("Engine de conexão assíncrona com o banco de dados configurado com sucesso")
except Exception as e:
    logger.error(f"Erro ao configurar engine do banco de dados: {e}")
    raise

# Sessão assíncrona para interagir com o banco de dados
AsyncSessionLocal = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False, 
    autoflush=False
)

# Base para os modelos ORM
Base = declarative_base()

# Função para obter a sessão assíncrona do banco de dados
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
            
# Função para inicializar o banco de dados
async def init_db():
    async with engine.begin() as conn:
        # Apenas para criar as tabelas na primeira inicialização
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Banco de dados inicializado com sucesso")
