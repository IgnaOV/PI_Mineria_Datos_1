import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Conclusiones — PI Minería de Datos",
    page_icon="📝",
    layout="wide",
)

st.title("📝 Conclusiones")
st.markdown("Hallazgos del análisis, limitaciones del proyecto y próximos pasos.")
st.markdown("---")

# ── 1. Resumen del proceso ──────────────────────────────────────────────────
st.markdown("## 1. Resumen del proceso")

st.markdown("""
Este proyecto analizó un dataset de usuarios de una plataforma de streaming
que contenía **8.160 registros** y **8 variables originales**. A lo largo de cinco
etapas se construyó un pipeline reproducible que va desde la inspección
inicial hasta la reducción de dimensionalidad.

El proceso siguió el siguiente orden:

- **Inspección inicial**: se identificaron nulos en tres columnas, tipo de dato
  incorrecto en `last_login_date`, valores imposibles en `age` y
  `monthly_watch_time_mins`, y duplicados.
- **Limpieza y preparación**: se tomaron decisiones justificadas por evidencia
  en cada variable, conservando el dataset original intacto y registrando
  cada transformación en el log ETL.
- **EDA**: se respondieron cinco preguntas concretas sobre el comportamiento
  de los usuarios mediante análisis univariado, bivariado y multivariado.
- **PCA**: se aplicó reducción de dimensionalidad sobre las tres variables
  numéricas (`age`, `monthly_watch_time_mins`, `customer_support_tickets`),
  documentando el escalamiento, la varianza explicada y la interpretación
  de los loadings.
""")

# ── Resumen del dataset ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## Resumen del dataset")

col1, col2, col3 = st.columns(3)
col1.metric("Registros originales", "8,160")
col2.metric("Registros después de limpieza", "7,251")
col3.metric("Registros eliminados", "818")

st.caption("Se eliminaron registros con valores imposibles, fechas futuras, edades fuera de rango (4-95 años) y se imputaron valores nulos de manera justificada.")

# ── 2. Hallazgos principales ──────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 2. Hallazgos principales")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Sobre el perfil de los usuarios")
    st.markdown("""
    La base de usuarios es predominantemente adulta joven, con una edad
    promedio de **34.5 años** y una mediana de **33 años**. El grupo con mayor
    concentración se encuentra entre los **20 y 40 años**, con muy pocos
    usuarios en los extremos de edad (menores de 4 años o mayores de 95).

    El **plan Básico** es el más frecuente, representando aproximadamente
    el **46%** de la base de usuarios, seguido por el plan Estándar con el
    **31%** y el Premium con el **23%**. Esto sugiere que la mayoría de los
    usuarios accede al nivel de servicio más elemental, lo que podría
    indicar sensibilidad al precio.
    """)

    st.markdown("### Sobre la distribución geográfica")
    st.markdown("""
    **Argentina y Brasil** son los mercados más importantes para la
    plataforma, concentrando la mayor cantidad de suscripciones con
    aproximadamente **2.500** y **2.400** usuarios respectivamente.
    México le sigue con cerca de **2.100** usuarios, mientras que Perú,
    Colombia, Chile y Uruguay completan el listado con cifras decrecientes.

    Las preferencias de género varían significativamente según el país:
    - **Argentina**: Drama y Thriller son los géneros más populares
    - **Brasil**: Romance y Comedia tienen fuerte preferencia
    - **México**: Comedia y Acción son los favoritos
    - **Chile y Perú**: Drama y Comedia predominan
    - **Colombia**: Distribución más equilibrada entre géneros
    - **Uruguay**: Documentales y Comedia son los más vistos
    """)

with col2:
    st.markdown("### Sobre el consumo por edad")
    st.markdown("""
    La relación entre la edad y el tiempo de visualización mensual revela
    una **tendencia clara**: los usuarios de mayor edad tienden a consumir
    más contenido. El coeficiente de correlación positivo, aunque moderado,
    indica que a medida que aumenta la edad, también lo hace la cantidad de
    minutos visualizados al mes.

    El **pico de consumo** se observa en el rango de **45 a 54 años**, donde
    los usuarios superan los **1000 minutos mensuales** en promedio. Los
    usuarios más jóvenes, especialmente aquellos menores de 20 años, son
    los que menos contenido consumen.
    """)

    st.markdown("### Sobre la estructura del dataset")
    st.markdown("""
    La matriz de correlación del EDA mostró **coeficientes cercanos a cero**
    entre todas las variables numéricas. Este resultado fue confirmado por el PCA:
    las tres componentes principales explican proporciones casi idénticas
    de varianza:
    - **PC1**: 33.68%
    - **PC2**: 33.42%
    - **PC3**: 32.90%

    Las variables describen **dimensiones independientes** del comportamiento
    del usuario y no presentan redundancia entre sí. Esto significa que la
    edad, el consumo y los problemas técnicos son aspectos distintos y
    complementarios del perfil del usuario.
    """)

# ── 3. Interpretación del PCA ─────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 3. Interpretación del PCA")

st.markdown("""
**PC1 — Calidad de Experiencia (33.68%)**
- `monthly_watch_time_mins`: **+0.74** (contribución fuerte, positiva)
- `customer_support_tickets`: **-0.62** (contribución fuerte, negativa)
- `age`: **+0.26** (contribución baja, positiva)

Los usuarios con valores altos en PC1 son aquellos que **ven más minutos,
tienen mayor edad y reportan menos problemas**. Por el contrario, los
usuarios con valores bajos en PC1 son aquellos que **ven menos contenido,
son más jóvenes y tienen más tickets de soporte**.

**PC2 — Perfil Etario (33.42%)**
- `age`: **+0.86** (contribución muy fuerte, positiva)
- `customer_support_tickets`: **+0.50** (contribución media, positiva)
- `monthly_watch_time_mins`: **+0.12** (contribución baja, positiva)

Los usuarios con valores altos en PC2 son **personas mayores**, que además
tienden a tener más tickets de soporte. Los usuarios con valores bajos en
PC2 son **personas más jóvenes**, con menos tickets.

**Conclusión del PCA**

El resultado más relevante del PCA no es la reducción de dimensionalidad
en sí —que en este caso no es posible sin pérdida significativa—, sino
la confirmación de que las tres variables aportan información
independiente y complementaria sobre el usuario.

Retener 2 componentes implicaría conservar solo el **67.1%** de la información
original. Para capturar el **100%** se requieren las 3 componentes originales.
En conjunto, el análisis confirma que la edad, el consumo y los problemas
técnicos son dimensiones separadas del comportamiento del usuario.
""")

# ── 4. Limitaciones ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 4. Limitaciones")

st.markdown("""
El alcance de las conclusiones se encuentra condicionado por la información
disponible y por las decisiones documentadas durante el proceso.

1. **Alcance geográfico limitado**: El análisis se centra en 7 países
   latinoamericanos, por lo que los resultados pueden no ser generalizables
   a otras regiones.

2. **Datos temporales**: Se trabajó con datos de un solo momento
   (corte transversal), sin información de evolución temporal del
   comportamiento de los usuarios.

3. **Datos faltantes**: Algunos registros fueron imputados o eliminados,
   lo que podría introducir sesgos en el análisis. Se imputaron 22 registros
   en `favorite_genre` con "Sin género favorito" y 15 registros en
   `monthly_watch_time_mins` con la mediana.

4. **Variables limitadas**: El análisis se basa en 8 variables. Incorporar
   más variables (como tipo de dispositivo, horario de visualización, etc.)
   podría enriquecer el análisis.

5. **PCA con 3 variables**: El PCA se aplicó solo a 3 variables numéricas,
   lo que limita la capacidad de reducción de dimensionalidad. Las variables
   no están correlacionadas, por lo que no es posible reducir dimensiones
   sin pérdida significativa de información.

6. **Género favorito declarado**: La variable `favorite_genre` se basa en
   preferencia declarada, no en consumo real, lo que puede introducir sesgo
   entre lo que el usuario dice preferir y lo que realmente ve.
""")

# ── 5. Referencias del proyecto ─────────────────────────────────────────────
st.markdown("---")
st.markdown("## 5. Referencias del proyecto")

col_r1, col_r2 = st.columns(2)

with col_r1:
    st.markdown("""
    **Repositorio GitHub**
    🔗 [Ver repositorio](https://github.com/IgnaOV/PI_Mineria_Datos_1)

    **Aplicación Streamlit Cloud**
    🔗 [Ver aplicación pública](https://pimineriadedatos01.streamlit.app)
    """)

with col_r2:
    st.markdown("""
    **Notebooks**
    - `01_inspeccion_inicial.ipynb`
    - `02_calidad_y_limpieza.ipynb`
    - `03_eda.ipynb`
    - `04_pca.ipynb`
    - `05_conclusiones.ipynb`
    """)

st.markdown("---")
st.caption("Vega Orellana Ignacio - Romano Arnoux Bruno · Minería de Datos 1 · Facultad de Ingeniería")