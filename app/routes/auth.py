import logging
from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.schemas.usuario import UsuarioAuth, UsuarioResponse
from app.services.usuario import UsuarioService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"],
    responses={401: {"description": "Não autorizado"}},
)

@router.post("/login", response_model=UsuarioResponse, 
              summary="Autenticar usuário",
              description="Autentica um usuário com CPF/CNPJ e senha")
async def login(
    auth_data: UsuarioAuth,
    db: AsyncSession = Depends(get_db)
):
    try:
        usuario = await UsuarioService.autenticar(db, auth_data.cpf_cnpj, auth_data.senha)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao autenticar usuário: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao autenticar usuário: {str(e)}")

@router.post("/alterar-senha", status_code=status.HTTP_204_NO_CONTENT, 
             summary="Alterar senha",
             description="Altera a senha de um usuário")
async def change_password(
    usuario_id: int,
    senha_atual: str = Body(..., description="Senha atual"),
    nova_senha: str = Body(..., description="Nova senha"),
    db: AsyncSession = Depends(get_db)
):
    try:
        success = await UsuarioService.change_password(db, usuario_id, senha_atual, nova_senha)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    except ValueError as e:
        logger.error(f"Erro de validação ao alterar senha: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao alterar senha: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao alterar senha: {str(e)}")

@router.post("/recuperar-senha", status_code=status.HTTP_200_OK,
            summary="Solicitar recuperação de senha",
            description="Envia um token de recuperação de senha para o e-mail e WhatsApp do usuário")
async def request_password_recovery(
    credential: str = Body(..., description="CPF/CNPJ ou e-mail do usuário"),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Importa o serviço de notificação
        from app.services.notifications.notification_service import NotificationService
        notification_service = NotificationService()
        
        # Gera o token de recuperação
        result = await UsuarioService.generate_password_reset_token(db, credential)
        if not result:
            # Por segurança, não informamos se o usuário existe ou não
            return {"message": "Se o usuário existir, um token de recuperação foi enviado para o e-mail e WhatsApp cadastrados"}
            
        # Envia as notificações por e-mail e WhatsApp
        notification_results = await notification_service.send_password_reset_notifications(
            usuario=result["usuario"],
            token=result["token"],
            expira_em=result["expira_em"]
        )
        
        # Log do resultado das notificações
        logger.info(f"Resultado das notificações para {result['usuario']['nome']}: {notification_results}")
        
        # Em ambiente de desenvolvimento, retornamos informações adicionais para testes
        dev_info = {
            "token": result["token"],
            "usuario": result["usuario"],
            "expira_em": result["expira_em"],
            "notificacoes": notification_results
        }
        
        # Retorna uma mensagem genérica por questões de segurança
        return {
            "message": "Um token de recuperação foi enviado para o e-mail e WhatsApp cadastrados",
            "dev_info": dev_info
        }
    except Exception as e:
        logger.error(f"Erro ao solicitar recuperação de senha: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar solicitação: {str(e)}")

@router.post("/validar-token", status_code=status.HTTP_200_OK,
            summary="Validar token de recuperação",
            description="Verifica se um token de recuperação de senha é válido")
async def validate_recovery_token(
    token: str = Body(..., description="Token de recuperação recebido"),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Verifica se o token é válido
        usuario_id = UsuarioService.verify_password_reset_token(token)
        if not usuario_id:
            return {"valid": False, "message": "Token inválido ou expirado"}
            
        # Busca o usuário para ter certeza de que ele existe
        usuario = await UsuarioService.get_by_id(db, usuario_id)
        if not usuario:
            return {"valid": False, "message": "Usuário não encontrado"}
            
        # Token é válido e usuário existe
        return {"valid": True, "usuario_id": usuario_id, "message": "Token válido"}
    except Exception as e:
        logger.error(f"Erro ao validar token: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao validar token: {str(e)}")

@router.post("/redefinir-senha", status_code=status.HTTP_200_OK,
            summary="Redefinir senha com token",
            description="Redefine a senha do usuário usando um token de recuperação válido")
async def reset_password_with_token(
    token: str = Body(..., description="Token de recuperação recebido"),
    nova_senha: str = Body(..., min_length=6, description="Nova senha"),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Verifica se o token é válido
        usuario_id = UsuarioService.verify_password_reset_token(token)
        if not usuario_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Token inválido ou expirado"
            )
            
        # Redefine a senha do usuário
        success = await UsuarioService.reset_password(db, usuario_id, nova_senha)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Usuário não encontrado"
            )
            
        return {"success": True, "message": "Senha redefinida com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao redefinir senha: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao redefinir senha: {str(e)}")
