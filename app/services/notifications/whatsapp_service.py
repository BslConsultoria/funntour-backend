import logging
import requests
from typing import Dict, Optional, Any
from app.config.email_config import WHATSAPP_API_KEY, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_SENDER_NUMBER

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self, api_key: str = None, phone_number_id: str = None, sender_number: str = None):
        # Usando as configurau00e7u00f5es do arquivo de config, que pode ser sobrescrito por variu00e1veis de ambiente
        self.api_key = api_key or WHATSAPP_API_KEY
        self.phone_number_id = phone_number_id or WHATSAPP_PHONE_NUMBER_ID
        self.sender_number = sender_number or WHATSAPP_SENDER_NUMBER
        self.api_version = "v16.0"  # Versu00e3o da API do WhatsApp Business
        self.api_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"
    
    def send_whatsapp_message(self, to_phone_number: str, message_content: str) -> bool:
        """
        Envia uma mensagem de WhatsApp para o nu00famero especificado.
        
        Args:
            to_phone_number: Nu00famero de telefone do destinatu00e1rio (formato internacional sem + ou espau00e7os)
            message_content: Conteu00fado da mensagem
            
        Returns:
            bool: True se o envio foi bem-sucedido, False caso contru00e1rio
        """
        try:
            # Formata o nu00famero de telefone (remove caracteres nu00e3o numu00e9ricos)
            formatted_number = ''.join(filter(str.isdigit, to_phone_number))
            
            # Se o nu00famero nu00e3o comeu00e7ar com o cu00f3digo do pau00eds, adiciona o cu00f3digo do Brasil
            if not formatted_number.startswith('55'):
                formatted_number = f"55{formatted_number}"
            
            # Payload da mensagem
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": formatted_number,
                "type": "text",
                "text": {"body": message_content}
            }
            
            # Cabeu00e7alhos da requisiu00e7u00e3o
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Em ambiente de desenvolvimento, apenas logamos a mensagem
            if self.api_key == "seu-token-api-whatsapp":
                logger.info(f"[DEV] Mensagem WhatsApp seria enviada para {formatted_number}: {message_content}")
                return True
            
            # Faz a requisiu00e7u00e3o para a API do WhatsApp
            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()  # Lanu00e7a exceu00e7u00e3o para erros HTTP
            
            logger.info(f"Mensagem WhatsApp enviada com sucesso para {formatted_number}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem WhatsApp para {to_phone_number}: {e}")
            return False
    
    def get_password_reset_whatsapp_template(self, usuario_nome: str, token: str) -> str:
        """
        Gera o template de mensagem WhatsApp para recuperau00e7u00e3o de senha.
        
        Args:
            usuario_nome: Nome do usuu00e1rio
            token: Token de recuperau00e7u00e3o
            
        Returns:
            str: Texto formatado da mensagem
        """
        message = f"""*Funntour - Recuperau00e7u00e3o de Senha*

Olu00e1 {usuario_nome},

Recebemos uma solicitau00e7u00e3o para redefinir sua senha na plataforma Funntour.

Seu cu00f3digo de verificau00e7u00e3o u00e9: *{token}*

Este cu00f3digo u00e9 vu00e1lido por 10 minutos.

Se vocu00ea nu00e3o solicitou essa redefiniu00e7u00e3o, por favor ignore esta mensagem.

Atenciosamente,
Equipe Funntour"""
        
        return message
