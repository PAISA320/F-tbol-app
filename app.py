import streamlit as st
import requests
import pandas as pd
import time

# ==========================================
# 🔑 CREDENCIALES CONFIGURADAS Y VERIFICADAS
# ==========================================
TELEGRAM_TOKEN = "8254842305:AAGerufL8CiGBjZBTkl4JqxyUqMbgG1_Lg"  
TELEGRAM_CHAT_ID = "6736135063" 
API_KEY = "bdd59031bc5eae14ad86af3b3fdf48fc" 
# ==========================================

st.set_page_config(page_title="IA Predictor Pro - Live", layout="wide")
st.title("🇨🇴 Live Predictor: Fútbol Profesional Real")
st.write("Conexión en directo con los servidores globales de fútbol.")

def enviar_alerta_telegram(mensaje):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    try: 
        requests.post(url, json=payload)
    except: 
        pass

# --- 🚀 BOTÓN DE PRUEBA INTEGRADO ---
st.subheader("🛠️ Panel de Control de Alertas")
if st.button("📲 FORZAR MENSAJE DE PRUEBA A TELEGRAM"):
    enviar_alerta_telegram("🚀 *¡Conexión Exitosa!* Tu aplicación móvil de predicciones ya está enlazada con tu chat. El canal de comunicación se encuentra abierto correctamente.")
    st.success("¡Mensaje de prueba enviado! Revisa tu chat con el bot.")
st.divider()

LIGAS_ELITE_IDS = {
    39: "Premier League", 140: "LaLiga", 135: "Serie A", 
    78: "Bundesliga", 61: "Ligue 1", 2: "Champions League", 
    13: "Copa Libertadores", 239: "Liga BetPlay (Colombia)"
}

def obtener_partidos_reales():
    try:
        url = "https://api-sports.io"
        headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
        res = requests.get(url, headers=headers).json()
        return res.get('response', [])
    except:
        return []

if "alertas_enviadas" not in st.session_state:
    st.session_state.alertas_enviadas = set()

partidos = obtener_partidos_reales()

# Filtrado inicial por ligas élite
partidos_filtrados = [p for p in partidos if p['league']['id'] in LIGAS_ELITE_IDS]

if not partidos_filtrados:
    st.warning("⚠️ No hay encuentros en juego de la Liga BetPlay o Ligas Europeas principales en este instante.")
    if partidos:
        st.info("Mostrando otros partidos profesionales disputándose en vivo en el mundo ahora mismo:")
        partidos_filtrados = partidos[:12] # Muestra partidos alternativos en tiempo real si el filtro principal está vacío
    else:
        st.error("No hay partidos de fútbol profesional jugándose en directo en este momento.")

for partido in partidos_filtrados:
    local = partido['teams']['home']['name']
    visitante = partido['teams']['away']['name']
    goles_l = partido['goals']['home'] if partido['goals']['home'] is not None else 0
    goles_v = partido['goals']['away'] if partido['goals']['away'] is not None else 0
    tiempo = partido['fixture']['status']['elapsed']
    fixture_id = partido['fixture']['id']
    nombre_liga = LIGAS_ELITE_IDS.get(partido['league']['id'], p['league']['name'] if 'league' in p else "Torneo Internacional")
    
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
        st.caption(f"🏆 {nombre_liga}")
        st.subheader(f"⏱️ {tiempo}' | {local} {goles_l} - {goles_v} {visitante}")
        
        presion_l = int((tiros_l * 2.5) + (goles_l * 0.2))
        presion_v = int((tiros_v * 2.5) + (goles_v * 0.2))
        
        df_chart = pd.DataFrame({"Equipo": [local, visitante], "Índice de Presión": [presion_l, presion_v]})
        st.bar_chart(data=df_chart, x="Equipo", y="Índice de Presión", color="#008080")
        
        alerta_id = f"{fixture_id}_{tiempo}_{goles_l}_{goles_v}"
        
        if presion_l > presion_v + 5 and alerta_id not in st.session_state.alertas_enviadas:
            msg = f"🏆 *{nombre_liga}* 🏆\n⚽ *ALERTA DE PRESIÓN* ⚽\n\n📌 *Partido:* {local} vs {visitante}\n⏱️ *Minuto:* {tiempo}'\n🔥 {local} empuja el ataque con {tiros_l} tiros al arco."
            enviar_alerta_telegram(msg)
            st.session_state.alertas_enviadas.add(alerta_id)
        elif presion_v > presion_l + 5 and alerta_id not in st.session_state.alertas_enviadas:
            msg = f"🏆 *{nombre_liga}* 🏆\n⚽ *ALERTA DE PRESIÓN* ⚽\n\n📌 *Partido:* {local} vs {visitante}\n⏱️ *Minuto:* {tiempo}'\n🔥 {visitante} empuja el ataque con {tiros_v} tiros al arco."
            enviar_alerta_telegram(msg)
            st.session_state.alertas_enviadas.add(alerta_id)

time.sleep(60)
st.rerun()
