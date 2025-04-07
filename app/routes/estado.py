from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from app.config.database import get_db
from app.schemas.estado import CreateEstado, UpdateEstado, EstadoResponse
from app.services.estado import EstadoService
import logging

# Configurau00e7u00e3o de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/estado",
    tags=["Estados"],
    responses={404: {"description": "Estado nu00e3o encontrado"}},
)

@router.get("/", response_model=List[EstadoResponse], summary="Listar estados", 
            description="Retorna lista de estados cadastrados no sistema (inclui o país relacionado)")
async def get_estados(
    skip: int = Query(0, description="Registros para pular"), 
    limit: int = Query(100, description="Limite de registros"),
    db: AsyncSession = Depends(get_db)
):
    try:
        estados = await EstadoService.get_all(db, skip=skip, limit=limit)
        return estados
    except Exception as e:
        logger.error(f"Erro ao listar estados: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitau00e7u00e3o"
        )



@router.get("/pais/{pais_id}", response_model=List[EstadoResponse], 
             summary="Listar estados por pau00eds",
             description="Retorna lista de estados de um determinado pau00eds")
async def get_estados_by_pais(
    pais_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        estados = await EstadoService.get_by_pais_id(db, pais_id=pais_id)
        return estados
    except Exception as e:
        logger.error(f"Erro ao listar estados por pau00eds: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitau00e7u00e3o"
        )

@router.get("/{estado_id}", response_model=Optional[EstadoResponse], 
            summary="Obter estado por ID",
            description="Retorna um estado a partir do ID informado ou null se não encontrado (inclui o país relacionado)")
async def get_estado(
    estado_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        estado = await EstadoService.get_by_id(db, estado_id=estado_id)
        # Retorna null (None) se o estado não for encontrado, sem gerar erro 404
        return estado
    except Exception as e:
        logger.error(f"Erro ao buscar estado por ID: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitação"
        )

@router.post("/", response_model=EstadoResponse, status_code=status.HTTP_201_CREATED,
              summary="Criar novo estado", description="Adiciona um novo estado ao sistema")
async def create_estado(
    estado: CreateEstado,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await EstadoService.create(db=db, estado_data=estado)
    except Exception as e:
        logger.error(f"Erro ao criar estado: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitau00e7u00e3o"
        )

@router.put("/{estado_id}", response_model=Optional[EstadoResponse], 
            summary="Atualizar estado",
            description="Atualiza os dados de um estado existente ou retorna null se nu00e3o encontrado")
async def update_estado(
    estado_id: int,
    estado: UpdateEstado,
    db: AsyncSession = Depends(get_db)
):
    try:
        updated_estado = await EstadoService.update(db=db, estado_id=estado_id, estado_data=estado)
        return updated_estado
    except Exception as e:
        logger.error(f"Erro ao atualizar estado: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitau00e7u00e3o"
        )

@router.delete("/{estado_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Excluir estado", description="Remove um estado do sistema (soft delete)")
async def delete_estado(
    estado_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await EstadoService.delete(db=db, estado_id=estado_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estado com ID {estado_id} nu00e3o encontrado"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir estado: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitau00e7u00e3o"
        )
