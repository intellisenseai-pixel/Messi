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
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Módulo do Servidor Web Falso ---
app = Flask(__name__)
@app.route('/')
def health_check():
    return "Bot is alive and running.", 200
def run_flask_app():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- NÚCLEO ANALÍTICO ARSENAL (V2.3 - DOUTRINA SOBERANA) ---
def arsenal_core_analysis(prompt: str) -> dict:
    logger.info(f"Executando análise V2.3 (Doutrina Soberana) para: '{prompt}'")
    if "analise o jogo" not in prompt.lower():
        return {"error": "Comando inválido. Use 'analise o jogo Time A vs Time B'."}
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
        # Simula as probabilidades para todas as opções do mercado
        probabilities = [random.uniform(0.1, 0.8) for _ in selection_options]
        probabilities = [p / sum(probabilities) for p in probabilities] # Normaliza para somar 1.0
        
        # Simula as odds de mercado
        odds = [round(random.uniform(1.5, 5.0), 2) for _ in selection_options]

        # Encontra a melhor oportunidade dentro do mercado
        best_opportunity = None
        max_ev = -1.0

        for i, selection in enumerate(selection_options):
            real_prob = probabilities[i]
            odd = odds[i]
            ev = (odd * real_prob) - 1
            if ev > max_ev:
                max_ev = ev
                
                # Calcula a prob da segunda melhor opção para o critério de dominância
                sorted_probs = sorted(probabilities, reverse=True)
                prob_dominance_diff = sorted_probs[0] - sorted_probs[1] if len(sorted_probs) > 1 else sorted_probs[0]

                best_opportunity = {
                    "selection": selection,
                    "odd": odd,
                    "real_probability": real_prob,
                    "expected_value": ev,
                    "implied_probability": 1 / odd,
                    "prob_difference": real_prob - (1 / odd),
                    "prob_dominance_diff": prob_dominance_diff,
                    "is_draw_selection": "empate" in selection.lower()
                }

        # --- Aplicação da Doutrina Arsenal Soberana ---
        opp = best_opportunity
        classification = "🔴 Vermelho"
        analysis_text = f"EV Negativo ({opp['expected_value']*100:+.1f}%). A aposta é matematicamente perdedora e foi descartada."

        # Critérios de falha que levam ao Amarelo ou Vermelho
        if opp['expected_value'] >= 0.0:
            if opp['expected_value'] < 0.10:
                classification = "🟡 Amarelo"
                analysis_text = f"EV positivo, mas abaixo do nosso padrão de +10%. A vantagem de {opp['expected_value']*100:+.1f}% é marginal."
            elif opp['prob_difference'] < 0.05:
                classification = "🟡 Amarelo"
                analysis_text = f"O EV é alto, mas a vantagem sobre o mercado ({opp['prob_difference']*100:+.1f}pts) é menor que os 5pts exigidos."
            elif opp['real_probability'] < 0.40:
                classification = "🟡 Amarelo"
                analysis_text = f"O EV é alto, mas a probabilidade de acerto ({opp['real_probability']*100:.1f}%) está abaixo do nosso mínimo de 40%."
            elif opp['is_draw_selection'] and opp['real_probability'] > 0.30:
                classification = "🔴 Vermelho" # Violação de regra de segurança fundamental
                analysis_text = f"APOSTA EM EMPATE DESCARTADA. A probabilidade de empate ({opp['real_probability']*100:.1f}%) excede o limite de 30%."
            elif opp['prob_dominance_diff'] < 0.15:
                classification = "🟡 Amarelo"
                analysis_text = f"CRITÉRIO SOBERANO FALHOU. A dominância sobre a 2ª opção é de apenas {opp['prob_dominance_diff']*100:+.1f}pts (mínimo 15pts)."
            else:
                # Se passou por todos os filtros, é Verde
                classification = "🟢 Verde"
                analysis_text = f"OPORTUNIDADE SOBERANA. Passou em todos os 5 portões de validação. EV: {opp['expected_value']*100:+.1f}%, Vantagem: {opp['prob_difference']*100:+.1f}pts, Dominância: {opp['prob_dominance_diff']*100:+.1f}pts."

        return {
            "market": market_name,
            "selection": opp['selection'],
            "odd": opp['odd'],
            "real_probability_percent": f"{opp['real_probability'] * 100:.1f}%",
            "expected_value_percent": f"{opp['expected_value'] * 100:+.1f}%",
            "classification": classification,
            "analysis_text": analysis_text
        }

    # --- Geração dos Cards ---
    analysis_1x2 = generate_market_analysis("Vencedor da Partida (1x2)", [home_team, "Empate", away_team])
    analysis_over_under = generate_market_analysis("Total de Gols (Over/Under 2.5)", ["Acima de 2.5", "Abaixo de 2.5"])
    analysis_btts = generate_market_analysis("Ambas as Equipes Marcam (BTTS)", ["Sim", "Não"])
    return {"game_title": game_title, "timestamp": datetime.now().strftime("%d/%m/%Y – %H:%M"),
            "markets": [analysis_1x2, analysis_over_under, analysis_btts]}

# --- Módulos de Formatação, Handlers e Main (sem alterações) ---
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
    await update.message.reply_text("Agente ⚽️ Messi (V2.3 - Doutrina Soberana) operacional.")

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prompt = update.message.text.replace(f"@{context.bot.username}", "").strip()
    await update.message.reply_text("Solicitação V2.3 recebida. Aplicando Doutrina Soberana...", reply_to_message_id=update.message.message_id)
    analysis_result = arsenal_core_analysis(prompt)
    response_card = format_multimarket_card(analysis_result)
    await update.message.reply_text(response_card)

def main() -> None:
    logger.info("Iniciando processo principal (V2.3 - Doutrina Soberana)...")
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
