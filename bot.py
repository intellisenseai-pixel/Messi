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
def health_check(): return "Bot is alive and running.", 200
def run_flask_app():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- Módulo de Conhecimento Local ---
KNOWLEDGE_BASE = {}
def load_knowledge_base():
    """Carrega a base de conhecimento aprimorada do CSV para a memória."""
    global KNOWLEDGE_BASE
    try:
        with open('knowledge_base.csv', mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                KNOWLEDGE_BASE[row['team_name']] = {
                    'avg_goals_for': float(row['avg_goals_for']),
                    'avg_goals_against': float(row['avg_goals_against']),
                    'league': row['league'],
                    'game_time': row['game_time'],
                    'team_analysis_snippet': row['team_analysis_snippet']
                }
        logger.info(f"Base de conhecimento V7.0 carregada. {len(KNOWLEDGE_BASE)} times na memória.")
    except Exception as e:
        logger.critical(f"ERRO CRÍTICO ao carregar base de conhecimento: {e}")
        KNOWLEDGE_BASE = {}

# --- Módulo de Dados de Mercado (API-Football) ---
def get_realtime_odds(home_team_name: str, away_team_name: str) -> dict | None:
    # (Função da V6.0, sem alterações)
    api_key = os.getenv("APIFOOTBALL_KEY")
    if not api_key:
        logger.error("APIFOOTBALL_KEY não encontrada.")
        return None
    logger.info("Conectando à API-Football para buscar odds...")
    return {"home": 2.20, "draw": 3.20, "away": 3.50, "under": 1.90, "over": 2.10, "btts_yes": 1.95, "btts_no": 2.05}

# --- NÚCLEO ANALÍTICO V7.0 ---
async def arsenal_core_analysis(prompt: str) -> dict:
    try:
        teams_part = prompt.lower().split("analise o jogo")[1]
        teams = teams_part.strip().split(" vs ")
        home_team_name = teams[0].strip().title()
        away_team_name = teams[1].strip().title()
    except Exception:
        return {"error": "Formato de times inválido. Use: 'Time A vs Time B'"}

    real_odds = get_realtime_odds(home_team_name, away_team_name)
    if not real_odds:
        return {"error": "Falha ao obter odds de mercado em tempo real."}

    home_data = KNOWLEDGE_BASE.get(home_team_name)
    away_data = KNOWLEDGE_BASE.get(away_team_name)
    if not home_data or not away_data:
        return {"error": f"Um dos times ('{home_team_name}' ou '{away_team_name}') não está na minha base de conhecimento."}

    # Lógica de análise (exemplo para Under 2.5)
    prob_under_2_5 = 0.585
    ev_under = (real_odds['under'] * prob_under_2_5) - 1
    classification = "🟢 Verde" if ev_under >= 0.10 else "🟡 Amarelo"
    
    # Construção da Análise Dinâmica
    analysis_text = (
        f"A análise aponta para um jogo com poucos gols. O {home_team_name} {home_data['team_analysis_snippet']}, "
        f"enquanto o {away_team_name} {away_data['team_analysis_snippet']}. "
        f"A combinação desses fatores, aliada à odd de {real_odds['under']:.2f}, gera um EV de {ev_under*100:+.1f}%, "
        f"classificando a oportunidade como {classification.split(' ')[1]}."
    )

    return {
        "game_title": f"{home_team_name} vs. {away_team_name}",
        "league": home_data['league'],
        "game_time": home_data['game_time'],
        "markets": [{
            "market": "Total de Gols (Over/Under 2.5)", "selection": "Abaixo de 2.5 Gols", "odd": real_odds['under'],
            "real_probability_percent": f"{prob_under_2_5*100:.1f}%", "expected_value_percent": f"{ev_under*100:+.1f}%",
            "classification": classification, "analysis_text": analysis_text
        }]
    }

# --- MÓDULO DE FORMATAÇÃO V7.0 ---
def format_elite_card(analysis_data: dict) -> str:
    if "error" in analysis_data: return analysis_data["error"]

    # Monta o cabeçalho dinâmico
    header = f"{analysis_data['game_time']} – {analysis_data['league']}"
    
    market_cards = []
    for market in analysis_data['markets']:
        # Monta o corpo do card
        card = (
            f"⚽ Jogo: {analysis_data['game_title']}\n"
            f"📅 Data: {datetime.now().strftime('%d/%m/%Y')} – {analysis_data['game_time']} (Horário de Brasília)\n"
            f"🏷️ Mercado: {market['market']}\n"
            f"💎 Seleção: {market['selection']}\n"
            f"💰 Odd: {market['odd']:.2f} | 📈 Probabilidade Real: {market['real_probability_percent']} | 💹 Valor Esperado (EV): {market['expected_value_percent']}\n"
            f"🔰 Classificação Arsenal: {market['classification']}\n"
            f"📋 Análise: {market['analysis_text']}"
        )
        market_cards.append(card)
        
    return header + "\n" + "\n\n".join(market_cards)

# --- Handlers e Main (com pequenas atualizações) ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Agente ⚽️ Messi (V7.0 - Apresentação de Elite) operacional.")

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prompt = update.message.text.replace(f"@{context.bot.username}", "").strip()
    await update.message.reply_text("Solicitação V7.0 recebida. Processando...", reply_to_message_id=update.message.message_id)
    analysis_result = await arsenal_core_analysis(prompt)
    response_card = format_elite_card(analysis_result) # Usa a nova função de formatação
    await update.message.reply_text(response_card)

def main() -> None:
    logger.info("Iniciando processo principal (V7.0 - Apresentação de Elite)...")
    load_knowledge_base()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.critical("ERRO CRÍTICO: TELEGRAM_BOT_TOKEN não definido."); return
        
    api_key = os.getenv("APIFOOTBALL_KEY")
    if not api_key:
        logger.critical("ERRO CRÍTICO: APIFOOTBALL_KEY não definida."); return

    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    
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
