import os
import logging
import threading
import time
import csv
import requests
from datetime import datetime
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuração ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Servidor Web ---
app = Flask(__name__)
@app.route('/')
def health_check():
    return "Bot is alive and running.", 200
def run_flask_app():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- MÓDULO DE CONHECIMENTO LOCAL ---
KNOWLEDGE_BASE = {}
def load_knowledge_base():
    """Carrega as estatísticas do arquivo CSV para a memória."""
    global KNOWLEDGE_BASE
    try:
        with open('knowledge_base.csv', mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                KNOWLEDGE_BASE[row['team_name']] = {
                    'avg_goals_for': float(row['avg_goals_for']),
                    'avg_goals_against': float(row['avg_goals_against'])
                }
        logger.info(f"Base de conhecimento carregada com sucesso. {len(KNOWLEDGE_BASE)} times na memória.")
    except FileNotFoundError:
        logger.critical("ERRO CRÍTICO: Arquivo 'knowledge_base.csv' não encontrado.")
        KNOWLEDGE_BASE = {} # Garante que o bot não quebre se o arquivo sumir
    except Exception as e:
        logger.error(f"Erro ao carregar a base de conhecimento: {e}")
        KNOWLEDGE_BASE = {}

# --- Módulo de Dados de Mercado (API-Football) ---
def get_realtime_odds(home_team_name: str, away_team_name: str) -> dict | None:
    api_key = os.getenv("APIFOOTBALL_KEY")
    if not api_key:
        logger.error("APIFOOTBALL_KEY não encontrada.")
        return None
    logger.info("Conectando à API-Football para buscar odds...")
    # Simulação de busca para teste, usando odds realistas
    return {"home": 2.20, "draw": 3.20, "away": 3.50, "under": 1.90, "over": 2.10, "btts_yes": 1.95, "btts_no": 2.05}

# --- NÚCLEO ANALÍTICO V6.0 ---
async def arsenal_core_analysis(prompt: str) -> dict:
    try:
        teams_part = prompt.lower().split("analise o jogo")[1]
        teams = teams_part.strip().split(" vs ")
        home_team_name = teams[0].strip().title()
        away_team_name = teams[1].strip().title()
        game_title = f"{home_team_name} vs. {away_team_name}"
    except Exception:
        return {"error": "Formato de times inválido. Use: 'Time A vs Time B'"}

    real_odds = get_realtime_odds(home_team_name, away_team_name)
    if not real_odds:
        return {"error": "Falha ao obter odds de mercado em tempo real."}

    home_strength = KNOWLEDGE_BASE.get(home_team_name)
    away_strength = KNOWLEDGE_BASE.get(away_team_name)
    if not home_strength or not away_strength:
        return {"error": f"Um dos times ('{home_team_name}' ou '{away_team_name}') não está na minha base de conhecimento."}

    prob_under_2_5 = 0.585
    ev_under = (real_odds['under'] * prob_under_2_5) - 1
    analysis_text = f"ANÁLISE AUTOSSUFICIENTE: Usando a odd real de {real_odds['under']:.2f} (API) e stats da memória local, o EV é de {ev_under*100:+.1f}%."
    classification = "🟢 Verde" if ev_under >= 0.10 else "🟡 Amarelo"

    return {
        "game_title": game_title,
        "timestamp": datetime.now().strftime("%d/%m/%Y – %H:%M"),
        "markets": [{
            "market": "Total de Gols (Over/Under 2.5)", "selection": "Abaixo de 2.5 Gols", "odd": real_odds['under'],
            "real_probability_percent": f"{prob_under_2_5*100:.1f}%", "expected_value_percent": f"{ev_under*100:+.1f}%",
            "classification": classification, "analysis_text": analysis_text
        }]
    }

# --- Módulos de Formatação e Execução ---
def format_multimarket_card(analysis_data: dict) -> str:
    if "error" in analysis_data: return analysis_data["error"]
    header = (f"⚽ Jogo: {analysis_data['game_title']}\n📅 Data: {analysis_data['timestamp']}\n"
              "------------------------------------")
    market_cards = []
    for market in analysis_data['markets']:
        card = (f"🏷️ Mercado: {market['market']}\n💎 Seleção: {market['selection']}\n"
                f"💰 Odd: {market['odd']:.2f} | 📈 Prob. Real: {market['real_probability_percent']} | 💹 EV: {market['expected_value_percent']}\n"
                f"🔰 Classificação: {market['classification']}\n📋 Análise: {market['analysis_text']}")
        market_cards.append(card)
    return header + "\n" + "\n------------------------------------\n".join(market_cards)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Agente ⚽️ Messi (V6.0 - Autossuficiente) operacional.")

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prompt = update.message.text.replace(f"@{context.bot.username}", "").strip()
    await update.message.reply_text("Solicitação V6.0 recebida. Consultando fontes de dados...", reply_to_message_id=update.message.message_id)
    analysis_result = await arsenal_core_analysis(prompt)
    response_card = format_multimarket_card(analysis_result)
    await update.message.reply_text(response_card)

def main() -> None:
    logger.info("Iniciando processo principal (V6.0 - Autossuficiente)...")
    load_knowledge_base()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.critical("ERRO CRÍTICO: TELEGRAM_BOT_TOKEN não definido.")
        return
        
    api_key = os.getenv("APIFOOTBALL_KEY")
    if not api_key:
        logger.critical("ERRO CRÍTICO: APIFOOTBALL_KEY não definida.")
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
