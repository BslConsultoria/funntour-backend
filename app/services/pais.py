from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.models.pais import Pais
from app.schemas.pais import CreatePais, UpdatePais
import logging
from typing import List, Optional
import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PaisService:
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Pais]:
        try:
            query = select(Pais).where(Pais.dt_exclusao == None).offset(skip).limit(limit)
            result = await db.execute(query)
            paises = result.scalars().all()
            logger.info(f"Recuperados {len(paises)} países")
            return paises
        except Exception as e:
            logger.error(f"Erro ao recuperar países: {e}")
            raise

    @staticmethod
    async def get_by_id(db: AsyncSession, pais_id: int) -> Optional[Pais]:
        try:
            query = select(Pais).where(Pais.id == pais_id, Pais.dt_exclusao == None)
            result = await db.execute(query)
            pais = result.scalars().first()
            if pais:
                logger.info(f"País recuperado: ID {pais_id}")
            else:
                logger.info(f"País não encontrado: ID {pais_id}")
            return pais
        except Exception as e:
            logger.error(f"Erro ao recuperar país por ID: {e}")
            raise

    @staticmethod
    async def create(db: AsyncSession, pais_data: CreatePais) -> Pais:
        try:
            pais = Pais(descricao=pais_data.descricao, sigla=pais_data.sigla)
            db.add(pais)
            await db.commit()
            await db.refresh(pais)
            logger.info(f"País criado: ID {pais.id}")
            return pais
        except Exception as e:
            await db.rollback()
            logger.error(f"Erro ao criar país: {e}")
            raise

    @staticmethod
    async def update(db: AsyncSession, pais_id: int, pais_data: UpdatePais) -> Optional[Pais]:
        try:
            pais = await PaisService.get_by_id(db, pais_id)
            if not pais:
                logger.info(f"Tentativa de atualizar país não existente: ID {pais_id}")
                return None
            
            # Atualizar apenas os campos que foram enviados
            if pais_data.descricao is not None:
                pais.descricao = pais_data.descricao
            if pais_data.sigla is not None:
                pais.sigla = pais_data.sigla
            
            # Atualizar data de atualização
            pais.dt_atualizacao = datetime.datetime.now()
            
            await db.commit()
            await db.refresh(pais)
            logger.info(f"País atualizado: ID {pais_id}")
            return pais
        except Exception as e:
            await db.rollback()
            logger.error(f"Erro ao atualizar país: {e}")
            raise

    @staticmethod
    async def delete(db: AsyncSession, pais_id: int) -> bool:
        try:
            pais = await PaisService.get_by_id(db, pais_id)
            if not pais:
                logger.info(f"Tentativa de excluir país não existente: ID {pais_id}")
                return False

            # Soft delete - atualizar o campo dt_exclusao
            pais.dt_exclusao = datetime.datetime.now()
            await db.commit()
            logger.info(f"País excluído (soft delete): ID {pais_id}")
            return True
        except Exception as e:
            await db.rollback()
            logger.error(f"Erro ao excluir país: {e}")
            raise
