from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.perfil import Perfil
import logging

logger = logging.getLogger(__name__)

class PerfilService:
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Perfil]:
        """
        Retorna todos os perfis não excluídos.
        """
        query = select(Perfil).where(Perfil.dt_exclusao.is_(None)).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, perfil_id: int) -> Optional[Perfil]:
        """
        Retorna um perfil pelo ID se não estiver excluído.
        """
        query = select(Perfil).where(
            and_(
                Perfil.id == perfil_id,
                Perfil.dt_exclusao.is_(None)
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def get_by_descricao(db: AsyncSession, descricao: str) -> Optional[Perfil]:
        """
        Busca um perfil pela descrição.
        """
        query = select(Perfil).where(
            and_(
                func.lower(Perfil.descricao) == descricao.lower(),
                Perfil.dt_exclusao.is_(None)
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def create(db: AsyncSession, perfil_data: Dict[str, Any]) -> Perfil:
        """
        Cria um novo perfil.
        """
        # Verifica se já existe um perfil com a mesma descrição
        existing_perfil = await PerfilService.get_by_descricao(db, perfil_data["descricao"])
        if existing_perfil:
            raise ValueError(f"Já existe um perfil com a descrição '{perfil_data['descricao']}'")

        # Cria o novo perfil
        db_perfil = Perfil(**perfil_data)
        db.add(db_perfil)
        await db.commit()
        await db.refresh(db_perfil)
        return db_perfil

    @staticmethod
    async def update(db: AsyncSession, perfil_id: int, perfil_data: Dict[str, Any]) -> Optional[Perfil]:
        """
        Atualiza um perfil existente.
        """
        # Verifica se o perfil existe
        db_perfil = await PerfilService.get_by_id(db, perfil_id)
        if not db_perfil:
            return None

        # Verifica se a descrição está sendo alterada e se já existe outro perfil com essa descrição
        if "descricao" in perfil_data and perfil_data["descricao"] != db_perfil.descricao:
            existing_perfil = await PerfilService.get_by_descricao(db, perfil_data["descricao"])
            if existing_perfil and existing_perfil.id != perfil_id:
                raise ValueError(f"Já existe um perfil com a descrição '{perfil_data['descricao']}'")

        # Atualiza o perfil
        update_stmt = update(Perfil).where(Perfil.id == perfil_id).values(**perfil_data)
        await db.execute(update_stmt)
        await db.commit()
        return await PerfilService.get_by_id(db, perfil_id)

    @staticmethod
    async def delete(db: AsyncSession, perfil_id: int) -> bool:
        """
        Exclui logicamente um perfil.
        """
        db_perfil = await PerfilService.get_by_id(db, perfil_id)
        if not db_perfil:
            return False

        # Exclusão lógica
        update_stmt = update(Perfil).where(Perfil.id == perfil_id).values(dt_exclusao=datetime.now())
        await db.execute(update_stmt)
        await db.commit()
        return True
