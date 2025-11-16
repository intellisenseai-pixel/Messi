import os
import logging
import threading
import time
import psycopg2
import requests # Nova importação para chamadas de API
import math
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

# --- Módulo de Conexão com Banco de Dados ---
def get_db_connection():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# --- MÓDULO DE DADOS DE MERCADO (API-FOOTBALL) ---
def get_realtime_odds(home_team_name: str, away_team_name: str) -> dict:
    """Conecta-se à API-Football para obter as odds reais de um jogo."""
    api_key = os.getenv("APIFOOTBALL_KEY")
    if not api_key:
        logger.error("Chave da API-Football não encontrada.")
        return None

    # 1. Encontrar o ID dos times
    # (A API-Football funciona melhor com IDs. Uma implementação real buscaria os IDs primeiro)
    # Para simplificar, vamos assumir que a busca por nome funciona.
    
    # 2. Buscar as odds para o jogo
    # A API-Football requer o ID da liga e a temporada. Vamos usar valores de exemplo.
    # Ex: Brasileirão Série A = 71, Temporada = 2025
    try:
        response = requests.get(
            "https://v3.football.api-sports.io/odds",
            headers={"x-apisports-key": api_key},
            params={"league": "71", "season": "2025", "bookmaker": "8", "bet": "1"} # Bet365, Match Winner
         )
        response.raise_for_status()
        odds_data = response.json()['response']
        
        # 3. Encontrar o jogo específico e retornar as odds
        # (A lógica real aqui seria mais complexa, iterando sobre a resposta para encontrar o jogo certo)
        # Para este exemplo, vamos 
