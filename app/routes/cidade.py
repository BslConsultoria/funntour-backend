from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any, Union

from app.config.database import get_db
from app.schemas.cidade import CreateCidade, UpdateCidade, CidadeResponse
from app.services.cidade import CidadeService
import logging

# Configurau00e7u00e3o de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/cidade",
    tags=["Cidades"],
    responses={404: {"description": "Cidade nu00e3o encontrada"}},
)

@router.get("/", response_model=List[CidadeResponse], summary="Listar cidades", 
            description="Retorna lista de cidades cadastradas no sistema (inclui estado e país relacionados)")
async def get_cidades(
    skip: int = Query(0, description="Registros para pular"), 
    limit: int = Query(100, description="Limite de registros"),
    db: AsyncSession = Depends(get_db)
):
    try:
        cidades = await CidadeService.get_all(
            db, 
            skip=skip, 
            limit=limit
        )
        return cidades
    except Exception as e:
        logger.error(f"Erro ao listar cidades: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitau00e7u00e3o"
        )





@router.get("/estado/{estado_id}", response_model=List[CidadeResponse], 
             summary="Listar cidades por estado",
             description="Retorna lista de cidades de um determinado estado")
async def get_cidades_by_estado(
    estado_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        cidades = await CidadeService.get_by_estado_id(db, estado_id=estado_id)
        return cidades
    except Exception as e:
        logger.error(f"Erro ao listar cidades por estado: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitau00e7u00e3o"
        )

@router.get("/{cidade_id}", response_model=Optional[CidadeResponse], 
            summary="Obter cidade por ID",
            description="Retorna uma cidade a partir do ID informado ou null se não encontrada (inclui estado e país relacionados)")
async def get_cidade(
    cidade_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        cidade = await CidadeService.get_by_id(
            db, 
            cidade_id=cidade_id
        )
        # Retorna null (None) se a cidade não for encontrada, sem gerar erro 404
        return cidade
    except Exception as e:
        logger.error(f"Erro ao buscar cidade por ID: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitação"
        )

@router.post("/", response_model=Union[CidadeResponse, str], status_code=status.HTTP_201_CREATED,
              summary="Criar nova cidade", 
              description="Adiciona uma nova cidade ao sistema. Retorna erro se a cidade já existir com o mesmo nome ou sigla para o estado selecionado")
async def create_cidade(
    cidade: CreateCidade,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await CidadeService.create(db=db, cidade_data=cidade)
        
        # Se retornou uma string, é uma mensagem de erro de validação
        if isinstance(result, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar cidade: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitau00e7u00e3o"
        )

@router.put("/{cidade_id}", response_model=Union[CidadeResponse, str], 
            summary="Atualizar cidade",
            description="Atualiza os dados de uma cidade existente ou retorna mensagem de erro se houver duplicidade de nome ou sigla")
async def update_cidade(
    cidade_id: int,
    cidade: UpdateCidade,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await CidadeService.update(db=db, cidade_id=cidade_id, cidade_data=cidade)
        
        # Se retornou None, a cidade não foi encontrada
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cidade com ID {cidade_id} não encontrada"
            )
            
        # Se retornou uma string, é uma mensagem de erro de validação
        if isinstance(result, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar cidade: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitau00e7u00e3o"
        )

@router.delete("/{cidade_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Excluir cidade", description="Remove uma cidade do sistema (soft delete)")
async def delete_cidade(
    cidade_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await CidadeService.delete(db=db, cidade_id=cidade_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cidade com ID {cidade_id} não encontrada"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir cidade: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitau00e7u00e3o"
        )
