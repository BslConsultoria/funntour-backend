from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_
from app.models.pais import Pais
from app.schemas.pais import CreatePais, UpdatePais
import logging
from typing import List, Optional, Tuple, Union
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
    async def check_duplicate(db: AsyncSession, descricao: str, sigla: str, exclude_id: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """Verifica se já existe um país com a mesma descrição ou sigla.
        
        Args:
            db: Sessão do banco de dados
            descricao: Descrição do país
            sigla: Sigla do país
            exclude_id: ID opcional a ser excluído da verificação (para updates)
            
        Returns:
            Tupla com (existe_duplicado, mensagem_erro)
        """
        try:
            # Construção da query base
            query = select(Pais).where(
                or_(
                    func.lower(Pais.descricao) == descricao.lower(),
                    func.lower(Pais.sigla) == sigla.lower()
                ),
                Pais.dt_exclusao == None
            )
            
            # Se estiver atualizando, excluir o próprio registro da verificação
            if exclude_id is not None:
                query = query.where(Pais.id != exclude_id)
                
            result = await db.execute(query)
            existing = result.scalars().first()
            
            if existing:
                if existing.descricao.lower() == descricao.lower():
                    return True, f"Já existe um país cadastrado com o nome '{descricao}'"
                else:
                    return True, f"Já existe um país cadastrado com a sigla '{sigla}'"
            
            return False, None
        except Exception as e:
            logger.error(f"Erro ao verificar duplicidade de país: {e}")
            raise
    
    @staticmethod
    async def create(db: AsyncSession, pais_data: CreatePais) -> Union[Pais, str]:
        try:
            # Verificar duplicidade
            is_duplicate, error_msg = await PaisService.check_duplicate(
                db, pais_data.descricao, pais_data.sigla
            )
            
            if is_duplicate:
                logger.warning(f"Tentativa de criar país duplicado: {error_msg}")
                return error_msg
            
            # Criar o novo país se não houver duplicidade
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
    async def update(db: AsyncSession, pais_id: int, pais_data: UpdatePais) -> Union[Pais, str, None]:
        try:
            pais = await PaisService.get_by_id(db, pais_id)
            if not pais:
                logger.info(f"Tentativa de atualizar país não existente: ID {pais_id}")
                return None
            
            # Se não houver alterações, retornar o objeto atual
            if (pais_data.descricao is None or pais_data.descricao == pais.descricao) and \
               (pais_data.sigla is None or pais_data.sigla == pais.sigla):
                return pais
            
            # Verificar duplicidade apenas se houver alterações nos campos relevantes
            descricao_to_check = pais_data.descricao if pais_data.descricao is not None else pais.descricao
            sigla_to_check = pais_data.sigla if pais_data.sigla is not None else pais.sigla
            
            is_duplicate, error_msg = await PaisService.check_duplicate(
                db, descricao_to_check, sigla_to_check, exclude_id=pais_id
            )
            
            if is_duplicate:
                logger.warning(f"Tentativa de atualizar país para valores duplicados: {error_msg}")
                return error_msg
            
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
