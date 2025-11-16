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

# --- NÚCLEO ANALÍTICO ARSENAL 2.0 (V2.2 - DOUTRINA ARSENAL) ---
def arsenal_core_analysis(prompt: str) -> dict:
    """
    Esta função implementa a Doutrina Arsenal, com critérios rigorosos de EV
    e diferença de probabilidade.
    """
    logger.info(f"Executando análise interna V2.2 (Doutrina Arsenal) para: '{prompt}'")
    
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
        # --- Simulação de Dados ---
        odd = round(random.uniform(1.5, 4.5), 2)
        real_probability = round(random.uniform(0.25, 0.75), 3)
        
        # --- Cálculos da Doutrina Arsenal ---
        implied_probability = 1 / odd
        expected_value = (odd * real_probability) - 1
        prob_difference = real_probability - implied_probability

        # --- Aplicação dos Critérios Rigorosos ---
        classification = "🔴 Vermelho"
        analysis_text = f"EV Negativo ({expected_value*100:+.1f}%). A aposta é matematicamente perdedora a longo prazo e foi descartada."

        if expected_value > 0.0 and expected_value < 0.10:
            classification = "🟡 Amarelo"
            analysis_text = f"EV positivo, mas abaixo do nosso padrão de +10%. A vantagem de {expected_value*100:+.1f}% é marginal e de maior risco."
        
        # O critério para Verde agora é mais rigoroso
        if expected_value >= 0.10 and prob_difference >= 0.05:
            classification = "🟢 Verde"
            analysis_text = (f"Oportunidade sólida. O EV de {expected_value*100:+.1f}% e a diferença de probabilidade de "
                             f"{prob_difference*100:+.1f} pontos atendem aos rigorosos critérios Arsenal.")
        elif expected_value >= 0.10 and prob_difference < 0.05:
            # Caso especial: EV alto, mas a diferença de probabilidade não é grande o suficiente
            classification = "🟡 Amarelo"
            analysis_text = (f"O EV de {expected_value*100:+.1f}% é alto, mas a diferença entre nossa análise e o mercado "
                             f"({prob_difference*100:+.1f} pontos) não atinge o mínimo de 5 pontos para garantir uma vantagem fundamental.")

        return {
            "market": market_name,
            "selection": random.choice(selection_options),
            "odd": odd,
            "real_probability_percent": f"{real_probability * 100:.1f}%",
            "expected_value_percent": f"{expected_value * 100:+.1f}%",
            "classification": classification,
            "analysis_text": analysis_text
        }

    # --- Geração dos Cards ---
    analysis_1x2 = generate_market_analysis("Vencedor da Partida (1x2)", [home_team, away_team, "Empate"])
    analysis_over_under = generate_market_analysis("Total de Gols (Over/Under 2.5)", ["Acima de 2.5", "Abaixo de 2.5"])
    analysis_btts = generate_market_analysis("Ambas as Equipes Marcam (BTTS)", ["Sim", "Não"])

    return {
        "game_title": game_title,
        "timestamp": datetime.now().strftime("%d/%m/%Y – %H:%M"),
        "markets": [analysis_1x2, analysis_over_under, analysis_btts]
    }

# --- Módulo de Formatação de Resposta (sem alterações) ---
def format_multimarket_card(analysis_data: dict) -> str:
    if "error" in analysis_data:
        return analysis_data["error"]
    header = (f"⚽ Jogo: {analysis_data['game_title']}\n📅 Data: {analysis_data['timestamp']}\n"
              "------------------------------------")
    market_cards = []
    for market in analysis_data['markets']:
        card = (f"🏷️ Mercado: {market['market']}\n💎 Seleção: {market['selection']}\n"
                f"💰 Odd: {market['odd']:.2f} | 📈 Prob. Real: {market['real_probability_percent']} | 💹 EV: {market['expected_value_percent']}\n"
                f"🔰 Classificação: {market['classification']}\n📋 Análise: {market['analysis_text']}")
        market_cards.append(card)
    return header + "\n" + "\n------------------------------------\n".join(market_cards)

# --- Handlers e Função Principal (sem alterações, apenas a mensagem de início) ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Agente ⚽️ Messi (V2.2 - Doutrina Arsenal) operacional.")

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prompt = update.message.text.replace(f"@{context.bot.username}", "").strip()
    await update.message.reply_text("Solicitação V2.2 recebida. Aplicando Doutrina Arsenal...", reply_to_message_id=update.message.message_id)
    analysis_result = arsenal_core_analysis(prompt)
    response_card = format_multimarket_card(analysis_result)
    await update.message.reply_text(response_card)

def main() -> None:
    logger.info("Iniciando processo principal (V2.2 - Doutrina Arsenal)...")
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
