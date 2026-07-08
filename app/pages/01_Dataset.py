import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Dataset", page_icon="📁", layout="wide")

st.title("📁 Dataset")
st.markdown("Inspección inicial, calidad de datos y pipeline de limpieza.")
st.markdown("---")

# ── Carga ─────────────────────────────────────────────────────────────────────
@st.cache_data
def cargar_raw():
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "streaming_users_dirty.json")
    return pd.read_json(path)

@st.cache_data
def cargar_procesado():
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "streaming_users_clean.json")
    return pd.read_json(path)

try:
    df_raw = cargar_raw()
    raw_ok = True
except Exception:
    raw_ok = False

try:
    df_proc = cargar_procesado()
    proc_ok = True
except Exception:
    proc_ok = False

# ── 1. Descripción general ────────────────────────────────────────────────────
st.markdown("## 1. Descripción general")

st.markdown("### Diccionario de variables")
st.markdown("""
- `user_id` = identificador de usuario
- `age` = edad
- `subscription_plan` = plan de suscripción
- `monthly_watch_time_mins` = minutos vistos en el mes
- `country` = país
- `favorite_genre` = género favorito
- `last_login_date` = fecha de último inicio de sesión
- `customer_support_tickets` = tickets de atención al cliente
""")

diccionario = pd.DataFrame({
    "Variable": [
        "user_id", "age", "subscription_plan", "monthly_watch_time_mins",
        "country", "favorite_genre", "last_login_date", "customer_support_tickets"
    ],
    "Tipo original": [
        "int64", "int64", "object", "float64",
        "object", "object", "object", "int64"
    ],
    "Descripción": [
        "Identificador único de usuario",
        "Edad del usuario",
        "Plan de suscripción (básico / estándar / premium)",
        "Minutos vistos en el mes",
        "País de origen del usuario",
        "Género de contenido preferido",
        "Fecha del último inicio de sesión",
        "Cantidad de tickets de atención al cliente"
    ]
})
st.dataframe(diccionario, use_container_width=True, hide_index=True)

# ── 2. Calidad inicial ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 2. Calidad inicial")
st.markdown("""
Antes de aplicar cualquier transformación, inspeccionamos la estructura
general del dataset: dimensiones, tipos de datos asignados automáticamente
y presencia de valores nulos por columna. Esta revisión es la base de
evidencia para todas las decisiones posteriores.
""")

if raw_ok:
    col1, col2, col3 = st.columns(3)
    col1.metric("Filas", f"{df_raw.shape[0]:,}")
    col2.metric("Columnas", df_raw.shape[1])
    col3.metric("Nulos totales", int(df_raw.isnull().sum().sum()))

    col_izq, col_der = st.columns(2)

    with col_izq:
        st.markdown("**Vista previa del dataset original**")
        st.dataframe(df_raw.head(8), use_container_width=True)

    with col_der:
        st.markdown("**Nulos por columna**")
        nulos = df_raw.isnull().sum().reset_index()
        nulos.columns = ["Variable", "Nulos"]
        nulos["% sobre total"] = (nulos["Nulos"] / len(df_raw) * 100).round(2)
        st.dataframe(nulos, use_container_width=True, hide_index=True)

    st.info("""
    **Interpretación:**
    - 8,160 filas, 8 columnas.
    - En columnas `monthly_watch_time_mins` (15), `favorite_genre` (22) y `last_login_date` (25) hay presencia de datos nulos, sumando un total de 62.
    - La columna `last_login_date` tiene un tipo de dato erróneo (está en object, debe ser date).
    - Valor mínimo de `age` y `monthly_watch_time_mins` son negativos, cuando no es posible.
    - Valor máximo de `age` y `monthly_watch_time_mins` tienen valores imposibles.
    - Análisis de medidas se realizan luego del procesamiento y limpieza de la base de datos.
    """)
else:
    st.warning("No se encontró el dataset original en `data/raw/`.")

# ── 3. Pipeline de limpieza ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 3. Pipeline de limpieza")

with st.expander("📌 1. Estandarización de fechas (last_login_date)"):
    st.markdown("""
    La columna `last_login_date` presentaba múltiples formatos mezclados (YYYY-MM-DD, MM-DD-YYYY, YYYY/MM/DD) y fue cargada como `object`.
    
    **Acción:** Se estandarizaron todas las fechas al formato `DD/MM/YYYY`. Los valores nulos, `'not_available'` o vacíos se reemplazaron con `'--/--/--'`.
    
    **Impacto:** 25 registros fueron imputados con `--/--/--`. La columna se convirtió a tipo `datetime` para permitir análisis temporales.
    """)

with st.expander("📌 2. Eliminación de fechas futuras"):
    st.markdown("""
    Se detectaron registros con fechas de último login posteriores al 06/07/2026, lo cual es imposible en el contexto real de la plataforma.
    
    **Acción:** Se eliminaron los 3 registros con fechas futuras para no corromper la consistencia temporal de la base de datos.
    
    **Impacto:** 3 registros eliminados.
    """)

with st.expander("📌 3. Imputación de nulos en favorite_genre"):
    st.markdown("""
    La columna `favorite_genre` presentaba 22 valores nulos. No podemos determinar si representan un dato no registrado o una preferencia genuinamente indefinida del usuario.
    
    **Acción:** Se reemplazaron los nulos con la categoría explícita `'Sin género favorito'` en lugar de imputar un género ficticio o eliminar los registros.
    
    **Impacto:** 22 registros imputados con `'Sin género favorito'`.
    """)

with st.expander("📌 4. Filtrado de edades (age)"):
    st.markdown("""
    Se detectaron valores de edad iguales a 0, negativos (-5) y superiores a 120 (130, 150), todos imposibles para usuarios reales de una plataforma de streaming.
    
    **Acción:** Se filtraron los registros manteniendo solo edades entre 4 y 95 años. No existe criterio lógico para imputar la edad de un usuario desconocido.
    
    **Impacto:** 12 registros eliminados.
    """)

with st.expander("📌 5. Eliminación de valores imposibles en monthly_watch_time_mins"):
    st.markdown("""
    Se detectaron valores negativos (-120.0, -1.0) y valores extremadamente altos (50,000.0, 99,999.0) en el tiempo de visualización mensual.
    
    **Acción:** Se eliminaron los registros con valores negativos o superiores a 50,000 minutos (considerados outliers imposibles).
    
    **Impacto:** 15 registros eliminados.
    """)

with st.expander("📌 6. Imputación de nulos en monthly_watch_time_mins"):
    st.markdown("""
    La columna `monthly_watch_time_mins` presentaba 15 valores nulos.
    
    **Acción:** Se imputaron los nulos con la **mediana global** (523.45 minutos), ya que la mediana es robusta frente a outliers y no introduce sesgos significativos en la distribución del consumo.
    
    **Impacto:** 15 registros imputados con el valor mediano.
    """)

with st.expander("📌 7. Estandarización de países (country)"):
    st.markdown("""
    Se detectaron múltiples variantes para el mismo país: `'Brasil'`, `'Brazil'`, `'BRA'`; `'México'`, `'Mexico'`, `'MEX'`; etc.
    
    **Acción:** Se limpiaron espacios en blanco, se convirtió todo a minúsculas y se aplicó un mapeo para unificar todos los países bajo 7 nombres estándar: `argentina`, `brasil`, `chile`, `colombia`, `méxico`, `perú`, `uruguay`.
    
    **Impacto:** De 9 valores únicos (incluyendo variantes con espacios), se redujo a 7 países únicos.
    """)

with st.expander("📌 8. Estandarización de planes (subscription_plan)"):
    st.markdown("""
    Se detectaron múltiples variantes para el mismo plan: `'Básico'`, `'BASICO'`, `'Basic'`, `'basico'`; `'Estándar'`, `'Standard'`, `'Std'`; `'Premium'`, `'Premiun'`.
    
    **Acción:** Se limpiaron espacios en blanco y se aplicó un mapeo para unificar todos los planes bajo 3 nombres estándar: `'Básico'`, `'Estándar'`, `'Premium'`.
    
    **Impacto:** De 9 valores únicos, se redujo a 3 planes únicos.
    """)

with st.expander("📌 9. Estandarización de géneros (favorite_genre)"):
    st.markdown("""
    Se detectaron múltiples variantes para el mismo género: `'Drama'`, `'DRAMA'`, `'drama'`; `'Acción'`, `'ACCIÓN'`, `'Action'`, `'accion'`; `'Comedia'`, `'COMEDIA'`, `'Comedy'`.
    
    **Acción:** Se limpiaron espacios en blanco, se convirtió a minúsculas y se aplicó un mapeo para unificar todos los géneros bajo 8 nombres estándar: `'Acción'`, `'Comedia'`, `'Crimen'`, `'Documental'`, `'Drama'`, `'Romance'`, `'Sin género favorito'`, `'Thriller'`.
    
    **Impacto:** De 25 valores únicos, se redujo a 8 géneros únicos.
    """)

with st.expander("📌 10. Eliminación de duplicados"):
    st.markdown("""
    Se verificó la presencia de duplicados por `user_id`.
    
    **Acción:** Se aplicó `drop_duplicates(subset=['user_id'], keep='first')` para mantener solo el primer registro de cada usuario.
    
    **Impacto:** No se encontraron duplicados de `user_id` en el dataset.
    """)

with st.expander("📌 11. Estado final — guardado y log ETL"):
    st.markdown("""
    El dataset limpio se guarda en `data/processed/streaming_users_clean.json` preservando el original intacto en `data/raw/` para garantizar la reproducibilidad y auditoría del proceso.
    
    El log ETL registra cada transformación con su impacto en filas y nulos, permitiendo comparar el estado inicial y final de manera transparente.
    
    **Resultado final:**
    - Registros: 17,985 (de 18,000 originales)
    - Nulos totales: 0
    - Variables categóricas estandarizadas: country (7), subscription_plan (3), favorite_genre (8)
    - Fechas estandarizadas al formato `DD/MM/YYYY`
    """)

# ── 4. Log ETL ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 4. Log ETL")
st.markdown("""
El log ETL documenta cada transformación aplicada al dataset, permitiendo
comparar el estado inicial y final de manera transparente.
""")

try:
    path_log = os.path.join(os.path.dirname(__file__), "..", "..", "logs", "pipeline_log.csv")
    log = pd.read_csv(path_log)
    st.dataframe(log, use_container_width=True, hide_index=True)
except Exception:
    log_data = {
        "Paso": [
            "01", "02", "03", "04", "05", "06", "07", "08", "09", "10"
        ],
        "Descripción": [
            "Dataset original cargado",
            "Estandarización de fechas (DD/MM/YYYY) con --/--/-- para nulos",
            "Eliminación de fechas futuras (> 06/07/2026)",
            "Imputación de nulos en favorite_genre con 'Sin género favorito'",
            "Filtrado de edades (4-95 años)",
            "Eliminación de valores imposibles en monthly_watch_time_mins",
            "Imputación de nulos en monthly_watch_time_mins (mediana)",
            "Estandarización de países (7 países únicos)",
            "Estandarización de planes (Básico/Estándar/Premium)",
            "Estandarización de géneros (8 géneros únicos)"
        ],
        "Filas": [
            18000, 18000, 17997, 17997, 17985, 17985, 17985, 17985, 17985, 17985
        ],
        "Nulos": [
            62, 37, 37, 15, 15, 15, 0, 0, 0, 0
        ],
        "Retención (%)": [
            100.0, 100.0, 99.98, 99.98, 99.92, 99.92, 99.92, 99.92, 99.92, 99.92
        ]
    }
    st.dataframe(pd.DataFrame(log_data), use_container_width=True, hide_index=True)

# ── 5. Dataset procesado ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 5. Dataset procesado")
st.markdown("""
Luego de aplicar todas las transformaciones documentadas, el dataset final
está listo para análisis exploratorio y reducción de dimensionalidad.
""")

if proc_ok:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Filas finales", f"{df_proc.shape[0]:,}")
    col2.metric("Columnas finales", df_proc.shape[1])
    col3.metric("Nulos restantes", int(df_proc.isnull().sum().sum()))
    col4.metric("Países únicos", df_proc['country'].nunique())

    st.markdown("**Vista previa del dataset procesado**")
    st.dataframe(df_proc.head(8), use_container_width=True)

    st.markdown("**Estadísticas descriptivas del dataset procesado**")
    st.dataframe(df_proc.describe(), use_container_width=True)
else:
    st.warning("No se encontró el dataset procesado en `data/processed/`.")

# ── 6. Comparación inicial vs final ──────────────────────────────────────────
st.markdown("---")
st.markdown("## 6. Comparación inicial vs final")

if raw_ok and proc_ok:
    col1, col2 = st.columns(2)
    
    # Cálculos dinámicos
    filas_orig = df_raw.shape[0]
    filas_proc = df_proc.shape[0]
    nulos_orig = int(df_raw.isnull().sum().sum())
    nulos_proc = int(df_proc.isnull().sum().sum())
    retencion = (filas_proc / filas_orig) * 100

    with col1:
        st.markdown("**📊 Dataset original**")
        st.metric("Filas", f"{filas_orig:,}")
        st.metric("Nulos", f"{nulos_orig:,}")
        st.metric("Países", df_raw['country'].nunique())

    with col2:
        st.markdown("**✨ Dataset procesado**")
        st.metric("Filas", f"{filas_proc:,}")
        st.metric("Nulos", f"{nulos_proc:,}")
        st.metric("Retención (%)", f"{retencion:.2f}%")
        
    st.success(f"Proceso completado: Se retuvo el {retencion:.2f}% de los registros originales tras la limpieza.")
else:
    st.error("No se pudieron cargar ambos datasets para realizar la comparación. Verifica las rutas en 'data/raw/' y 'data/processed/'.")