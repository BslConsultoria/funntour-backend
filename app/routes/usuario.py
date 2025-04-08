from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from app.config.database import get_db
from app.schemas.usuario import CreateUsuario, UpdateUsuario, UsuarioResponse
from app.services.usuario import UsuarioService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/usuario",
    tags=["Usuários"],
    responses={404: {"description": "Usuário não encontrado"}},
)

@router.get("/", summary="Listar usuários", 
            description="Retorna lista de usuários cadastrados no sistema")
async def get_usuarios(
    skip: int = Query(0, description="Registros para pular"), 
    limit: int = Query(100, description="Limite de registros"),
    db: AsyncSession = Depends(get_db)
):
    try:
        logger.info("Buscando todos os usuários")
        usuarios = await UsuarioService.get_all(db, skip=skip, limit=limit)
        logger.info(f"Encontrados {len(usuarios)} usuários")
        
        # Prepara a lista de usuários para resposta estruturada
        resultado = []
        for usuario in usuarios:
            # Dados básicos do usuário - sempre presentes
            usuario_dict = {
                "id": usuario.id,
                "nome": usuario.nome,
                "cpf_cnpj": usuario.cpf_cnpj,
                "email": usuario.email,
                "telefone": usuario.telefone,
                "whatsapp": usuario.whatsapp,
                "dt_nascimento": usuario.dt_nascimento.isoformat() if usuario.dt_nascimento else None,
                "perfil_id": usuario.perfil_id,
            }
            
            # Adiciona perfil se existir
            if getattr(usuario, 'perfil', None) is not None:
                usuario_dict["perfil_descricao"] = getattr(usuario.perfil, 'descricao', None)
            else:
                usuario_dict["perfil_descricao"] = None
                
            # Adiciona endereco se existir, com verificações em cada nível
            endereco_dict = None
            if getattr(usuario, 'endereco', None) is not None:
                endereco = usuario.endereco
                endereco_dict = {
                    "id": endereco.id,
                    "cep": endereco.cep,
                    "complemento": endereco.complemento,
                    "cidade_id": endereco.cidade_id,
                }
                
                # Adiciona objeto cidade completo com tratamento robusto de erros
                try:
                    if getattr(endereco, 'cidade', None) is not None:
                        cidade = endereco.cidade
                        cidade_dict = {
                            "id": cidade.id,
                            "descricao": getattr(cidade, 'descricao', None),
                            "sigla": getattr(cidade, 'sigla', None)
                        }
                        
                        # Adiciona o objeto estado se existir
                        try:
                            # Verifica se podemos acessar o estado via cidade
                            estado = None
                            if getattr(cidade, 'estado', None) is not None:
                                estado = cidade.estado
                            
                            # Se o estado não estiver carregado pelo lazy loading, busca explicitamente
                            if estado is None and getattr(cidade, 'estado_id', None) is not None:
                                try:
                                    logger.info(f"Buscando estado com ID {cidade.estado_id} explicitamente")
                                    from app.models.estado import Estado
                                    estado_query = select(Estado).where(
                                        Estado.id == cidade.estado_id,
                                        Estado.dt_exclusao.is_(None)
                                    )
                                    estado_result = await db.execute(estado_query)
                                    estado = estado_result.scalars().first()
                                    logger.info(f"Estado encontrado: {estado.descricao if estado else None}")
                                except Exception as e:
                                    logger.error(f"Erro ao buscar estado explicitamente: {e}")
                                    estado = None
                            
                            if estado is not None:
                                estado_dict = {
                                    "id": estado.id,
                                    "sigla": getattr(estado, 'sigla', None),
                                    "descricao": getattr(estado, 'descricao', None)
                                }
                                
                                # Adiciona o objeto pais se existir
                                try:
                                    if getattr(estado, 'pais', None) is not None:
                                        pais = estado.pais
                                        pais_dict = {
                                            "id": pais.id,
                                            "descricao": getattr(pais, 'descricao', None),
                                            "sigla": getattr(pais, 'sigla', None)
                                        }
                                        estado_dict["pais"] = pais_dict
                                except Exception as e:
                                    logger.error(f"Erro ao processar pais: {e}")
                                    estado_dict["pais"] = None
                                    
                                cidade_dict["estado"] = estado_dict
                            else:
                                cidade_dict["estado"] = None
                        except Exception as e:
                            logger.error(f"Erro ao processar estado: {e}")
                            cidade_dict["estado"] = None
                            
                        endereco_dict["cidade"] = cidade_dict
                    else:
                        endereco_dict["cidade"] = None
                except Exception as e:
                    logger.error(f"Erro ao processar cidade: {e}")
                    endereco_dict["cidade"] = None
                    
            usuario_dict["endereco"] = endereco_dict
            resultado.append(usuario_dict)
            
        # Retorna diretamente a lista de usuários
        return resultado
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Erro ao listar usuários: {e}\n{tb}")
        # Simplificando a mensagem de erro para o cliente
        raise HTTPException(status_code=500, detail="Erro interno no servidor. Verifique os logs para mais detalhes.")

@router.get("/{usuario_id}", 
            summary="Obter usuário por ID",
            description="Retorna um usuário a partir do ID informado ou null se não encontrado")
async def get_usuario(
    usuario_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        usuario = await UsuarioService.get_by_id(db, usuario_id=usuario_id)
        
        # Retorna null quando não encontrar o usuário
        if not usuario:
            return None
            
        # Dados básicos do usuário - sempre presentes
        usuario_dict = {
            "id": usuario.id,
            "nome": usuario.nome,
            "cpf_cnpj": usuario.cpf_cnpj,
            "email": usuario.email,
            "telefone": usuario.telefone,
            "whatsapp": usuario.whatsapp,
            "dt_nascimento": usuario.dt_nascimento.isoformat() if usuario.dt_nascimento else None,
            "perfil_id": usuario.perfil_id,
        }
        
        # Adiciona perfil se existir
        if getattr(usuario, 'perfil', None) is not None:
            usuario_dict["perfil_descricao"] = getattr(usuario.perfil, 'descricao', None)
        else:
            usuario_dict["perfil_descricao"] = None
            
        # Adiciona endereco se existir, com verificações em cada nível
        endereco_dict = None
        if getattr(usuario, 'endereco', None) is not None:
            endereco = usuario.endereco
            endereco_dict = {
                "id": endereco.id,
                "cep": endereco.cep,
                "complemento": endereco.complemento,
                "cidade_id": endereco.cidade_id,
            }
            
            # Adiciona objeto cidade completo com tratamento robusto de erros
            try:
                if getattr(endereco, 'cidade', None) is not None:
                    cidade = endereco.cidade
                    cidade_dict = {
                        "id": cidade.id,
                        "descricao": getattr(cidade, 'descricao', None),
                        "sigla": getattr(cidade, 'sigla', None)
                    }
                    
                    # Adiciona o objeto estado se existir
                    try:
                        # Verifica se podemos acessar o estado via cidade
                        estado = None
                        if getattr(cidade, 'estado', None) is not None:
                            estado = cidade.estado
                            
                        # Se o estado não estiver carregado pelo lazy loading, busca explicitamente
                        if estado is None and getattr(cidade, 'estado_id', None) is not None:
                            try:
                                logger.info(f"Buscando estado com ID {cidade.estado_id} explicitamente")
                                from app.models.estado import Estado
                                estado_query = select(Estado).where(
                                    Estado.id == cidade.estado_id,
                                    Estado.dt_exclusao.is_(None)
                                )
                                estado_result = await db.execute(estado_query)
                                estado = estado_result.scalars().first()
                                logger.info(f"Estado encontrado: {estado.descricao if estado else None}")
                            except Exception as e:
                                logger.error(f"Erro ao buscar estado explicitamente: {e}")
                                estado = None
                                
                        if estado is not None:
                            estado_dict = {
                                "id": estado.id,
                                "sigla": getattr(estado, 'sigla', None),
                                "descricao": getattr(estado, 'descricao', None)
                            }
                            
                            # Adiciona o objeto pais se existir
                            try:
                                if getattr(estado, 'pais', None) is not None:
                                    pais = estado.pais
                                    pais_dict = {
                                        "id": pais.id,
                                        "descricao": getattr(pais, 'descricao', None),
                                        "sigla": getattr(pais, 'sigla', None)
                                    }
                                    estado_dict["pais"] = pais_dict
                            except Exception as e:
                                logger.error(f"Erro ao processar pais: {e}")
                                estado_dict["pais"] = None
                                
                            cidade_dict["estado"] = estado_dict
                        else:
                            cidade_dict["estado"] = None
                    except Exception as e:
                        logger.error(f"Erro ao processar estado: {e}")
                        cidade_dict["estado"] = None
                        
                    endereco_dict["cidade"] = cidade_dict
                else:
                    endereco_dict["cidade"] = None
            except Exception as e:
                logger.error(f"Erro ao processar cidade: {e}")
                endereco_dict["cidade"] = None
                
        usuario_dict["endereco"] = endereco_dict
        
        # Retorna diretamente o objeto de usuário
        return usuario_dict
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Erro ao buscar usuário: {e}\n{tb}")
        # Simplificando a mensagem de erro para o cliente
        raise HTTPException(status_code=500, detail="Erro interno no servidor. Verifique os logs para mais detalhes.")

@router.post("/", status_code=status.HTTP_201_CREATED, 
              summary="Criar usuário",
              description="Cria um novo usuário no sistema")
async def create_usuario(
    usuario: CreateUsuario,
    db: AsyncSession = Depends(get_db)
):
    try:
        usuario_data = usuario.dict()
        db_usuario = await UsuarioService.create(db, usuario_data)
        
        # Retornando uma resposta estruturada
        return {
            "success": True,
            "message": "Usuário criado com sucesso",
            "data": {
                "id": db_usuario.id,
                "cpf_cnpj": db_usuario.cpf_cnpj,
                "nome": db_usuario.nome,
                "email": db_usuario.email
            }
        }
    except ValueError as e:
        logger.error(f"Erro de validação ao criar usuário: {e}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Erro ao criar usuário: {e}\n{tb}")
        # Simplificando a mensagem de erro para o cliente
        raise HTTPException(status_code=500, detail="Erro interno no servidor. Verifique os logs para mais detalhes.")

@router.put("/{usuario_id}", 
            summary="Atualizar usuário",
            description="Atualiza um usuário existente")
async def update_usuario(
    usuario_id: int,
    usuario: UpdateUsuario,
    db: AsyncSession = Depends(get_db)
):
    try:
        usuario_data = {k: v for k, v in usuario.dict().items() if v is not None}
        if not usuario_data:
            # Se não houver dados para atualizar, apenas retorna o usuário atual
            return await UsuarioService.get_by_id(db, usuario_id)
            
        updated_usuario = await UsuarioService.update(db, usuario_id, usuario_data)
        if not updated_usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="usuário não encontrado")
        return updated_usuario
    except ValueError as e:
        logger.error(f"Erro de validação ao atualizar usuário: {e}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar usuário: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar usuário: {str(e)}")

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT, 
               summary="Excluir usuário",
               description="Exclui um usuário existente (exclusão lógica)")
async def delete_usuario(
    usuario_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        success = await UsuarioService.delete(db, usuario_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="usuário não encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir usuário: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao excluir usuário: {str(e)}")
