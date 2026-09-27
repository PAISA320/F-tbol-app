import streamlit as st
import random
import time

st.set_page_config(page_title="Predicciones de Fútbol en Vivo", layout="wide")

st.title("⚽ Simulador de Pronósticos de Fútbol en Tiempo Real")
st.write("Esta app analiza estadísticas en vivo para predecir los próximos goles.")

@st.cache_data(ttl=1)
def simular_partidos_en_vivo():
    equipos_locales = ["Real Madrid", "Barcelona", "Manchester City", "Liverpool"]
    equipos_visita = ["PSG", "Arsenal", "Inter de Milán", "Juventus"]
    
    partidos_en_vivo = []
    
    for i in range(3):
        local = equipos_locales[i]
        visita = equipos_visita[i]
        
        tiros_l = random.randint(1, 12)
        tiros_v = random.randint(1, 12)
        goles_l = random.randint(0, 2)
        goles_v = random.randint(0, 2)
        tiempo = random.randint(45, 85)
        
        presion_local = (tiros_l * 1.8) + (goles_l * 0.5)
        presion_visita = (tiros_v * 1.8) + (goles_v * 0.5)
        
        if presion_local > presion_visita + 4:
            pronostico = "🔥 ALTA PRESIÓN: Se acerca gol del Local"
            color = "green"
        elif presion_visita > presion_local + 4:
            pronostico = "🔥 ALTA PRESIÓN: Se acerca gol del Visitante"
            color = "green"
        else:
            pronostico = "⚖️ Partido trabado / Tendencia al Empate"
            color = "orange"
            
        partidos_en_vivo.append({
            "local": local, "visita": visita,
            "goles_l": goles_l, "goles_v": goles_v,
            "tiempo": tiempo, "tiros_l": tiros_l, "tiros_v": tiros_v,
            "pronostico": pronostico, "color": color
        })
    return partidos_en_vivo

partidos = simular_partidos_en_vivo()

for p in partidos:
    with st.container(border=True):
        st.subheader(f"⏱️ Minuto {p['tiempo']}' | {p['local']} {p['goles_l']} - {p['goles_v']} {p['visita']}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label=f"Tiros al arco de {p['local']}", value=f"{p['tiros_l']} 🎯")
        with col2:
            st.metric(label=f"Tiros al arco de {p['visita']}", value=f"{p['tiros_v']} 🎯")
            
        st.markdown(f"### **Predicción IA:** :{p['color']}[{p['pronostico']}]")
        st.divider()

st.caption("🔄 Los datos se actualizan y reanalizan automáticamente cada 5 segundos...")
time.sleep(5)
st.rerun()
