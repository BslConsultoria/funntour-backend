import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from app.config.email_config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SENDER_EMAIL

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, smtp_server: str = None, smtp_port: int = None, 
                 smtp_username: str = None, smtp_password: str = None, 
                 sender_email: str = None):
        # Usando as configurau00e7u00f5es do arquivo de config, que pode ser sobrescrito por varu00e1veis de ambiente
        self.smtp_server = smtp_server or SMTP_SERVER
        self.smtp_port = smtp_port or SMTP_PORT
        self.smtp_username = smtp_username or SMTP_USERNAME
        self.smtp_password = smtp_password or SMTP_PASSWORD
        self.sender_email = sender_email or SENDER_EMAIL

    def send_email(self, recipient: str, subject: str, html_content: str, 
                  text_content: Optional[str] = None) -> bool:
        """
        Envia um email para o destinatário especificado.
        
        Args:
            recipient: Email do destinatário
            subject: Assunto do email
            html_content: Conteúdo HTML do email
            text_content: Conteúdo em texto simples (opcional)
            
        Returns:
            bool: True se o envio foi bem-sucedido, False caso contrário
        """
        try:
            # Criando a mensagem
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient
            
            # Versão em texto simples - fallback
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            # Versão HTML - principal
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Conectando ao servidor SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(
                    self.sender_email, recipient, message.as_string()
                )
                
            logger.info(f"Email enviado com sucesso para {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email para {recipient}: {e}")
            return False

    def get_password_reset_email_template(self, usuario_nome: str, token: str, expira_em: str) -> Dict[str, str]:
        """
        Gera o template de e-mail para recuperação de senha.
        
        Args:
            usuario_nome: Nome do usuário
            token: Token de recuperação
            expira_em: Data/hora de expiração
            
        Returns:
            Dict: Com as versões HTML e texto do email
        """
        # Versão em texto simples
        text_content = f"""Olá {usuario_nome},

Recebemos uma solicitação para redefinir sua senha na plataforma Funntour.

Seu código de verificação é: {token}

Este código é válido até {expira_em}.

Se você não solicitou a redefinição de senha, por favor ignore este e-mail.

Atenciosamente,
Equipe Funntour
"""
        
        # Versão em HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Recuperação de Senha - Funntour</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #3498db; color: white; padding: 10px; text-align: center; }}
                .content {{ padding: 20px; border: 1px solid #ddd; }}
                .token {{ font-size: 24px; font-weight: bold; text-align: center; padding: 15px; 
                          background-color: #f8f9fa; margin: 20px 0; letter-spacing: 5px; }}
                .footer {{ text-align: center; font-size: 12px; color: #777; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Recuperação de Senha</h1>
                </div>
                <div class="content">
                    <p>Olá <strong>{usuario_nome}</strong>,</p>
                    <p>Recebemos uma solicitação para redefinir sua senha na plataforma Funntour.</p>
                    <p>Seu código de verificação é:</p>
                    <div class="token">{token}</div>
                    <p>Este código é válido até <strong>{expira_em}</strong>.</p>
                    <p>Se você não solicitou a redefinição de senha, por favor ignore este e-mail.</p>
                    <p>Atenciosamente,<br>Equipe Funntour</p>
                </div>
                <div class="footer">
                    <p>© 2025 Funntour. Todos os direitos reservados.</p>
                    <p>Este é um e-mail automático, não responda a esta mensagem.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return {
            "html": html_content,
            "text": text_content
        }
