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
    - 8.160 filas, 8 columnas.
    - En columnas `monthly_watch_time_mins` (193), `favorite_genre` (240) y `last_login_date` (320) hay presencia de datos nulos, sumando un total de 753.
    - La columna `last_login_date` tiene un tipo de dato erróneo (está en object, debe ser date), además de tres formatos mezclados (YYYY-MM-DD, MM-DD-YYYY, YYYY/MM/DD).
    - 160 registros duplicados por `user_id`.
    - Valor mínimo de `age` es -5 y valor máximo es 150, ambos imposibles.
    - Valor mínimo de `monthly_watch_time_mins` es -120.0 y valor máximo es 99.999.0, ambos imposibles.
    - Variantes inconsistentes en categóricas: `country` (24 valores únicos), `subscription_plan` (13 valores únicos).
    - Análisis de medidas se realizan luego del procesamiento y limpieza de la base de datos.
    """)
else:
    st.warning("No se encontró el dataset original en `data/raw/`.")

# ── 3. Pipeline de limpieza ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 3. Pipeline de limpieza")

with st.expander("📌 1. Eliminación de duplicados (user_id)"):
    st.markdown("""
    Se detectaron **160 registros duplicados** por `user_id` (mismo usuario cargado más de una vez).

    **Acción:** Se aplicó `drop_duplicates(subset=['user_id'], keep='first')` para mantener solo el primer registro de cada usuario.

    **Impacto:** 8.160 → 8.000 filas. 160 registros eliminados.
    """)

with st.expander("📌 2. Estandarización de fechas y eliminación de fechas futuras (last_login_date)"):
    st.markdown("""
    La columna `last_login_date` presentaba tres formatos mezclados (YYYY-MM-DD, MM-DD-YYYY, YYYY/MM/DD) y fue cargada como `object`. Además, se detectaron registros con fecha de último login posterior al 06/07/2026, imposibles en el contexto real de la plataforma.

    **Acción:** Se estandarizaron todas las fechas al formato `DD/MM/YYYY` (probando cada formato posible) y se eliminaron los registros con fecha futura. Los valores nulos o irrecuperables se marcaron como `'--/--/--'`.

    **Impacto:** 8.000 → 7.601 filas. 399 registros eliminados por fecha futura o irrecuperable.
    """)

with st.expander("📌 3. Filtrado de minutos de visualización (monthly_watch_time_mins)"):
    st.markdown("""
    Se detectaron valores negativos (mínimo -120.0) y valores extremadamente altos (máximo 99.999.0) en el tiempo de visualización mensual, ambos imposibles.

    **Acción:** Se conservaron únicamente los registros con `monthly_watch_time_mins` entre 0 y 5.000 minutos. Como los nulos no cumplen ninguna condición de rango, este filtro también descarta las filas con valores faltantes en esta columna.

    **Impacto:** 7.601 → 7.342 filas. 259 registros eliminados (outliers y nulos).
    """)

with st.expander("📌 4. Imputación y estandarización de favorite_genre"):
    st.markdown("""
    La columna `favorite_genre` presentaba valores nulos y múltiples variantes para el mismo género: `'Drama'`, `'DRAMA'`, `'drama'`; `'Acción'`, `'ACCIÓN'`, `'Action'`, `'thriler'` (mal escrito), etc. No podemos determinar si un nulo representa un dato no registrado o una preferencia genuinamente indefinida.

    **Acción:** Los nulos se reemplazaron con la categoría explícita `'Sin género favorito'` en lugar de imputar un género ficticio o eliminar el registro. Luego se aplicó un mapeo para unificar todas las variantes bajo 8 categorías estándar: `Acción`, `Comedia`, `Crimen`, `Documental`, `Drama`, `Romance`, `Sin género favorito`, `Thriller`.

    **Impacto:** 227 nulos imputados. Filas sin cambios (7.342). ⚠️ *Nota de calidad:* 15 registros con el valor `'DOC'` en mayúsculas no fueron capturados por el mapeo (que compara en minúsculas) y quedaron como `'Doc'` sin estandarizar — pendiente de corrección en una futura iteración.
    """)

with st.expander("📌 5. Filtrado de edades (age)"):
    st.markdown("""
    Se detectaron valores de edad negativos (mínimo -5) y superiores a 120 (máximo 150), ambos imposibles para usuarios reales de una plataforma de streaming.

    **Acción:** Se filtraron los registros manteniendo solo edades entre 4 y 95 años. No existe criterio lógico para imputar la edad de un usuario desconocido.

    **Impacto:** 7.342 → 7.251 filas. 91 registros eliminados.
    """)

with st.expander("📌 6. Estandarización de países (country)"):
    st.markdown("""
    Se detectaron 24 valores únicos para 7 países reales: variantes con mayúsculas/minúsculas, códigos ISO (`ARG`, `BRA`, `CHL`...) y nombres en inglés (`Brazil`, `Mexico`).

    **Acción:** Se limpiaron espacios en blanco, se convirtió todo a minúsculas y se aplicó un mapeo para unificar todos los países bajo 7 nombres estándar: `argentina`, `brasil`, `chile`, `colombia`, `méxico`, `perú`, `uruguay`.

    **Impacto:** De 24 valores únicos se redujo a 7 países únicos. Filas sin cambios (7.251).
    """)

with st.expander("📌 7. Estandarización de planes (subscription_plan)"):
    st.markdown("""
    Se detectaron 13 valores únicos para 3 planes reales: `'Básico'`, `'BASICO'`, `'Basic'`, `'basico'`; `'Estándar'`, `'STANDARD'`, `'Std'`; `'Premium'`, `'PREMIUM'`, `'Premiun'` (mal escrito).

    **Acción:** Se limpiaron espacios en blanco y se aplicó un mapeo para unificar todos los planes bajo 3 nombres estándar: `'Básico'`, `'Estándar'`, `'Premium'`.

    **Impacto:** De 13 valores únicos se redujo a 3 planes únicos. Filas sin cambios (7.251).
    """)

with st.expander("📌 8. Estado final — guardado y log ETL"):
    st.markdown("""
    El dataset limpio se guarda en `data/processed/streaming_users_clean.json` preservando el original intacto en `data/raw/` para garantizar la reproducibilidad y auditoría del proceso.

    El log ETL registra cada transformación con su impacto en filas y nulos, permitiendo comparar el estado inicial y final de manera transparente.

    **Resultado final:**
    - Registros: 7.251 (de 8.160 originales, 88,9% de retención)
    - Nulos totales: 0
    - Variables categóricas estandarizadas: country (7), subscription_plan (3), favorite_genre (8, con 15 registros residuales pendientes)
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
            "01", "02", "03", "04", "05", "06", "07", "08"
        ],
        "Descripción": [
            "Dataset original cargado",
            "Eliminación de duplicados por user_id (keep=first)",
            "Estandarización y limpieza de fechas",
            "Filtrado de minutos de visualización (0-5.000 min)",
            "Reemplazo de nulos y estandarización de favorite_genre",
            "Filtrado de edades (4-95 años)",
            "Estandarización de países",
            "Estandarización de subscription_plan"
        ],
        "Filas": [
            8160, 8000, 7601, 7342, 7342, 7251, 7251, 7251
        ],
        "Nulos": [
            753, 753, 418, 227, 0, 0, 0, 0
        ],
        "Retención (%)": [
            100.0, 98.04, 93.15, 89.97, 89.97, 88.86, 88.86, 88.86
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