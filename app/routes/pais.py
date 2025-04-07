from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.config.database import get_db
from app.schemas.pais import CreatePais, UpdatePais, PaisResponse
from app.services.pais import PaisService
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/pais",
    tags=["País"],
    responses={404: {"description": "País não encontrado"}},
)

@router.get("/", response_model=List[PaisResponse], summary="Listar países", 
            description="Retorna lista de países cadastrados no sistema")
async def get_paises(
    skip: int = Query(0, description="Registros para pular"), 
    limit: int = Query(100, description="Limite de registros"),
    db: AsyncSession = Depends(get_db)
):
    try:
        paises = await PaisService.get_all(db, skip=skip, limit=limit)
        return paises
    except Exception as e:
        logger.error(f"Erro ao listar países: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitação"
        )

@router.get("/{pais_id}", response_model=Optional[PaisResponse], summary="Obter país por ID",
            description="Retorna um país a partir do ID informado ou null se não encontrado")
async def get_pais(
    pais_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        pais = await PaisService.get_by_id(db, pais_id=pais_id)
        # Retorna null (None) se o país não for encontrado, sem gerar erro 404
        return pais
    except Exception as e:
        logger.error(f"Erro ao buscar país por ID: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitação"
        )

@router.post("/", response_model=PaisResponse, status_code=status.HTTP_201_CREATED,
              summary="Criar novo país", description="Adiciona um novo país ao sistema")
async def create_pais(
    pais: CreatePais,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await PaisService.create(db=db, pais_data=pais)
    except Exception as e:
        logger.error(f"Erro ao criar país: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitação"
        )

@router.put("/{pais_id}", response_model=PaisResponse, summary="Atualizar país",
            description="Atualiza os dados de um país existente")
async def update_pais(
    pais_id: int,
    pais: UpdatePais,
    db: AsyncSession = Depends(get_db)
):
    try:
        updated_pais = await PaisService.update(db=db, pais_id=pais_id, pais_data=pais)
        if updated_pais is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"País com ID {pais_id} não encontrado"
            )
        return updated_pais
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar país: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitação"
        )

@router.delete("/{pais_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Excluir país", description="Remove um país do sistema (soft delete)")
async def delete_pais(
    pais_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await PaisService.delete(db=db, pais_id=pais_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"País com ID {pais_id} não encontrado"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir país: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitação"
        )
