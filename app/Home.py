import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="PI — Minería de Datos",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 Proyecto Integrador — Minería de Datos 1")
st.markdown("**Análisis de usuarios de plataforma de streaming**")
st.markdown("---")

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("""
    ### Contexto

    Este proyecto aplica técnicas de Minería de Datos sobre un dataset de **8160 usuarios**
    de una plataforma de streaming. El objetivo es construir un análisis reproducible
    que cubra inspección, limpieza, exploración, reducción de dimensionalidad
    e interpretación de resultados con decisiones justificadas en evidencia.

    ### Dataset

    El dataset original contiene **8 variables** que describen el comportamiento de los usuarios:

    - **Demográficas:** `age`, `country`
    - **Suscripción:** `subscription_plan`
    - **Consumo:** `monthly_watch_time_mins`, `favorite_genre`
    - **Actividad:** `last_login_date`
    - **Experiencia:** `customer_support_tickets`

    Luego del proceso de limpieza, se obtuvieron **7,342 registros** sin valores nulos
    y con todas las variables categóricas estandarizadas.

    ### Etapas del proyecto

    | Página | Contenido |
    |---|---|
    | 📁 Dataset | Inspección inicial, calidad de datos y pipeline de limpieza |
    | 📊 EDA | Análisis exploratorio con cinco preguntas de análisis concretas |
    | 🔷 PCA | Escalamiento, reducción de dimensionalidad e interpretación |
    | 📝 Conclusiones | Hallazgos, limitaciones y próximos pasos |
    """)

with col2:
    st.markdown("### 👥 Integrantes")
    st.markdown("""
    - **Ignacio Vega Orellana**
    - **Bruno Romano Arnoux**
    """)

    st.markdown("### 📚 Cursado")
    st.markdown("""
    - **Materia:** Minería de Datos 1
    """)

    st.markdown("### 🔗 Enlaces")
    st.markdown("""
    - [📂 Repositorio GitHub](https://github.com/IgnaOV/PI_Mineria_Datos_1)
    - [🚀 Streamlit Cloud](https://pimineriadedatos01.streamlit.app)
    """)

# ── Resumen Dinámico ────────────────────────────────────────────────────────
# Intentamos cargar el procesado para obtener el dato real
try:
    path_proc = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "streaming_users_clean.json")
    df_proc = pd.read_json(path_proc)
    total_registros = df_proc.shape[0]
except Exception:
    total_registros = 7251  # Valor por defecto si no encuentra el archivo

st.markdown("### 📊 Resumen del Dataset")
st.metric("Registros finales", f"{total_registros:,}")
st.metric("Variables", "8")
st.metric("Países", "7")

st.markdown("---")
st.caption("Proyecto Integrador · Minería de Datos 1")