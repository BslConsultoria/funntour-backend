from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from app.config.database import get_db
from app.schemas.perfil import CreatePerfil, UpdatePerfil, PerfilResponse
from app.services.perfil import PerfilService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/perfil",
    tags=["Perfis"],
    responses={404: {"description": "Perfil nu00e3o encontrado"}},
)

@router.get("/", response_model=List[PerfilResponse], summary="Listar perfis", 
            description="Retorna lista de perfis cadastrados no sistema")
async def get_perfis(
    skip: int = Query(0, description="Registros para pular"), 
    limit: int = Query(100, description="Limite de registros"),
    db: AsyncSession = Depends(get_db)
):
    try:
        perfis = await PerfilService.get_all(db, skip=skip, limit=limit)
        return perfis
    except Exception as e:
        logger.error(f"Erro ao listar perfis: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar perfis: {str(e)}")

@router.get("/{perfil_id}", response_model=Optional[PerfilResponse], 
            summary="Obter perfil por ID",
            description="Retorna um perfil a partir do ID informado ou null se nu00e3o encontrado")
async def get_perfil(
    perfil_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        perfil = await PerfilService.get_by_id(db, perfil_id=perfil_id)
        # Retorna null (None) se o perfil nu00e3o for encontrado, sem gerar erro 404
        return perfil
    except Exception as e:
        logger.error(f"Erro ao buscar perfil: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar perfil: {str(e)}")

@router.post("/", response_model=PerfilResponse, 
              status_code=status.HTTP_201_CREATED,
              summary="Criar perfil",
              description="Cria um novo perfil no sistema")
async def create_perfil(
    perfil: CreatePerfil,
    db: AsyncSession = Depends(get_db)
):
    try:
        perfil_data = perfil.dict()
        perfil = await PerfilService.create(db, perfil_data)
        return perfil
    except ValueError as e:
        logger.error(f"Erro de validau00e7u00e3o ao criar perfil: {e}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar perfil: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar perfil: {str(e)}")

@router.put("/{perfil_id}", response_model=Optional[PerfilResponse], 
            summary="Atualizar perfil",
            description="Atualiza um perfil existente")
async def update_perfil(
    perfil_id: int,
    perfil: UpdatePerfil,
    db: AsyncSession = Depends(get_db)
):
    try:
        perfil_data = {k: v for k, v in perfil.dict().items() if v is not None}
        if not perfil_data:
            # Se nu00e3o houver dados para atualizar, apenas retorna o perfil atual
            return await PerfilService.get_by_id(db, perfil_id)
            
        updated_perfil = await PerfilService.update(db, perfil_id, perfil_data)
        if not updated_perfil:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil nu00e3o encontrado")
        return updated_perfil
    except ValueError as e:
        logger.error(f"Erro de validau00e7u00e3o ao atualizar perfil: {e}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar perfil: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar perfil: {str(e)}")

@router.delete("/{perfil_id}", status_code=status.HTTP_204_NO_CONTENT, 
               summary="Excluir perfil",
               description="Exclui um perfil existente (exclusu00e3o lu00f3gica)")
async def delete_perfil(
    perfil_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        success = await PerfilService.delete(db, perfil_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil nu00e3o encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir perfil: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao excluir perfil: {str(e)}")
