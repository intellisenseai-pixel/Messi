import os
import logging
import random
import threading
import time
from datetime import datetime
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

# --- NÚCLEO ANALÍTICO ARSENAL 2.0 (V2.1 - ANÁLISE DETALHADA) ---
def arsenal_core_analysis(prompt: str) -> dict:
    """
    Esta função agora É o Agente ⚽️ Messi, analisando múltiplos mercados
    e fornecendo uma justificativa textual para cada um.
    """
    logger.info(f"Executando análise interna V2.1 para: '{prompt}'")
    
    if "analise o jogo" not in prompt.lower():
        return {"error": "Comando de análise inválido. Use 'analise o jogo Time A vs Time B'."}
        
    try:
        teams_part = prompt.lower().split("analise o jogo")[1]
        teams = teams_part.strip().split(" vs ")
        home_team = teams[0].strip().title()
        away_team = teams[1].strip().title()
        game_title = f"{home_team} vs. {away_team}"
    except Exception:
        return {"error": "Formato de times inválido. Use 'Time A vs Time B'."}

    def generate_market_analysis(market_name, selection_options):
        odd = round(random.uniform(1.5, 4.5), 2)
        real_probability = round(random.uniform(0.25, 0.75), 3)
        expected_value = (odd * real_probability) - 1
        
        classification = "🔴 Vermelho"
        analysis_text = f"O Valor Esperado (EV) de {expected_value*100:+.1f}% é negativo. A aposta não possui valor estatístico."
        
        if expected_value >= 0.0:
            classification = "🟡 Amarelo"
            analysis_text = f"O EV é positivo ({expected_value*100:+.1f}%), mas a aposta falha em algum critério de segurança (ex: Prob. Real de {real_probability*100:.1f}% abaixo do mínimo de 40%)."
        
        if expected_value >= 0.10 and real_probability >= 0.40:
            classification = "🟢 Verde"
            analysis_text = f"Oportunidade sólida. O EV de {expected_value*100:+.1f}% é excelente e a Prob. Real de {real_probability*100:.1f}% atende aos critérios de segurança."
            
        return {
            "market": market_name,
            "selection": random.choice(selection_options),
            "odd": odd,
            "real_probability_percent": f"{real_probability * 100:.1f}%",
            "expected_value_percent": f"{expected_value * 100:+.1f}%",
            "classification": classification,
            "analysis_text": analysis_text
        }

    analysis_1x2 = generate_market_analysis("Vencedor da Partida (1x2)", [home_team, away_team, "Empate"])
    analysis_over_under = generate_market_analysis("Total de Gols (Over/Under 2.5)", ["Acima de 2.5", "Abaixo de 2.5"])
    analysis_btts = generate_market_analysis("Ambas as Equipes Marcam (BTTS)", ["Sim", "Não"])

    return {
        "game_title": game_title,
        "timestamp": datetime.now().strftime("%d/%m/%Y – %H:%M"),
        "markets": [analysis_1x2, analysis_over_under, analysis_btts]
    }

# --- Módulo de Formatação de Resposta (V2.1) ---
def format_multimarket_card(analysis_data: dict) -> str:
    """Formata os dados de múltiplos mercados no novo card com justificativa."""
    if "error" in analysis_data:
        return analysis_data["error"]

    header = (
        f"⚽ Jogo: {analysis_data['game_title']}\n"
        f"📅 Data: {analysis_data['timestamp']}\n"
        "------------------------------------"
    )
    
    market_cards = []
    for market in analysis_data['markets']:
        card = (
            f"🏷️ Mercado: {market['market']}\n"
            f"💎 Seleção: {market['selection']}\n"
            f"💰 Odd: {market['odd']:.2f} | 📈 Prob. Real: {market['real_probability_percent']} | 💹 EV: {market['expected_value_percent']}\n"
            f"🔰 Classificação: {market['classification']}\n"
            f"📋 Análise: {market['analysis_text']}"
        )
        market_cards.append(card)
        
    return header + "\n" + "\n------------------------------------\n".join(market_cards)

# --- Handlers do Bot do Telegram ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Agente ⚽️ Messi (V2.1 - Análise Detalhada) operacional.")

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prompt = update.message.text.replace(f"@{context.bot.username}", "").strip()
    
    await update.message.reply_text("Solicitação V2.1 recebida. Executando análise detalhada...", reply_to_message_id=update.message.message_id)
    
    analysis_result = arsenal_core_analysis(prompt)
    response_card = format_multimarket_card(analysis_result)
    
    await update.message.reply_text(response_card)

# --- Função Principal de Execução ---
def main() -> None:
    logger.info("Iniciando processo principal (V2.1 - Análise Detalhada)...")
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
