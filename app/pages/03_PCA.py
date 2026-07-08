import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os

st.set_page_config(
    page_title="PCA — PI Minería de Datos",
    page_icon="🔷",
    layout="wide",
)

st.title("🔷 Escalamiento y PCA")
st.markdown("Reducción de dimensionalidad e interpretación de componentes principales.")
st.markdown("---")

# ── Carga de datos ──────────────────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "streaming_users_clean.json")
    return pd.read_json(path)

try:
    df = cargar_datos()
except Exception:
    st.error("No se encontró el dataset procesado en `data/processed/`.")
    st.stop()

sns.set_theme(style="darkgrid")

# ── Resumen del dataset ──────────────────────────────────────────────────────
st.markdown("### Resumen del dataset")

col1, col2, col3 = st.columns(3)
col1.metric("Registros originales", "8,160")
col2.metric("Registros después de limpieza", f"{len(df):,}")
col3.metric("Registros eliminados", f"{8160 - len(df):,}")

st.caption("Se eliminaron registros con valores imposibles, fechas futuras y edades fuera de rango (4-95 años).")

# ── 1. Variables utilizadas ──────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 1. Variables utilizadas")

st.markdown("""
Se seleccionaron las **3 variables numéricas** del dataset:
- `age` — Edad del usuario
- `monthly_watch_time_mins` — Minutos visualizados en el mes
- `customer_support_tickets` — Tickets de atención al cliente

Estas variables describen dimensiones distintas del comportamiento del usuario:
perfil demográfico, consumo y experiencia técnica. Las variables categóricas
como `subscription_plan`, `country` y `favorite_genre` fueron excluidas
porque PCA opera exclusivamente sobre variables numéricas.
""")

variables = ["age", "monthly_watch_time_mins", "customer_support_tickets"]
X = df[variables]

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Variables incluidas**")
    vars_df = pd.DataFrame({
        "Variable": variables,
        "Descripción": [
            "Edad del usuario",
            "Minutos vistos en el mes",
            "Tickets de atención al cliente"
        ]
    })
    st.dataframe(vars_df, use_container_width=True, hide_index=True)

with col2:
    st.markdown("**Estadísticas antes de escalar**")
    st.dataframe(X.describe().round(2), use_container_width=True)

# ── 2. Escalamiento ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 2. Escalamiento — StandardScaler")

st.markdown("""
Antes de aplicar PCA es **obligatorio escalar las variables**. PCA es
sensible a la magnitud de cada variable: sin escalar, `monthly_watch_time_mins`
(que puede superar los 4000 minutos) dominaría completamente el análisis
sobre `customer_support_tickets` (que rara vez supera 5), simplemente
por diferencia de escala y no por importancia real.

Se aplica `StandardScaler`, que transforma cada variable para que tenga
**media 0 y desvío estándar 1**, haciendo que todas contribuyan en igualdad
de condiciones al análisis.
""")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

verificacion = pd.DataFrame({
    "Variable": variables,
    "Media post-escalado": X_scaled.mean(axis=0).round(6),
    "Desvío post-escalado": X_scaled.std(axis=0).round(4)
})
st.dataframe(verificacion, use_container_width=True, hide_index=True)
st.caption("Las medias son aproximadamente 0 y los desvíos aproximadamente 1, confirmando el escalamiento correcto.")

# ── 3. PCA y varianza explicada ─────────────────────────────────────────────
st.markdown("---")
st.markdown("## 3. Aplicación de PCA y varianza explicada")

st.markdown("""
Aplicamos PCA con todas las componentes posibles (3, una por variable)
para observar cuánta varianza explica cada una antes de decidir cuántas
retener. La varianza explicada por cada componente indica cuánta
información del dataset original captura esa dimensión reducida.
""")

pca = PCA(n_components=3)
X_pca = pca.fit_transform(X_scaled)

varianza = pca.explained_variance_ratio_
varianza_acumulada = np.cumsum(varianza)

resumen_pca = pd.DataFrame({
    "Componente": [f"PC{i+1}" for i in range(3)],
    "Varianza explicada (%)": (varianza * 100).round(2),
    "Varianza acumulada (%)": (varianza_acumulada * 100).round(2)
})

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("PC1", f"{varianza[0]*100:.1f}%")
col_m2.metric("PC2", f"{varianza[1]*100:.1f}%")
col_m3.metric("PC3", f"{varianza[2]*100:.1f}%")

st.dataframe(resumen_pca, use_container_width=True, hide_index=True)

# ── VIZ 1 — Scree plot ──────────────────────────────────────────────────────
st.markdown("### Viz 1 · Varianza explicada por componente principal")

st.markdown("""
El scree plot muestra que las tres componentes principales explican
proporciones casi idénticas de varianza: **PC1 (33.7%)**, **PC2 (33.4%)**
y **PC3 (32.9%)**. La varianza acumulada crece de forma perfectamente
lineal, sin ningún quiebre o codo visible.

Este resultado confirma lo observado en el análisis exploratorio:
**las tres variables no están correlacionadas entre sí**, por lo que cada
una aporta información independiente. PCA no encuentra ninguna dirección
que concentre más información que las demás, y en consecuencia no permite
una reducción de dimensionalidad sin pérdida significativa.

Retener 2 componentes implicaría conservar solo el **67.1%** de la información
original. Para capturar el **100%** se requieren las 3 componentes originales.
""")

componentes = [f"PC{i+1}" for i in range(3)]

fig1, ax1 = plt.subplots(figsize=(8, 5))
ax1.bar(
    componentes, varianza * 100,
    color=['#3498db', '#2ecc71', '#e74c3c'],
    edgecolor="white", alpha=0.8, label="Varianza individual"
)

ax2 = ax1.twinx()
ax2.plot(
    componentes, varianza_acumulada * 100,
    color="darkblue", marker="o", linewidth=2.5, markersize=10,
    label="Varianza acumulada"
)
ax2.set_ylabel("Varianza acumulada (%)", fontsize=12)
ax2.set_ylim(0, 110)

for i, v in enumerate(varianza * 100):
    ax1.text(i, v + 1.5, f"{v:.1f}%", ha="center", fontsize=11, fontweight="bold")

for i, v in enumerate(varianza_acumulada * 100):
    ax2.text(i, v + 2, f"{v:.1f}%", ha="center", fontsize=9, color="darkblue")

ax1.axhline(y=80, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='80% de varianza')
ax1.set_title("Varianza explicada por componente principal", fontsize=15)
ax1.set_xlabel("Componente", fontsize=12)
ax1.set_ylabel("Varianza explicada (%)", fontsize=12)
ax1.set_ylim(0, 45)
ax1.legend(loc="upper left", fontsize=10)
plt.tight_layout()
st.pyplot(fig1)
plt.close(fig1)

# ── VIZ 2 — Loadings ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Viz 2 · Contribución de variables a PC1 y PC2 (loadings)")

loadings = pd.DataFrame(
    pca.components_.T,
    index=variables,
    columns=[f"PC{i+1}" for i in range(3)]
)

x = np.arange(len(variables))
width = 0.35

fig2, ax3 = plt.subplots(figsize=(10, 5))
bars1 = ax3.bar(x - width/2, loadings["PC1"], width,
                color='steelblue', label="PC1", edgecolor="black")
bars2 = ax3.bar(x + width/2, loadings["PC2"], width,
                color='coral', label="PC2", edgecolor="black")
ax3.axhline(0, color="gray", linewidth=0.8, linestyle="--")
ax3.set_xticks(x)
ax3.set_xticklabels(["age", "watch_mins", "tickets"], fontsize=11)
ax3.set_title("Contribución de variables a PC1 y PC2", fontsize=15)
ax3.set_ylabel("Loadings", fontsize=12)
ax3.set_ylim(-1, 1)
ax3.legend(fontsize=11, loc="upper right")

for i, w in enumerate(loadings["PC1"]):
    ax3.text(i - width/2, w + (0.05 if w >= 0 else -0.1), f"{w:.2f}", 
             ha='center', fontsize=9, fontweight='bold')

for i, w in enumerate(loadings["PC2"]):
    ax3.text(i + width/2, w + (0.05 if w >= 0 else -0.1), f"{w:.2f}", 
             ha='center', fontsize=9, fontweight='bold')

plt.tight_layout()
st.pyplot(fig2)
plt.close(fig2)

st.markdown("**Tabla de loadings completa**")
st.dataframe(loadings.round(4), use_container_width=True)

# ── 4. Interpretación general ─────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 4. Interpretación general")

st.markdown("""
**PC1 — Calidad de Experiencia (33.68%)**
- `monthly_watch_time_mins`: **+0.74** (contribución fuerte, positiva)
- `customer_support_tickets`: **-0.62** (contribución fuerte, negativa)
- `age`: **+0.26** (contribución baja, positiva)

Los usuarios con valores altos en PC1 son aquellos que **ven más minutos, tienen mayor edad y reportan menos problemas**. Por el contrario, los usuarios con valores bajos en PC1 son aquellos que **ven menos contenido, son más jóvenes y tienen más tickets de soporte**.

**PC2 — Perfil Etario (33.42%)**
- `age`: **+0.86** (contribución muy fuerte, positiva)
- `customer_support_tickets`: **+0.50** (contribución media, positiva)
- `monthly_watch_time_mins`: **+0.12** (contribución baja, positiva)

Los usuarios con valores altos en PC2 son **personas mayores**, que además tienden a tener más tickets de soporte. Los usuarios con valores bajos en PC2 son **personas más jóvenes**, con menos tickets.
""")

st.info("""
**Conclusión del PCA**

Las tres variables describen aspectos distintos e independientes del comportamiento del usuario.
PCA no puede comprimir el dataset sin pérdida significativa de información.

- Retener 2 componentes = 67.1% de información
- Retener 3 componentes = 100% de información

El resultado relevante no es la reducción de dimensionalidad en sí, sino entender
qué estructura captura cada componente: **calidad de experiencia (PC1)** y
**perfil etario (PC2)**.

En conjunto, el análisis confirma que la edad, el consumo y los problemas
técnicos son dimensiones separadas del comportamiento del usuario, por lo que
para futuros análisis resulta más apropiado trabajar con las variables originales
en lugar de utilizar componentes principales.
""")

st.caption("PCA · 3 variables · 7,251 registros · Proyecto Integrador Minería de Datos 1")