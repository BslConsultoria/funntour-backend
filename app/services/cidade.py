from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, join, func, or_
from sqlalchemy.orm import selectinload
from app.models.cidade import Cidade
from app.models.estado import Estado
from app.models.pais import Pais
from app.schemas.cidade import CreateCidade, UpdateCidade
import logging
from typing import List, Optional, Dict, Any, Tuple, Union
import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CidadeService:
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Cidade]:
        """Recupera todas as cidades sempre incluindo estado e país relacionados.
        
        Args:
            db: Sessão do banco de dados
            skip: Quantidade de registros para pular
            limit: Quantidade máxima de registros para retornar
            
        Returns:
            Lista de objetos Cidade com estado e país relacionados
        """
        try:
            query = select(Cidade).where(Cidade.dt_exclusao == None).offset(skip).limit(limit)
            
            # Sempre incluir estado e país
            query = query.options(
                selectinload(Cidade.estado).selectinload(Estado.pais)
            )

            result = await db.execute(query)
            cidades = result.scalars().all()
            
            logger.info(f"Recuperadas {len(cidades)} cidades com estado e país")
            return cidades
        except Exception as e:
            logger.error(f"Erro ao recuperar cidades: {e}")
            raise



    @staticmethod
    async def get_by_id(db: AsyncSession, cidade_id: int) -> Optional[Cidade]:
        """Recupera uma cidade pelo ID sempre incluindo o estado e país relacionados.
        
        Args:
            db: Sessão do banco de dados
            cidade_id: ID da cidade a ser buscada
            
        Returns:
            Objeto Cidade com estado e país relacionados
        """
        try:
            query = select(Cidade).where(Cidade.id == cidade_id, Cidade.dt_exclusao == None)
            
            # Sempre incluir estado e país
            query = query.options(
                selectinload(Cidade.estado).selectinload(Estado.pais)
            )
                    
            result = await db.execute(query)
            cidade = result.scalars().first()
            
            if cidade:
                logger.info(f"Cidade recuperada: ID {cidade_id} (com estado e país)")
            else:
                logger.info(f"Cidade não encontrada: ID {cidade_id}")
                
            return cidade
        except Exception as e:
            logger.error(f"Erro ao recuperar cidade por ID: {e}")
            raise

    @staticmethod
    async def get_by_estado_id(db: AsyncSession, estado_id: int) -> List[Cidade]:
        try:
            query = select(Cidade).where(
                Cidade.estado_id == estado_id,
                Cidade.dt_exclusao == None
            )
            # Incluir estado e país
            query = query.options(
                selectinload(Cidade.estado).selectinload(Estado.pais)
            )
            
            result = await db.execute(query)
            cidades = result.scalars().all()
            logger.info(f"Recuperadas {len(cidades)} cidades do estado ID {estado_id} (com estado e país)")
            return cidades
        except Exception as e:
            logger.error(f"Erro ao recuperar cidades por estado ID: {e}")
            raise



    @staticmethod
    async def check_duplicate(db: AsyncSession, estado_id: int, descricao: str, sigla: Optional[str] = None, exclude_id: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """Verifica se já existe uma cidade com a mesma descrição ou sigla dentro do mesmo estado.
        
        Args:
            db: Sessão do banco de dados
            estado_id: ID do estado
            descricao: Descrição da cidade
            sigla: Sigla da cidade (opcional)
            exclude_id: ID opcional a ser excluído da verificação (para updates)
            
        Returns:
            Tupla com (existe_duplicado, mensagem_erro)
        """
        try:
            # Construir condição para verifcar duplicidade de descrição
            conditions = [
                Cidade.estado_id == estado_id,
                func.lower(Cidade.descricao) == descricao.lower(),
                Cidade.dt_exclusao == None
            ]
            
            # Se estiver atualizando, excluir o próprio registro da verificação
            if exclude_id is not None:
                conditions.append(Cidade.id != exclude_id)
                
            # Verificar duplicidade de descrição
            query_descricao = select(Cidade).where(*conditions)
            result = await db.execute(query_descricao)
            existing_descricao = result.scalars().first()
            
            if existing_descricao:
                return True, f"Já existe uma cidade cadastrada com o nome '{descricao}' para o estado selecionado"
            
            # Verificar duplicidade de sigla (apenas se sigla for fornecida)
            if sigla:
                conditions = [
                    Cidade.estado_id == estado_id,
                    func.lower(Cidade.sigla) == sigla.lower(),
                    Cidade.dt_exclusao == None
                ]
                
                if exclude_id is not None:
                    conditions.append(Cidade.id != exclude_id)
                    
                query_sigla = select(Cidade).where(*conditions)
                result = await db.execute(query_sigla)
                existing_sigla = result.scalars().first()
                
                if existing_sigla:
                    return True, f"Já existe uma cidade cadastrada com a sigla '{sigla}' para o estado selecionado"
            
            return False, None
        except Exception as e:
            logger.error(f"Erro ao verificar duplicidade de cidade: {e}")
            raise


            
    @staticmethod
    async def create(db: AsyncSession, cidade_data: CreateCidade) -> Union[Cidade, str]:
        try:
            # Verificar duplicidade de nome ou sigla
            is_duplicate, error_msg = await CidadeService.check_duplicate(
                db, cidade_data.estado_id, cidade_data.descricao, cidade_data.sigla
            )
            
            if is_duplicate:
                logger.warning(f"Tentativa de criar cidade duplicada: {error_msg}")
                return error_msg
            
            cidade = Cidade(
                estado_id=cidade_data.estado_id,
                descricao=cidade_data.descricao,
                sigla=cidade_data.sigla
            )
            db.add(cidade)
            await db.commit()
            await db.refresh(cidade)
            
            # Buscar a cidade novamente com relacionamentos carregados
            cidade = await CidadeService.get_by_id(db, cidade.id)
            logger.info(f"Cidade criada: ID {cidade.id} (com estado e país)")
            return cidade
        except Exception as e:
            await db.rollback()
            logger.error(f"Erro ao criar cidade: {e}")
            raise

    @staticmethod
    async def update(db: AsyncSession, cidade_id: int, cidade_data: UpdateCidade) -> Union[Cidade, str, None]:
        try:
            cidade = await CidadeService.get_by_id(db, cidade_id)
            if not cidade:
                logger.info(f"Tentativa de atualizar cidade não existente: ID {cidade_id}")
                return None
            
            # Se não houver alterações, retornar o objeto atual
            if (cidade_data.estado_id is None or cidade_data.estado_id == cidade.estado_id) and \
               (cidade_data.descricao is None or cidade_data.descricao == cidade.descricao) and \
               (cidade_data.sigla is None or cidade_data.sigla == cidade.sigla):
                return cidade
            
            # Preparar dados para verificar duplicidade
            estado_id_to_check = cidade_data.estado_id if cidade_data.estado_id is not None else cidade.estado_id
            descricao_to_check = cidade_data.descricao if cidade_data.descricao is not None else cidade.descricao
            sigla_to_check = cidade_data.sigla if cidade_data.sigla is not None else cidade.sigla
            
            # Verificar duplicidade de nome ou sigla
            is_duplicate, error_msg = await CidadeService.check_duplicate(
                db, estado_id_to_check, descricao_to_check, sigla_to_check, exclude_id=cidade_id
            )
            
            if is_duplicate:
                logger.warning(f"Tentativa de atualizar cidade para valores duplicados: {error_msg}")
                return error_msg
            
            # Atualizar apenas os campos que foram enviados
            if cidade_data.estado_id is not None:
                cidade.estado_id = cidade_data.estado_id
            if cidade_data.descricao is not None:
                cidade.descricao = cidade_data.descricao
            if cidade_data.sigla is not None:
                cidade.sigla = cidade_data.sigla
            
            # Atualizar data de atualização
            cidade.dt_atualizacao = datetime.datetime.now()
            
            await db.commit()
            
            # Buscar a cidade novamente com relacionamentos carregados
            cidade = await CidadeService.get_by_id(db, cidade_id)
            logger.info(f"Cidade atualizada: ID {cidade_id} (com estado e país)")
            return cidade
        except Exception as e:
            await db.rollback()
            logger.error(f"Erro ao atualizar cidade: {e}")
            raise

    @staticmethod
    async def delete(db: AsyncSession, cidade_id: int) -> bool:
        try:
            cidade = await CidadeService.get_by_id(db, cidade_id)
            if not cidade:
                logger.info(f"Tentativa de excluir cidade não existente: ID {cidade_id}")
                return False

            # Soft delete - atualizar o campo dt_exclusao
            cidade.dt_exclusao = datetime.datetime.now()
            await db.commit()
            logger.info(f"Cidade excluída (soft delete): ID {cidade_id}")
            return True
        except Exception as e:
            await db.rollback()
            logger.error(f"Erro ao excluir cidade: {e}")
            raise
