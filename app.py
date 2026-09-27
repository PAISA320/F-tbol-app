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

st.set_page_config(page_title="IA Predictor Pro - Live", layout="wide")
st.title("🇨🇴 Live Predictor: Fútbol en Tiempo Real")
st.write("Conexión directa con los servidores globales de datos deportivos.")

def enviar_alerta_telegram(mensaje):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    try: 
        requests.post(url, json=payload)
    except: 
        pass

# --- 🚀 PANEL DE CONTROL DE PRUEBAS ---
st.subheader("🛠️ Panel de Control de Alertas")
if st.button("📲 FORZAR MENSAJE DE PRUEBA A TELEGRAM"):
    enviar_alerta_telegram("🚀 *¡Conexión Exitosa!* Tu aplicación en la nube está enlazada correctamente con tu chat. ¡El canal de alertas está abierto!")
    st.success("¡Mensaje de prueba enviado! Revisa tu chat con el bot.")
st.divider()

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

if not partidos:
    st.error("No hay partidos profesionales jugándose en directo en este momento en los servidores de la API.")
else:
    # Quitamos los filtros de ID para que lea todos los partidos en juego (incluyendo Junior vs DIM)
    for partido in partidos:
        local = partido['teams']['home']['name']
        visitante = partido['teams']['away']['name']
        goles_l = partido['goals']['home'] if partido['goals']['home'] is not None else 0
        goles_v = partido['goals']['away'] if partido['goals']['away'] is not None else 0
        tiempo = partido['fixture']['status']['elapsed']
        fixture_id = partido['fixture']['id']
        nombre_liga = partido['league']['name']
        
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
            st.caption(f"🏆 {nombre_liga} (ID: {partido['league']['id']})")
            st.subheader(f"⏱️ {tiempo}' | {local} {goles_l} - {goles_v} {visitante}")
            
            # Algoritmo de Presión Ofensiva Real
            presion_l = int((tiros_l * 2.5) + (goles_l * 0.2))
            presion_v = int((tiros_v * 2.5) + (goles_v * 0.2))
            
            # Gráfica de rendimiento para ver la presión desde el celular
            df_chart = pd.DataFrame({"Equipo": [local, visitante], "Índice de Presión": [presion_l, presion_v]})
            st.bar_chart(data=df_chart, x="Equipo", y="Índice de Presión", color="#008080")
            
            alerta_id = f"{fixture_id}_{tiempo}_{goles_l}_{goles_v}"
            
            # Disparador y envío de la alerta real a tu Telegram
            if presion_l > presion_v + 4 and alerta_id not in st.session_state.alertas_enviadas:
                msg = f"🏆 *{nombre_liga}* 🏆\n⚽ *ALERTA DE PRESIÓN EN VIVO* ⚽\n\n📌 *Partido:* {local} vs {visitante}\n⏱️ *Minuto:* {tiempo}'\n🔥 *Presión:* {local} ataca intensamente con {tiros_l} tiros directos."
                enviar_alerta_telegram(msg)
                st.session_state.alertas_enviadas.add(alerta_id)
                st.success(f"🚨 Análisis de {local} enviado a tu Telegram.")
                
            elif presion_v > presion_l + 4 and alerta_id not in st.session_state.alertas_enviadas:
                msg = f"🏆 *{nombre_liga}* 🏆\n⚽ *ALERTA DE PRESIÓN EN VIVO* ⚽\n\n📌 *Partido:* {local} vs {visitante}\n⏱️ *Minuto:* {tiempo}'\n🔥 *Presión:* {visitante} domina con {tiros_v} tiros directos."
                enviar_alerta_telegram(msg)
                st.session_state.alertas_enviadas.add(alerta_id)
                st.success(f"🚨 Análisis de {visitante} enviado a tu Telegram.")

# Actualización automática cada 60 segundos
time.sleep(60)
st.rerun()
