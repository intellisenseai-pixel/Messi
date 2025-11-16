import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuração do Logging ---
# Essencial para diagnosticar problemas no ambiente de produção (Render)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# --- Módulo de Comunicação com o Núcleo Analítico (API do Manus) ---
def query_manus_api(prompt: str, chat_id: int) -> str:
    """
    Envia o prompt do usuário para a API real do Manus (⚽️ Messi) e retorna a resposta.
    """
    logger.info(f"Enviando prompt para a API real do Manus: '{prompt}'")

    # Carrega as credenciais da API a partir das variáveis de ambiente no Render
    api_endpoint = os.getenv("MANUS_API_ENDPOINT")
    api_key = os.getenv("MANUS_API_KEY")

    # Validação de segurança: verifica se as credenciais estão configuradas
    if not api_endpoint or not api_key:
        error_message = "Erro Crítico de Configuração: A URL (MANUS_API_ENDPOINT) ou a chave (MANUS_API_KEY) da API do Manus não foram definidas no servidor Render."
        logger.error(error_message)
        return error_message

    # Define os cabeçalhos para a requisição HTTP, incluindo a autenticação
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Monta o corpo da requisição (payload)
    # Usamos o ID do chat do Telegram para manter o contexto da conversa com o Manus
    payload = {
        "prompt": prompt,
        "conversation_id": f"telegram_{chat_id}"
    }

    try:
        # Executa a chamada POST para a API, com um timeout de 60 segundos
        response = requests.post(api_endpoint, headers=headers, json=payload, timeout=60)
        
        # Lança uma exceção se a API retornar um código de erro (4xx ou 5xx)
        response.raise_for_status()
        
        # Extrai a resposta do JSON retornado pela API
        # O .get() previne erros caso a chave "response" não exista
        return response.json().get("response", "Resposta da API recebida, mas em formato inesperado.")

    except requests.exceptions.RequestException as e:
        # Captura qualquer erro de rede ou de comunicação com a API
        logger.error(f"Erro de comunicação com a API do Manus: {e}")
        return f"Falha na comunicação com o núcleo analítico. A conexão não pôde ser estabelecida. Detalhes técnicos: {e}"


# --- Handlers do Bot do Telegram ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para o comando /start. Envia uma mensagem de boas-vindas.
    """
    user_name = update.message.from_user.first_name
    await update.message.reply_text(
        f"Olá, {user_name}.\n\n"
        "Agente Analítico Arsenal 2.0 (⚽️ Messi) operacional.\n"
        "Para solicitar uma análise, mencione-me em uma mensagem. Ex: `@MeuBot analise o jogo X vs Y`."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para o comando /help. Fornece instruções de uso.
    """
    bot_username = f"@{context.bot.username}"
    await update.message.reply_text(
        "**Instruções de Uso - Agente ⚽️ Messi**\n\n"
        "1.  **Análise de Jogo:**\n"
        f"`{bot_username} analise [nome do jogo]`\n\n"
        "2.  **Análise de Imagem:**\n"
        f"Envie uma imagem com jogos e comente: `{bot_username} analise a imagem`\n\n"
        "3.  **Status do Sistema:**\n"
        "`/status` - Verifica a conexão com o núcleo analítico."
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para o comando /status. Verifica a conexão com a API do Manus.
    """
    await update.message.reply_text("Verificando status do sistema...")
    response = query_manus_api("Ping", update.message.chat_id)
    await update.message.reply_text(f"**Status do Núcleo Analítico:**\n{response}")


async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler principal que processa mensagens que mencionam o bot.
    """
    # Extrai o texto da mensagem e o nome de usuário do bot
    message_text = update.message.text
    bot_username = f"@{context.bot.username}"
    
    # Limpa o prompt, removendo a menção ao bot
    prompt = message_text.replace(bot_username, "").strip()

    # Valida se o prompt não está vazio
    if not prompt:
        await update.message.reply_text("Comando inválido. Forneça uma instrução após me mencionar. Use /help para ver os comandos.")
        return

    # Envia uma confirmação imediata para o usuário
    await update.message.reply_text("Solicitação recebida. Conectando ao núcleo analítico...", reply_to_message_id=update.message.message_id)

    # Chama a função que se comunica com a API real
    response = query_manus_api(prompt, update.message.chat_id)
    
    # Envia a resposta final da análise para o grupo
    await update.message.reply_text(response)


# --- Função Principal de Execução ---

def main() -> None:
    """
    Função principal que configura e inicia o bot do Telegram.
    """
    logger.info("Iniciando o bot...")

    # Carrega o token do bot do Telegram a partir das variáveis de ambiente
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.critical("ERRO CRÍTICO: A variável de ambiente TELEGRAM_BOT_TOKEN não foi definida.")
        return

    # Cria o objeto da aplicação do bot
    application = Application.builder().token(token).build()

    # Registra os handlers de comando
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    
    # Registra o handler de menções, que é o principal gatilho para análises
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.Entity("mention"), 
        handle_mention
    ))

    # Inicia o bot em modo "polling" (verificação contínua de novas mensagens)
    logger.info("Bot configurado. Iniciando o polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

