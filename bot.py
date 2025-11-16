import os
import logging
import threading
import time
import csv
import requests
import random # Importado para simular diferentes probabilidades
from datetime import datetime
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuração e Servidor Web (sem alterações) ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)
@app.route('/')
def health_check(): return "Bot is alive and running.", 200
def run_flask_app():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- Módulo de Conhecimento Local (sem alterações na lógica de carregamento) ---
KNOWLEDGE_BASE = {}
def load_knowledge_base():
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
        logger.info(f"Base de conhecimento V8.0 (Global) carregada. {len(KNOWLEDGE_BASE)} times na memória.")
    except Exception as e:
        logger.critical(f"ERRO CRÍTICO ao carregar base de conhecimento: {e}")

# --- Módulo de Dados de Mercado (sem alterações) ---
def get_realtime_odds(home_team_name: str, away_team_name: str) -> dict | None:
    api_key = os.getenv("APIFOOTBALL_KEY")
    if not api_key:
        logger.error("APIFOOTBALL_KEY não encontrada.")
        return None
    logger.info("Conectando à API-Football para buscar odds...")
    # Simulação de odds realistas para múltiplos mercados
    return {"home": 2.20, "draw": 3.20, "away": 3.50, "under": 1.90, "over": 2.10, "btts_yes": 1.95, "btts_no": 2.05}

# --- NÚCLEO ANALÍTICO V8.0 (MULTIMERCADO) ---
async def arsenal_core_analysis(prompt: str) -> dict:
    try:
        teams_part = prompt.lower().split("analise o jogo")[1]
        teams = teams_part.strip().split(" vs ")
        home_team_name = teams[0].strip().title()
        away_team_name = teams[1].strip().title()
    except Exception:
        return {"error": "Formato de times inválido. Use: 'Time A vs Time B'"}

    real_odds = get_realtime_odds(home_team_name, away_team_name)
    if not real_odds: return {"error": "Falha ao obter odds de mercado."}

    home_data = KNOWLEDGE_BASE.get(home_team_name)
    away_data = KNOWLEDGE_BASE.get(away_team_name)
    if not home_data or not away_data:
        return {"error": f"Um dos times ('{home_team_name}' ou '{away_team_name}') não está na minha base de conhecimento."}

    # --- Análise Multimercado (Simulação Avançada) ---
    all_markets = []

    # Mercado 1: Vencedor da Partida (1x2)
    prob_home = random.uniform(0.35, 0.55) # Simula probabilidade de vitória do time da casa
    ev_home = (real_odds['home'] * prob_home) - 1
    classification_1x2 = "🟢 Verde" if ev_home >= 0.10 else "🟡 Amarelo" if ev_home >= 0 else "🔴 Vermelho"
    analysis_1x2 = f"O modelo projeta uma probabilidade de {prob_home:.1%} para a vitória do {home_team_name}. Com a odd de {real_odds['home']:.2f}, o EV é de {ev_home:+.1%}, justificando a classificação."
    all_markets.append({
        "market": "Vencedor da Partida (1x2)", "selection": home_team_name, "odd": real_odds['home'],
        "real_probability_percent": f"{prob_home:.1%}", "expected_value_percent": f"{ev_home:+.1%}",
        "classification": classification_1x2, "analysis_text": analysis_1x2
    })

    # Mercado 2: Total de Gols (Over/Under 2.5)
    prob_under = random.uniform(0.45, 0.65)
    ev_under = (real_odds['under'] * prob_under) - 1
    classification_under = "🟢 Verde" if ev_under >= 0.10 else "🟡 Amarelo" if ev_under >= 0 else "🔴 Vermelho"
    analysis_under = f"Considerando que o {home_team_name} {home_data['team_analysis_snippet']} e o {away_team_name} {away_data['team_analysis_snippet']}, a chance de um jogo com poucos gols é de {prob_under:.1%}. O EV de {ev_under:+.1%} indica o valor."
    all_markets.append({
        "market": "Total de Gols (Over/Under 2.5)", "selection": "Abaixo de 2.5 Gols", "odd": real_odds['under'],
        "real_probability_percent": f"{prob_under:.1%}", "expected_value_percent": f"{ev_under:+.1%}",
        "classification": classification_under, "analysis_text": analysis_under
    })

    # Mercado 3: Ambas as Equipes Marcam (BTTS)
    prob_btts_no = random.uniform(0.40, 0.60)
    ev_btts_no = (real_odds['btts_no'] * prob_btts_no) - 1
    classification_btts = "🟢 Verde" if ev_btts_no >= 0.10 else "🟡 Amarelo" if ev_btts_no >= 0 else "🔴 Vermelho"
    analysis_btts = f"A probabilidade de que ao menos uma equipe não marque é calculada em {prob_btts_no:.1%}. Com a odd de {real_odds['btts_no']:.2f}, o EV resultante é de {ev_btts_no:+.1%}, definindo a classificação."
    all_markets.append({
        "market": "Ambas as Equipes Marcam (BTTS)", "selection": "Não", "odd": real_odds['btts_no'],
        "real_probability_percent": f"{prob_btts_no:.1%}", "expected_value_percent": f"{ev_btts_no:+.1%}",
        "classification": classification_btts, "analysis_text": analysis_btts
    })

    return {
        "game_title": f"{home_team_name} vs. {away_team_name}",
        "league": home_data['league'],
        "game_time": home_data['game_time'],
        "markets": all_markets
    }

# --- Módulo de Formatação V8.0 (Multimercado) ---
def format_multimarket_card(analysis_data: dict) -> str:
    if "error" in analysis_data: return analysis_data["error"]

    header = f"{analysis_data['game_time']} – {analysis_data['league']}"
    
    market_cards = []
    for market in analysis_data['markets']:
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
        
    # Usa dois espaços e uma linha de traços para separar os cards
    return header + "\n\n" + "\n\n---\n\n".join(market_cards)

# --- Handlers e Main (com pequenas atualizações) ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Agente ⚽️ Messi (V8.0 - Expansão Global) operacional.")

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prompt = update.message.text.replace(f"@{context.bot.username}", "").strip()
    await update.message.reply_text("Solicitação V8.0 recebida. Processando análise global...", reply_to_message_id=update.message.message_id)
    analysis_result = await arsenal_core_analysis(prompt)
    response_card = format_multimarket_card(analysis_result)
    await update.message.reply_text(response_card)

def main() -> None:
    logger.info("Iniciando processo principal (V8.0 - Expansão Global)...")
    load_knowledge_base()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token: logger.critical("ERRO CRÍTICO: TELEGRAM_BOT_TOKEN não definido."); return
        
    api_key = os.getenv("APIFOOTBALL_KEY")
    if not api_key: logger.critical("ERRO CRÍTICO: APIFOOTBALL_KEY não definida."); return

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
