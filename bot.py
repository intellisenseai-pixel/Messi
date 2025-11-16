import os
import logging
import requests
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuração do Logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Módulo do Servidor Web Falso (para satisfazer o Render) ---
# Este servidor web não faz nada além de manter uma porta aberta.
app = Flask(__name__)

@app.route('/')
def health_check():
    """Endpoint que o Render pode verificar para saber que o serviço está vivo."""
    return "Bot is alive and running.", 200

def run_flask_app():
    """Função para rodar o servidor Flask em uma porta definida pelo Render."""
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- Módulo de Comunicação com o Núcleo Analítico (API do Manus) ---
def query_manus_api(prompt: str, chat_id: int) -> str:
    logger.info(f"Enviando prompt para a API real do Manus: '{prompt}'")
    api_endpoint = os.getenv("MANUS_API_ENDPOINT")
    api_key = os.getenv("MANUS_API_KEY")

    if not api_endpoint or not api_key:
        error_message = "Erro Crítico de Configuração: A URL ou a chave da API do Manus não foram definidas no servidor."
        logger.error(error_message)
        return error_message

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "conversation_id": f"telegram_{chat_id}"}

    try:
        response = requests.post(api_endpoint, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "Resposta da API em formato inesperado.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de comunicação com a API do Manus: {e}")
        return f"Falha na comunicação com o núcleo analítico. Detalhes: {e}"

# --- Handlers do Bot do Telegram ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.message.from_user.first_name
    await update.message.reply_text(f"Olá, {user_name}. Agente ⚽️ Messi operacional. Mencione-me para uma análise.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot_username = f"@{context.bot.username}"
    await update.message.reply_text(f"**Comandos:**\n- `{bot_username} [sua pergunta]`\n- `/status` para verificar a conexão.")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Verificando status...")
    response = query_manus_api("Ping", update.message.chat_id)
    await update.message.reply_text(f"**Status do Núcleo:**\n{response}")

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prompt = update.message.text.replace(f"@{context.bot.username}", "").strip()
    if not prompt:
        await update.message.reply_text("Comando inválido. Use /help para ver os comandos.")
        return
    await update.message.reply_text("Solicitação recebida...", reply_to_message_id=update.message.message_id)
    response = query_manus_api(prompt, update.message.chat_id)
    await update.message.reply_text(response)

# --- Função Principal de Execução ---
def main() -> None:
    logger.info("Iniciando o bot...")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.critical("ERRO CRÍTICO: TELEGRAM_BOT_TOKEN não definido.")
        return

    # Inicia o servidor Flask em uma thread separada
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    logger.info("Servidor web falso iniciado em segundo plano.")

    # Configura e inicia o bot do Telegram
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Entity("mention"), handle_mention))
    
    logger.info("Bot configurado. Iniciando o polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
