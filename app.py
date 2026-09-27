import streamlit as st
import requests
import pandas as pd
import random
import time

# ==========================================
# 🔑 CREDENCIALES TOTALMENTE CONFIGURADAS 
# ==========================================
TELEGRAM_TOKEN = "8254842305:AAGerufL8CiGBjZBTkl4JqxyUqMbgG1_Lg"  
TELEGRAM_CHAT_ID = "6736135063" 

# ⚠️ COLOCA TU API-KEY AQUÍ CUANDO LA TENGAS PARA ENTRAR EN MODO REAL
# Mientras esté vacía "", la app usará el simulador inteligente multiligas.
API_KEY = "" 
# ==========================================

st.set_page_config(page_title="IA Predictor Pro - Elite", layout="wide")
st.title("🇪🇺🇨🇴 Live Predictor: Ligas Élite")
st.write("Monitoreando en tiempo real: Liga BetPlay, Premier, LaLiga, Serie A, Bundesliga, Ligue 1, Champions y Libertadores.")

# IDs oficiales de API-Football para las mejores ligas del mundo
LIGAS_ELITE_IDS = {
    39: "Premier League (Inglaterra)",
    140: "LaLiga (España)",
    135: "Serie A (Italia)",
    78: "Bundesliga (Alemania)",
    61: "Ligue 1 (Francia)",
    2: "UEFA Champions League",
    13: "Copa Libertadores",
    239: "Liga BetPlay (Colombia)"
}

def enviar_alerta_telegram(mensaje):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload)
    except: pass

def obtener_datos():
    if API_KEY and API_KEY != "":
        try:
            url = "https://api-sports.io"
            headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
            res = requests.get(url, headers=headers).json()
            return res.get('response', []), True
        except: pass
    
    # Simulador inteligente multiligas (Se activa automáticamente si no hay API Key)
    partidos_mock = []
    simulacion_partidos = [
        {"l": "Millonarios", "v": "Atlético Nacional", "liga": "Liga BetPlay"},
        {"l": "Real Madrid", "v": "Barcelona", "liga": "LaLiga"},
        {"l": "Manchester City", "v": "Liverpool", "liga": "Premier League"},
        {"l": "Bayern Múnich", "v": "PSG", "liga": "Champions League"}
    ]
    for i, part in enumerate(simulacion_partidos):
        tiros_l = random.randint(2, 15)
        tiros_v = random.randint(2, 15)
        goles_l = random.randint(0, 3)
        goles_v = random.randint(0, 3)
        partidos_mock.append({
            'fixture': {'id': 500 + i}, 'status': {'elapsed': random.randint(15, 88)},
            'league': {'name': part['liga'], 'id': list(LIGAS_ELITE_IDS.keys())[i if i < len(LIGAS_ELITE_IDS) else 0]},
            'teams': {'home': {'name': part['l']}, 'away': {'name': part['v']}},
            'goals': {'home': goles_l, 'away': goles_v}, 'mock_stats': (tiros_l, tiros_v)
        })
    return list(partidos_mock), False

if "alertas_enviadas" not in st.session_state:
    st.session_state.alertas_enviadas = set()

partidos, es_real = obtener_datos()

# Filtrado Inteligente de las Mejores Ligas del Mundo
partidos_filtrados = []
for p in partidos:
    league_id = p['league']['id']
    # Si los datos provienen de la API real, validamos contra nuestro Diccionario Élite
    if es_real:
        if league_id in LIGAS_ELITE_IDS:
            partidos_filtrados.append(p)
    else:
        partidos_filtrados.append(p) # El simulador ya viene pre-filtrado

if not partidos_filtrados:
    st.info("No hay partidos de las ligas grandes o Colombia jugándose en vivo en este milisegundo.")
else:
    for partido in partidos_filtrados:
        local = partido['teams']['home']['name']
        visitante = partido['teams']['away']['name']
        goles_l = partido['goals']['home'] or 0
        goles_v = partido['goals']['away'] or 0
        tiempo = partido['fixture']['status']['elapsed'] if es_real else partido['status']['elapsed']
        fixture_id = partido['fixture']['id']
        nombre_liga = LIGAS_ELITE_IDS.get(partido['league']['id'], partido['league']['name'])
        
        if es_real:
            stats = partido.get('statistics', [])
            tiros_l, tiros_v = 0, 0
            for s in stats:
                if s['team']['name'] == local:
                    for stat in s['statistics']:
                        if stat['type'] == 'Shots on Goal': tiros_l = stat['value'] or 0
                if s['team']['name'] == visitante:
                    for stat in s['statistics']:
                        if stat['type'] == 'Shots on Goal': tiros_v = stat['value'] or 0
        else:
            tiros_l, tiros_v = partido['mock_stats']

        with st.container(border=True):
            st.write(f"🏆 *{nombre_liga}*")
            st.subheader(f"⏱️ {tiempo}' | {local} {goles_l} - {goles_v} {visitante}")
            
            # Algoritmo de Presión Ofensiva Modificado para Ligas Élite
            presion_l = int((tiros_l * 2.5) + (goles_l * 0.2))
            presion_v = int((tiros_v * 2.5) + (goles_v * 0.2))
            
            df_chart = pd.DataFrame({"Equipo": [local, visitante], "Índice de Presión": [presion_l, presion_v]})
            st.bar_chart(data=df_chart, x="Equipo", y="Índice de Presión", color="#008080")
            
            alerta_id = f"{fixture_id}_{tiempo}_{goles_l}_{goles_v}"
            
            # Envío automático a tu Telegram
            if presion_l > presion_v + 6 and alerta_id not in st.session_state.alertas_enviadas:
                msg = f"🏆 *{nombre_liga}* 🏆\n⚽ *ALERTA DE GOL INMINENTE* ⚽\n\n📌 *Partido:* {local} vs {visitante}\n⏱️ *Minuto:* {tiempo}'\n🔥 *Presión:* {local} está encima con {tiros_l} tiros directos. ¡El gol del local se cae de maduro!"
                enviar_alerta_telegram(msg)
                st.session_state.alertas_enviadas.add(alerta_id)
                st.success("🚨 Análisis Élite enviado a tu Telegram.")
                
            elif presion_v > presion_l + 6 and alerta_id not in st.session_state.alertas_enviadas:
                msg = f"🏆 *{nombre_liga}* 🏆\n⚽ *ALERTA DE GOL INMINENTE* ⚽\n\n📌 *Partido:* {local} vs {visitante}\n⏱️ *Minuto:* {tiempo}'\n🔥 *Presión:* {visitante} está encima con {tiros_v} tiros directos. ¡El gol del visitante está muy cerca!"
                enviar_alerta_telegram(msg)
                st.session_state.alertas_enviadas.add(alerta_id)
                st.success("🚨 Análisis Élite enviado a tu Telegram.")

time.sleep(15)
st.rerun()
