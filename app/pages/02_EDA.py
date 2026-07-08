import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.set_page_config(page_title="EDA", page_icon="📊", layout="wide")

st.title("📊 Análisis Exploratorio de Datos")
st.markdown("Cinco preguntas concretas respondidas con evidencia del dataset procesado.")
st.markdown("---")

# ── Carga ─────────────────────────────────────────────────────────────────────
@st.cache_data
def cargar():
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "streaming_users_clean.json")
    return pd.read_json(path)

try:
    df = cargar()
    datos_ok = True
except Exception:
    datos_ok = False
    st.error("No se encontró el dataset procesado en `data/processed/`.")
    st.stop()

sns.set_theme(style="darkgrid")

# Mostrar dimensiones del dataset
st.markdown(f"**Dataset procesado:** {df.shape[0]:,} registros · {df.shape[1]} variables")

# Derivar columna grupo_edad a partir de datos procesados
if "grupo_edad" not in df.columns:
    bins = [0, 17, 25, 35, 45, 60, 100]
    labels = ["<18", "18-25", "26-35", "36-45", "46-60", ">60"]
    df["grupo_edad"] = pd.cut(df["age"], bins=bins, labels=labels)

# ── Preguntas de análisis ──────────────────────────────────────────────────────
st.markdown("## Preguntas de análisis")
st.markdown("""
Este EDA busca responder cinco preguntas concretas sobre el comportamiento
de los usuarios de la plataforma de streaming, utilizando únicamente
datos estandarizados del dataset procesado:

1. **¿Cómo se distribuye la edad de los usuarios?**
2. **¿Qué plan de suscripción predomina en la plataforma?**
3. **¿El plan de suscripción se refleja en el consumo real de la plataforma?**
4. **¿Existe relación entre la edad y el tiempo de visualización?**
5. **¿Un país tiene más fijación que otro por cierto género de películas?**
""")
st.markdown("---")

# ── VIZ 1 — Distribución de edad (univariada) ─────────────────────────────────
st.markdown("## Viz 1 · Distribución de usuarios por grupo etario")
st.caption("Univariada · Pregunta 1")

conteo = df["grupo_edad"].value_counts().sort_index()

fig1, ax1 = plt.subplots(figsize=(8, 4))
bars = ax1.bar(
    conteo.index, conteo.values,
    color=sns.color_palette("Blues_d", len(conteo)),
    edgecolor="white"
)
for bar in bars:
    ax1.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 10,
        str(int(bar.get_height())),
        ha="center", va="bottom", fontsize=9
    )
ax1.set_title("Distribución de usuarios por grupo etario")
ax1.set_xlabel("Grupo de edad")
ax1.set_ylabel("Cantidad de usuarios")
plt.tight_layout()
st.pyplot(fig1)
plt.close(fig1)

col_t1, _ = st.columns([2, 1])
with col_t1:
    tabla_edades = pd.DataFrame({
        "Cantidad": df["grupo_edad"].value_counts().sort_index(),
        "Porcentaje (%)": round(df["grupo_edad"].value_counts(normalize=True).sort_index() * 100, 2)
    })
    st.dataframe(tabla_edades, use_container_width=True)

st.markdown("""
**Interpretación:** La distribución muestra que la base de usuarios es predominantemente adulta joven.
La mayor concentración se encuentra en el rango de 26 a 35 años, con presencia reducida
en los extremos. Esto condiciona cualquier decisión de segmentación posterior:
las estrategias orientadas al segmento 26-35 tienen mayor cobertura sobre la base de clientes.
""")
st.markdown("---")

# ── VIZ 2 — Distribución de planes (univariada) ───────────────────────────────
st.markdown("## Viz 2 · Distribución de planes de suscripción")
st.caption("Univariada · Pregunta 2")

conteo_planes = df["subscription_plan"].value_counts()

fig2, ax2 = plt.subplots(figsize=(6, 4))
bars2 = ax2.barh(
    conteo_planes.index, conteo_planes.values,
    color=sns.color_palette("Blues_d", len(conteo_planes)),
    edgecolor="white"
)
total = conteo_planes.sum()
for bar, val in zip(bars2, conteo_planes.values):
    ax2.text(
        bar.get_width() + 15,
        bar.get_y() + bar.get_height() / 2,
        f"{val / total * 100:.1f}%",
        va="center", fontsize=9
    )
ax2.set_title("Distribución de planes de suscripción")
ax2.set_xlabel("Cantidad de usuarios")
ax2.set_ylabel("Plan")
plt.tight_layout()
st.pyplot(fig2)
plt.close(fig2)

col_t2, _ = st.columns([2, 1])
with col_t2:
    tabla_planes = pd.DataFrame({
        "Cantidad": df["subscription_plan"].value_counts(),
        "Porcentaje (%)": round(df["subscription_plan"].value_counts(normalize=True) * 100, 2)
    })
    tabla_planes.index.name = "Plan de suscripción"
    st.dataframe(tabla_planes, use_container_width=True)

st.markdown("""
**Interpretación:** El plan básico es el más utilizado, representando aproximadamente el 46%
de la base de usuarios. Este resultado establece al segmento básico como la referencia
principal para comparaciones entre planes en el análisis bivariado.
""")
st.markdown("---")

# ── VIZ 3 — Consumo por plan (bivariada) ──────────────────────────────────────
st.markdown("## Viz 3 · Consumo mensual de minutos por plan de suscripción")
st.caption("Bivariada · Pregunta 3")

orden = ["Básico", "Estándar", "Premium"]

fig3, ax3 = plt.subplots(figsize=(8, 4))
sns.boxplot(
    data=df, x="subscription_plan", y="monthly_watch_time_mins",
    order=orden, palette="Blues", hue="subscription_plan", legend=False,
    width=0.5, linewidth=1.2,
    flierprops=dict(marker="o", markersize=3, alpha=0.3),
    ax=ax3
)
ax3.set_title("Consumo mensual de minutos por plan de suscripción")
ax3.set_xlabel("Plan de suscripción")
ax3.set_ylabel("Minutos mensuales")
plt.tight_layout()
st.pyplot(fig3)
plt.close(fig3)

col_t3, _ = st.columns([2, 1])
with col_t3:
    resumen = (
        df.groupby("subscription_plan")["monthly_watch_time_mins"]
        .agg(Cantidad="count", Promedio="mean", Mediana="median", Minimo="min", Maximo="max")
        .round(2)
    )
    st.dataframe(resumen, use_container_width=True)

st.markdown("""
**Interpretación:** El análisis bivariado mostró que el consumo mensual de minutos crece
de forma consistente de básico a estándar y de estándar a premium.
Los usuarios premium presentan una mediana de minutos claramente superior
a los otros dos planes, lo que sugiere que el tipo de suscripción contratada
se refleja en el uso real de la plataforma. Sin embargo, la dispersión
dentro de cada plan es considerable, lo que indica que el plan no explica
por sí solo el comportamiento de visualización.
""")
st.markdown("---")

# ── VIZ 4 — Edad vs Minutos Visualizados (bivariada) ──────────────────────────
st.markdown("## Viz 4 · Relación entre Edad y Minutos Visualizados")
st.caption("Bivariada · Pregunta 4")

# Calcular promedio por rango de edad
avg_by_age = df.groupby("grupo_edad")["monthly_watch_time_mins"].mean().reset_index()

fig4, ax4 = plt.subplots(figsize=(10, 5))
bars4 = ax4.bar(
    avg_by_age["grupo_edad"], 
    avg_by_age["monthly_watch_time_mins"],
    color=sns.color_palette("Blues_d", len(avg_by_age)),
    edgecolor="white"
)
for bar, val in zip(bars4, avg_by_age["monthly_watch_time_mins"]):
    ax4.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 10,
        f"{val:.0f} min",
        ha="center", va="bottom", fontsize=9
    )
ax4.set_title("Promedio de Minutos Visualizados por Rango de Edad")
ax4.set_xlabel("Grupo de Edad")
ax4.set_ylabel("Promedio de Minutos Visualizados al Mes")
plt.tight_layout()
st.pyplot(fig4)
plt.close(fig4)

correlacion_edad_consumo = df["age"].corr(df["monthly_watch_time_mins"])
st.metric("Correlación de Pearson (edad vs minutos)", f"{correlacion_edad_consumo:.3f}")

col_t4, _ = st.columns([2, 1])
with col_t4:
    tabla_edad_consumo = (
        df.groupby("grupo_edad")["monthly_watch_time_mins"]
        .agg(Cantidad="count", Promedio="mean", Mediana="median")
        .round(2)
    )
    st.dataframe(tabla_edad_consumo, use_container_width=True)

st.markdown("""
**Interpretación:** La correlación de Pearson entre edad y minutos visualizados es de **0.006**,
prácticamente nula. El promedio de minutos visualizados se mantiene estable en todos los rangos
etarios (entre 776 y 809 minutos mensuales), sin una tendencia de crecimiento o caída asociada
a la edad. La hipótesis de que los usuarios de mayor edad consumen más contenido **no encuentra
respaldo en los datos**: la edad y el consumo mensual son, en la práctica, variables independientes
entre sí.
""")
st.markdown("---")

# ── VIZ 5 — Preferencia de género por país (multivariada) ─────────────────────
st.markdown("## Viz 5 · Preferencia de Género por País")
st.caption("Multivariada · Pregunta 5")

# Crear tabla de contingencia
genero_pais = pd.crosstab(df["country"], df["favorite_genre"])

fig5, ax5 = plt.subplots(figsize=(14, 8))
sns.heatmap(
    genero_pais, 
    annot=True, 
    fmt="d", 
    cmap="YlOrRd",
    linewidths=0.5, 
    linecolor="white",
    ax=ax5
)
ax5.set_title("Preferencia de Género por País", fontsize=14)
ax5.set_xlabel("Género Favorito")
ax5.set_ylabel("País")
plt.tight_layout()
st.pyplot(fig5)
plt.close(fig5)

col_t5, _ = st.columns([2, 1])
with col_t5:
    st.dataframe(genero_pais, use_container_width=True)

# Top 3 géneros por país
st.markdown("### Top 3 géneros por país")
for pais in genero_pais.index:
    top_generos = genero_pais.loc[pais].sort_values(ascending=False).head(3)
    st.markdown(f"**{pais.capitalize()}:**")
    for genero, count in top_generos.items():
        pct = (count / genero_pais.loc[pais].sum() * 100)
        st.markdown(f"  - {genero}: {count} usuarios ({pct:.1f}%)")

st.markdown("""
**Interpretación:** La distribución de `favorite_genre` es, en términos generales, bastante pareja
tanto a nivel global como dentro de cada país: los ocho géneros representan entre 13% y 17% de las
preferencias en cada mercado, y la diferencia entre el género más elegido y el segundo dentro de un
mismo país es de apenas 1 a 2 puntos porcentuales (ver tabla de arriba). Esto significa que, si bien
existe un género "líder" por país, no hay una preferencia dominante o marcadamente diferenciada como
para hablar de patrones culturales fuertes: la variación observada es moderada y podría deberse en
parte a variabilidad muestral.

Con esa salvedad, los géneros más elegidos por país son:
- **Argentina:** Drama y Comedia
- **Brasil:** Comedia y Thriller
- **Chile:** Crimen y Acción
- **Colombia:** Comedia y Thriller
- **México:** Acción y Comedia
- **Perú:** Romance y Drama
- **Uruguay:** Drama y Romance

Antes de usar estas diferencias para decisiones de catálogo por mercado, sería conveniente
confirmar que son estadísticamente significativas (por ejemplo con un test de chi-cuadrado)
y no solo variación esperable dado el tamaño de cada muestra.
""")
st.markdown("---")

st.markdown("---")
st.caption(f"EDA · 5 visualizaciones · {df.shape[0]:,} registros procesados")