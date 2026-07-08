# 🎬 Proyecto Integrador — Minería de Datos 1

Análisis de usuarios de una plataforma de streaming aplicando técnicas de Minería de Datos.

## 👥 Integrantes

- Vega Orellana, Ignacio Rodolfo
- Romano Arnoux, Bruno Leonel

## 📋 Descripción

Este proyecto construye un pipeline de análisis reproducible sobre un dataset de usuarios de streaming, cubriendo:

1. **Inspección inicial** — identificación de nulos, tipos incorrectos y valores imposibles
2. **Calidad y limpieza** — pipeline ETL con decisiones documentadas y justificadas
3. **EDA** — cinco preguntas de análisis respondidas con visualizaciones
4. **PCA** — escalamiento, reducción de dimensionalidad e interpretación de componentes
5. **Conclusiones** — hallazgos, limitaciones y próximos pasos

## 🗂 Estructura del repositorio

```
PI_Mineria_Datos_1/
├── app/                        # Aplicación Streamlit
│   ├── Home.py                 # Página principal
│   └── pages/
│       ├── 01_Dataset.py       # Inspección y limpieza
│       ├── 02_EDA.py           # Análisis exploratorio
│       ├── 03_PCA.py           # PCA y reducción
│       └── 04_Conclusiones.py  # Conclusiones
├── data/
│   ├── raw/                    # Dataset original
│   └── processed/              # Dataset limpio
├── logs/
│   └── pipeline_log.csv        # Log ETL paso a paso
├── notebooks/
│   ├── 01_inspeccion_inicial.ipynb
│   ├── 02_calidad_y_limpieza.ipynb
│   ├── 03_eda.ipynb
│   ├── 04_pca.ipynb
│   └── 05_conclusiones.ipynb
└── requirements.txt
```

## 🚀 Ejecución local

```
pip install -r requirements.txt
streamlit run app/Home.py
```

## 🌐 Aplicación en la nube

[🚀 Ver en Streamlit Cloud](https://pimineriadedatos01.streamlit.app)

## 📦 Dependencias

- `streamlit` — aplicación web interactiva
- `pandas` — manipulación de datos
- `numpy` — operaciones numéricas
- `matplotlib` / `seaborn` — visualizaciones
- `scikit-learn` — escalamiento y PCA

---
Minería de Datos 1
