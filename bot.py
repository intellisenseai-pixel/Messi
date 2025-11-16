import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuração de logging para diagnóstico no servidor
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- SIMULAÇÃO DA API DO MANUS (⚽️ Messi) ---
# No futuro, esta função fará uma chamada HTTP real para a API do Manus.
def query_manus_api(prompt: str) -> str:
    """
    Função mock que simula a resposta do agente ⚽️ Messi.
    """
    logger.info(f"Simulando chamada à API do Manus com o prompt: '{prompt}'")
    # Lógica de simulação baseada no contexto da "sala de guerra"
    if "analise o jogo" in prompt.lower():
        return (
            "Análise recebida. Processando dados...\n\n"
            "⚽ Jogo: Exemplo FC vs. Rival AC\n"
            "📅 Data: 16/11/2025 – 17:00\n"
            "🏷️ Mercado: Vencedor da Partida (1x2)\n"
            "💎 Seleção: Exemplo FC\n"
            "💰 Odd: 2.10 | 📈 Probabilidade Real: 52.0% | 💹 Valor Esperado (EV): +9.2%\n"
            "🔰 Classificação Arsenal: 🟡 Amarelo"
        )
    return f"Comando '{prompt}' recebido. Aguardando dados para análise completa."
# --- FIM DA SIMULAÇÃO ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia uma mensagem de boas-vindas quando o comando /start é emitido."""
    await update.message.reply_text(
        "Agente Analítico Arsenal 2.0 (⚽️ Messi) operacional. "
        "Mencione-me em uma mensagem para solicitar uma análise."
    )

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processa mensagens que mencionam o bot."""
    message_text = update.message.text
    bot_username = f"@{context.bot.username}"
    
    # Remove a menção do bot do texto da mensagem para obter o prompt limpo
    prompt = message_text.replace(bot_username, "").strip()

    if not prompt:
        await update.message.reply_text("Comando inválido. Por favor, forneça uma instrução após me mencionar.")
        return

    # Envia uma confirmação imediata
    await update.message.reply_text("Solicitação recebida. Conectando ao núcleo analítico...", reply_to_message_id=update.message.message_id)

    # Chama a função que consulta a API do Manus
    response = query_manus_api(prompt)
    
    # Envia a resposta final da análise
    await update.message.reply_text(response)

def main() -> None:
    """Inicia e executa o bot."""
    # Carrega o token do ambiente do servidor
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("Erro Crítico: A variável de ambiente TELEGRAM_BOT_TOKEN não foi definida.")
        return

    # Cria a aplicação do bot
    application = Application.builder().token(token).build()

    # Adiciona os handlers de comando
    application.add_handler(CommandHandler("start", start))
    
    # Adiciona o handler para menções
    # O bot só responderá a mensagens de texto que o mencionem diretamente
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.Entity("mention"), 
        handle_mention
    ))

    # Inicia o bot em modo polling (verificando constantemente por novas mensagens)
    logger.info("Iniciando o bot em modo polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
