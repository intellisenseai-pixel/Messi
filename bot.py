import os
import logging
import random
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

# --- Módulo do Servidor Web Falso (para manter o serviço vivo) ---
app = Flask(__name__)
@app.route('/')
def health_check():
    return "Bot is alive and running.", 200

def run_flask_app():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- NÚCLEO ANALÍTICO ARSENAL 2.0 (INTERNALIZADO) ---
def arsenal_core_analysis(prompt: str) -> dict:
    """
    Esta função agora É o Agente ⚽️ Messi.
    Ela simula a análise estatística e retorna um resultado estruturado.
    """
    logger.info(f"Executando análise interna do Arsenal Core para: '{prompt}'")
    
    # Simulação de análise de dados (no futuro, aqui entraria o código real de Poisson, etc.)
    # Para demonstração, vamos gerar resultados aleatórios, mas realistas.
    
    # Extrai nomes de times do prompt (lógica simples)
    try:
        teams = prompt.replace("analise o jogo", "").strip().split(" vs ")
        home_team = teams[0].strip().title()
        away_team = teams[1].strip().title()
        game_title = f"{home_team} vs. {away_team}"
    except Exception:
        game_title = "Jogo não especificado"

    # Geração de dados estatísticos aleatórios
    odd = round(random.uniform(1.5, 4.5), 2)
    real_probability = round(random.uniform(0.25, 0.75), 3)
    expected_value = (odd * real_probability) - 1
    
    # Aplicação dos Critérios Arsenal
    classification = "🔴 Vermelho"
    if expected_value >= 0.0:
        classification = "🟡 Amarelo"
    if expected_value >= 0.10 and real_probability >= 0.40:
        classification = "🟢 Verde"

    return {
        "game": game_title,
        "market": "Vencedor da Partida (1x2)",
        "selection": home_team,
        "odd": odd,
        "real_probability_percent": f"{real_probability * 100:.1f}%",
        "expected_value_percent": f"{expected_value * 100:+.1f}%",
        "classification": classification
    }

# --- Módulo de Formatação de Resposta ---
def format_analysis_card(analysis: dict) -> str:
    """Formata o dicionário de análise no card de resposta."""
    return (
        f"⚽ Jogo: {analysis['game']}\n"
        f"🏷️ Mercado: {analysis['market']}\n"
        f"💎 Seleção: {analysis['selection']}\n\n"
        f"💰 Odd: {analysis['odd']:.2f} | 📈 Prob. Real: {analysis['real_probability_percent']} | 💹 EV: {analysis['expected_value_percent']}\n"
        f"🔰 Classificação Arsenal: {analysis['classification']}"
    )

# --- Handlers do Bot do Telegram ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Agente ⚽️ Messi (v. Autossuficiente) operacional.")

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prompt = update.message.text.replace(f"@{context.bot.username}", "").strip()
    if not prompt:
        await update.message.reply_text("Comando inválido.")
        return
        
    await update.message.reply_text("Solicitação recebida. Executando análise interna...", reply_to_message_id=update.message.message_id)
    
    # Chama o núcleo de análise LOCAL
    analysis_result = arsenal_core_analysis(prompt)
    
    # Formata a resposta
    response_card = format_analysis_card(analysis_result)
    
    await update.message.reply_text(response_card)

# --- Função Principal de Execução ---
def main() -> None:
    logger.info("Iniciando processo principal (v. Autossuficiente)...")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.critical("ERRO CRÍTICO: TELEGRAM_BOT_TOKEN não definido.")
        return

    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    logger.info("Servidor web de saúde iniciado.")

    while True:
        try:
            application = Application.builder().token(token).build()
            application.add_handler(CommandHandler("start", start_command))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Entity("mention"), handle_mention))
            
            logger.info("Bot configurado. Iniciando polling...")
            application.run_polling(allowed_updates=Update.ALL_TYPES)
        except Exception as e:
            logger.error(f"Erro fatal no bot: {e}. Reiniciando em 10s...")
            time.sleep(10)
        logger.warning("Polling parado. Reiniciando loop em 5s...")
        time.sleep(5)

if __name__ == "__main__":
    main()
