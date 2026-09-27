import streamlit as st
import requests
import pandas as pd
import time

# ==========================================
# 🔑 CREDENCIALES COMPLETAMENTE CONFIGURADAS 
# ==========================================
TELEGRAM_TOKEN = "8254842305:AAGerufL8CiGBjZBTkl4JqxyUqMbgG1_Lg"  
TELEGRAM_CHAT_ID = "6736135063" 
API_KEY = "bdd59031bc5eae14ad86af3b3fdf48fc" 
# ==========================================

st.set_page_config(page_title="IA Predictor Pro - Real Time", layout="wide")
st.title("🇨🇴 Live Predictor: Fútbol Profesional Real")
st.write("Analizando datos en vivo de la Liga BetPlay, Europa y las mejores ligas del mundo.")

# IDs oficiales para las mejores ligas
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
    try: 
        requests.post(url, json=payload)
    except: 
        pass

def obtener_partidos_reales():
    try:
        url = "https://api-sports.io"
        headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
        res = requests.get(url, headers=headers).json()
        return res.get('response', [])
    except Exception as e:
        st.error(f"Error de conexión con los servidores de fútbol: {e}")
        return []

if "alertas_enviadas" not in st.session_state:
    st.session_state.alertas_enviadas = set()

partidos = obtener_partidos_reales()

# Filtrado Inteligente de las Mejores Ligas del Mundo
partidos_filtrados = [p for p in partidos if p['league']['id'] in LIGAS_ELITE_IDS]

if not partidos_filtrados:
    st.info("⚽ No hay partidos en juego en este momento de la Liga BetPlay o Ligas Grandes Europeas.")
    if partidos:
        if st.checkbox("Mostrar otros partidos en vivo disponibles en el mundo"):
            partidos_filtrados = partidos[:10]
else:
    for partido in partidos_filtrados:
        local = partido['teams']['home']['name']
        visitante = partido['teams']['away']['name']
        goles_l = partido['goals']['home'] if partido['goals']['home'] is not None else 0
        goles_v = partido['goals']['away'] if partido['goals']['away'] is not None else 0
        tiempo = partido['fixture']['status']['elapsed']
        fixture_id = partido['fixture']['id']
        nombre_liga = LIGAS_ELITE_IDS.get(partido['league']['id'], partido['league']['name'])
        
        # Extraer estadísticas de ataques en vivo reales de la API
        stats = partido.get('statistics', [])
        tiros_l, tiros_v = 0, 0
        for s in stats:
            if s['team']['name'] == local:
                for stat in s['statistics']:
                    if stat['type'] == 'Shots on Goal': tiros_l = stat['value'] or 0
            if s['team']['name'] == visitante:
                for stat in s['statistics']:
                    if stat['type'] == 'Shots on Goal': tiros_v = stat['value'] or 0

        with st.container(border=True):
            st.write(f"🏆 *{nombre_liga}*")
            st.subheader(f"⏱| {tiempo}' | {local} {goles_l} - {goles_v} {visitante}")
            
            # Algoritmo de Presión Ofensiva Real
            presion_l = int((tiros_l * 2.5) + (goles_l * 0.2))
            presion_v = int((tiros_v * 2.5) + (goles_v * 0.2))
            
            # Gráfica de rendimiento para ver la presión desde el celular
            df_chart = pd.DataFrame({"Equipo": [local, visitante], "Índice de Presión": [presion_l, presion_v]})
            st.bar_chart(data=df_chart, x="Equipo", y="Índice de Presión", color="#008080")
            
            alerta_id = f"{fixture_id}_{tiempo}_{goles_l}_{goles_v}"
            
            # Disparador y envío de la alerta real
            if presion_l > presion_v + 5 and alerta_id not in st.session_state.alertas_enviadas:
                msg = f"🏆 *{nombre_liga}* 🏆\n⚽ *ALERTA DE GOL REAL TIME* ⚽\n\n📌 *Partido:* {local} vs {visitante}\n⏱️ *Minuto:* {tiempo}'\n🔥 *Presión:* {local} está atacando intensamente con {tiros_l} remates directos. ¡Se acerca el gol local!"
                enviar_alerta_telegram(msg)
                st.session_state.alertas_enviadas.add(alerta_id)
                st.success("🚨 Análisis real enviado a tu Telegram.")
                
            elif presion_v > presion_l + 5 and alerta_id not in st.session_state.alertas_enviadas:
                msg = f"🏆 *{nombre_liga}* 🏆\n⚽ *ALERTA DE GOL REAL TIME* ⚽\n\n📌 *Partido:* {local} vs {visitante}\n⏱️ *Minuto:* {tiempo}'\n🔥 *Presión:* {visitante} domina el ataque con {tiros_v} remates directos. ¡Se acerca el gol visitante!"
                enviar_alerta_telegram(msg)
                st.session_state.alertas_enviadas.add(alerta_id)
                st.success("🚨 Análisis real enviado a tu Telegram.")

# Actualización automática cada 60 segundos
time.sleep(60)
st.rerun()
