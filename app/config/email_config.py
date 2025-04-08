# Configurações para envio de e-mail
# Em produção, estes valores devem vir de variáveis de ambiente

import os
from dotenv import load_dotenv

# Tenta carregar variáveis de .env, se existir
load_dotenv()

# Configurações de SMTP
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "funntour.df@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", '"pF>-5B3p{$(x\'k]')
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "funntour.df@gmail.com")

# Configurações de WhatsApp
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY", "seu-token-api-whatsapp")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "seu-phone-number-id")
WHATSAPP_SENDER_NUMBER = os.getenv("WHATSAPP_SENDER_NUMBER", "5561992784283")
