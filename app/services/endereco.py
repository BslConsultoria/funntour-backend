from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.endereco import Endereco
from app.models.cidade import Cidade
from app.models.estado import Estado
import logging

logger = logging.getLogger(__name__)

class EnderecoService:
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Endereco]:
        """
        Retorna todos os endereu00e7os nu00e3o excluu00eddos, incluindo cidade e estado.
        """
        query = select(Endereco).where(Endereco.dt_exclusao.is_(None))
        query = query.options(
            selectinload(Endereco.cidade),
            selectinload(Endereco.estado).selectinload(Estado.pais)
        )
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, endereco_id: int) -> Optional[Endereco]:
        """
        Retorna um endereu00e7o pelo ID se nu00e3o estiver excluu00eddo, incluindo cidade e estado.
        """
        query = select(Endereco).where(
            and_(
                Endereco.id == endereco_id,
                Endereco.dt_exclusao.is_(None)
            )
        )
        query = query.options(
            selectinload(Endereco.cidade),
            selectinload(Endereco.estado).selectinload(Estado.pais)
        )
        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def create(db: AsyncSession, endereco_data: Dict[str, Any]) -> Endereco:
        """
        Cria um novo endereu00e7o.
        """
        # Cria o novo endereu00e7o
        db_endereco = Endereco(**endereco_data)
        db.add(db_endereco)
        await db.commit()
        await db.refresh(db_endereco)
        
        # Retorna o endereu00e7o com relacionamentos
        return await EnderecoService.get_by_id(db, db_endereco.id)

    @staticmethod
    async def update(db: AsyncSession, endereco_id: int, endereco_data: Dict[str, Any]) -> Optional[Endereco]:
        """
        Atualiza um endereu00e7o existente.
        """
        # Verifica se o endereu00e7o existe
        db_endereco = await EnderecoService.get_by_id(db, endereco_id)
        if not db_endereco:
            return None

        # Atualiza o endereu00e7o
        update_stmt = update(Endereco).where(Endereco.id == endereco_id).values(**endereco_data)
        await db.execute(update_stmt)
        await db.commit()
        
        # Retorna o endereu00e7o atualizado com relacionamentos
        return await EnderecoService.get_by_id(db, endereco_id)

    @staticmethod
    async def delete(db: AsyncSession, endereco_id: int) -> bool:
        """
        Exclui logicamente um endereu00e7o.
        """
        db_endereco = await EnderecoService.get_by_id(db, endereco_id)
        if not db_endereco:
            return False

        # Exclusu00e3o lu00f3gica
        update_stmt = update(Endereco).where(Endereco.id == endereco_id).values(dt_exclusao=datetime.now())
        await db.execute(update_stmt)
        await db.commit()
        return True
