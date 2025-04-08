import logging
from typing import Dict, Optional, Any
from .email_service import EmailService
from .whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.email_service = EmailService()
        self.whatsapp_service = WhatsAppService()
        
    async def send_password_reset_notifications(self, usuario: Dict[str, Any], token: str, expira_em: str) -> Dict[str, bool]:
        """
        Envia notificações de recuperação de senha por e-mail e WhatsApp.
        
        Args:
            usuario: Dicionário com dados do usuário (id, nome, email, whatsapp, cpf_cnpj)
            token: Token de recuperação
            expira_em: Data/hora de expiração do token
            
        Returns:
            Dict[str, bool]: Status de envio para cada canal
        """
        results = {"email": False, "whatsapp": False}
        
        # Envia o e-mail de recuperação de senha
        if usuario.get("email"):
            try:
                # Pega os templates de e-mail
                templates = self.email_service.get_password_reset_email_template(
                    usuario_nome=usuario["nome"], 
                    token=token,
                    expira_em=expira_em
                )
                
                # Envia o e-mail
                results["email"] = self.email_service.send_email(
                    recipient=usuario["email"],
                    subject="Funntour - Recuperação de Senha",
                    html_content=templates["html"],
                    text_content=templates["text"]
                )
                
                if results["email"]:
                    logger.info(f"E-mail de recuperação de senha enviado para {usuario['email']}")
                else:
                    logger.error(f"Falha ao enviar e-mail de recuperação de senha para {usuario['email']}")
            except Exception as e:
                logger.error(f"Erro ao processar envio de e-mail: {e}")
        
        # Envia a mensagem de WhatsApp para recuperação de senha
        if usuario.get("whatsapp"):
            try:
                # Pega o template de mensagem do WhatsApp
                message = self.whatsapp_service.get_password_reset_whatsapp_template(
                    usuario_nome=usuario["nome"],
                    token=token
                )
                
                # Envia a mensagem do WhatsApp
                results["whatsapp"] = self.whatsapp_service.send_whatsapp_message(
                    to_phone_number=usuario["whatsapp"],
                    message_content=message
                )
                
                if results["whatsapp"]:
                    logger.info(f"Mensagem WhatsApp de recuperação de senha enviada para {usuario['whatsapp']}")
                else:
                    logger.error(f"Falha ao enviar mensagem WhatsApp de recuperação de senha para {usuario['whatsapp']}")
            except Exception as e:
                logger.error(f"Erro ao processar envio de WhatsApp: {e}")
                
        return results
