from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, join, func, or_
from sqlalchemy.orm import selectinload
from app.models.estado import Estado
from app.models.pais import Pais
from app.schemas.estado import CreateEstado, UpdateEstado
import logging
from typing import List, Optional, Dict, Any, Tuple, Union
import datetime

# Configurau00e7u00e3o de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EstadoService:
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Estado]:
        """Recupera todos os estados sempre incluindo o país relacionado.
        
        Args:
            db: Sessão do banco de dados
            skip: Quantidade de registros para pular
            limit: Quantidade máxima de registros para retornar
            
        Returns:
            Lista de objetos Estado com o país relacionado
        """
        try:
            # Sempre incluir o relacionamento com país
            query = select(Estado).where(Estado.dt_exclusao == None).offset(skip).limit(limit)
            query = query.options(selectinload(Estado.pais))
                
            result = await db.execute(query)
            estados = result.scalars().all()
            
            logger.info(f"Recuperados {len(estados)} estados com país")
            return estados
        except Exception as e:
            logger.error(f"Erro ao recuperar estados: {e}")
            raise



    @staticmethod
    async def get_by_id(db: AsyncSession, estado_id: int) -> Optional[Estado]:
        """Recupera um estado pelo ID sempre incluindo o país relacionado.
        
        Args:
            db: Sessão do banco de dados
            estado_id: ID do estado a ser buscado
            
        Returns:
            Objeto Estado com o país relacionado
        """
        try:
            # Sempre incluir o relacionamento com país
            query = select(Estado).where(Estado.id == estado_id, Estado.dt_exclusao == None)
            query = query.options(selectinload(Estado.pais))
                
            result = await db.execute(query)
            estado = result.scalars().first()
            
            if estado:
                logger.info(f"Estado recuperado: ID {estado_id} (com país)")
            else:
                logger.info(f"Estado não encontrado: ID {estado_id}")
                
            return estado
        except Exception as e:
            logger.error(f"Erro ao recuperar estado por ID: {e}")
            raise

    @staticmethod
    async def get_by_pais_id(db: AsyncSession, pais_id: int) -> List[Estado]:
        try:
            query = select(Estado).where(
                Estado.pais_id == pais_id,
                Estado.dt_exclusao == None
            )
            result = await db.execute(query)
            estados = result.scalars().all()
            logger.info(f"Recuperados {len(estados)} estados do pau00eds ID {pais_id}")
            return estados
        except Exception as e:
            logger.error(f"Erro ao recuperar estados por pau00eds ID: {e}")
            raise

    @staticmethod
    async def check_duplicate(db: AsyncSession, pais_id: int, descricao: str, sigla: str, exclude_id: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """Verifica se já existe um estado com a mesma descrição ou sigla dentro do mesmo país.
        
        Args:
            db: Sessão do banco de dados
            pais_id: ID do país
            descricao: Descrição do estado
            sigla: Sigla do estado
            exclude_id: ID opcional a ser excluído da verificação (para updates)
            
        Returns:
            Tupla com (existe_duplicado, mensagem_erro)
        """
        try:
            # Construção da query base - busca pelo mesmo país e mesma descrição ou sigla
            query = select(Estado).where(
                Estado.pais_id == pais_id,
                or_(
                    func.lower(Estado.descricao) == descricao.lower(),
                    func.lower(Estado.sigla) == sigla.lower()
                ),
                Estado.dt_exclusao == None
            )
            
            # Se estiver atualizando, excluir o próprio registro da verificação
            if exclude_id is not None:
                query = query.where(Estado.id != exclude_id)
                
            result = await db.execute(query)
            existing = result.scalars().first()
            
            if existing:
                if existing.descricao.lower() == descricao.lower():
                    return True, f"Já existe um estado cadastrado com o nome '{descricao}' para o país selecionado"
                else:
                    return True, f"Já existe um estado cadastrado com a sigla '{sigla}' para o país selecionado"
            
            return False, None
        except Exception as e:
            logger.error(f"Erro ao verificar duplicidade de estado: {e}")
            raise
            
    @staticmethod
    async def create(db: AsyncSession, estado_data: CreateEstado) -> Union[Estado, str]:
        try:
            # Verificar duplicidade
            is_duplicate, error_msg = await EstadoService.check_duplicate(
                db, estado_data.pais_id, estado_data.descricao, estado_data.sigla
            )
            
            if is_duplicate:
                logger.warning(f"Tentativa de criar estado duplicado: {error_msg}")
                return error_msg
                
            estado = Estado(
                pais_id=estado_data.pais_id,
                descricao=estado_data.descricao,
                sigla=estado_data.sigla
            )
            db.add(estado)
            await db.commit()
            await db.refresh(estado)
            
            # Buscar o estado novamente com o país relacionado
            estado = await EstadoService.get_by_id(db, estado.id)
            logger.info(f"Estado criado: ID {estado.id} (com país)")
            return estado
        except Exception as e:
            await db.rollback()
            logger.error(f"Erro ao criar estado: {e}")
            raise

    @staticmethod
    async def update(db: AsyncSession, estado_id: int, estado_data: UpdateEstado) -> Union[Estado, str, None]:
        try:
            estado = await EstadoService.get_by_id(db, estado_id)
            if not estado:
                logger.info(f"Tentativa de atualizar estado não existente: ID {estado_id}")
                return None
            
            # Se não houver alterações, retornar o objeto atual
            if (estado_data.pais_id is None or estado_data.pais_id == estado.pais_id) and \
               (estado_data.descricao is None or estado_data.descricao == estado.descricao) and \
               (estado_data.sigla is None or estado_data.sigla == estado.sigla):
                return estado
            
            # Verificar duplicidade apenas se houver alterações nos campos relevantes
            pais_id_to_check = estado_data.pais_id if estado_data.pais_id is not None else estado.pais_id
            descricao_to_check = estado_data.descricao if estado_data.descricao is not None else estado.descricao
            sigla_to_check = estado_data.sigla if estado_data.sigla is not None else estado.sigla
            
            is_duplicate, error_msg = await EstadoService.check_duplicate(
                db, pais_id_to_check, descricao_to_check, sigla_to_check, exclude_id=estado_id
            )
            
            if is_duplicate:
                logger.warning(f"Tentativa de atualizar estado para valores duplicados: {error_msg}")
                return error_msg
            
            # Atualizar apenas os campos que foram enviados
            if estado_data.pais_id is not None:
                estado.pais_id = estado_data.pais_id
            if estado_data.descricao is not None:
                estado.descricao = estado_data.descricao
            if estado_data.sigla is not None:
                estado.sigla = estado_data.sigla
            
            # Atualizar data de atualização
            estado.dt_atualizacao = datetime.datetime.now()
            
            await db.commit()
            
            # Buscar o estado novamente com o país relacionado
            estado = await EstadoService.get_by_id(db, estado_id)
            logger.info(f"Estado atualizado: ID {estado_id} (com país)")
            return estado
        except Exception as e:
            await db.rollback()
            logger.error(f"Erro ao atualizar estado: {e}")
            raise

    @staticmethod
    async def delete(db: AsyncSession, estado_id: int) -> bool:
        try:
            estado = await EstadoService.get_by_id(db, estado_id)
            if not estado:
                logger.info(f"Tentativa de excluir estado nu00e3o existente: ID {estado_id}")
                return False

            # Soft delete - atualizar o campo dt_exclusao
            estado.dt_exclusao = datetime.datetime.now()
            await db.commit()
            logger.info(f"Estado excluu00eddo (soft delete): ID {estado_id}")
            return True
        except Exception as e:
            await db.rollback()
            logger.error(f"Erro ao excluir estado: {e}")
            raise
