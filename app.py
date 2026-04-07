import streamlit as st
import pandas as pd
import pyodbc
import plotly.graph_objects as go

# ==============================
# 🧠 FUNCIONES AUXILIARES (SOPORTE VISUAL - NO CAPA)
# ==============================
# Estas funciones apoyan la visualización (frontend), no pertenecen a una capa de datos

def formatear_texto(texto):
    lineas = texto.split("\n")
    lineas_limpias = [line.strip() for line in lineas if line.strip() != ""]
    return "<br><br>".join(lineas_limpias)

def estilo_plotly(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified",
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    return fig

# ==============================
# ⚙ CONFIGURACIÓN GENERAL (PRESENTACIÓN - NO CAPA)
# ==============================

st.set_page_config(
    page_title="BI Educación Bolivia",
    layout="wide",
    page_icon="📊"
)

# ==============================
# 🎨 CSS (CAPA DE PRESENTACIÓN)
# ==============================

def load_css():
    with open("estilo.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ==============================
# 🥉 CAPA BRONZE (INGESTA DE DATOS)
# ==============================
# Aquí se conecta a la fuente de datos (SQL Server)
# Representa datos crudos provenientes del sistema transaccional

server = r'localhost\SQLEXPRESS'
database = 'BI_Educacion'
driver = 'ODBC Driver 17 for SQL Server'

conn = pyodbc.connect(
    f'DRIVER={{{driver}}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    'Trusted_Connection=yes;'
)

# ==============================
# 🥇 CAPA GOLD (MODELO ANALÍTICO)
# ==============================
# Consulta optimizada sobre modelo estrella
# Aquí ya trabajamos con datos estructurados para análisis (HECHOS + DIMENSIONES)

query = """
SELECT 
    t.anio,
    c.desempleo,
    c.tic,
    COUNT(*) AS total_estudiantes,
    SUM(CASE WHEN h.estado_empleo = 'Empleado' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) 
    AS tasa_empleabilidad
FROM HECHO_EMPLEABILIDAD h
JOIN DIM_TIEMPO t ON h.id_tiempo = t.id_tiempo
JOIN CEPAL_INDICADORES c ON t.anio = c.anio
GROUP BY t.anio, c.desempleo, c.tic
ORDER BY t.anio
"""

df = pd.read_sql(query, conn)

# ==============================
# 🥈 CAPA SILVER (TRANSFORMACIÓN / FILTRO)
# ==============================
# Aquí se aplican filtros dinámicos y preparación de datos para análisis

st.sidebar.header("🎛 Filtros")

anio_min, anio_max = int(df["anio"].min()), int(df["anio"].max())

rango = st.sidebar.slider(
    "Selecciona rango de años",
    anio_min,
    anio_max,
    (anio_min, anio_max)
)

# Dataset limpio y preparado para visualización
df_filtrado = df[(df["anio"] >= rango[0]) & (df["anio"] <= rango[1])]

# ==============================
# 🖥 CAPA DE PRESENTACIÓN (DASHBOARD)
# ==============================

# HEADER
st.markdown("""
<div class="header">
    <h1>📊 Educación y Brecha Digital Laboral</h1>
    <p>Análisis estratégico de empleabilidad, desempleo y habilidades TIC en Bolivia</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==============================
# 🧠 VISUALIZACIÓN DE ARQUITECTURA (EXPLICACIÓN)
# ==============================

st.subheader("🏗️ Arquitectura de Datos (Medallion)")

st.markdown("""
<div class="insight-card">
    <div class="insight-title">🔹 Capa Bronze (Ingesta)</div>
    <div class="insight-text">
    Extracción de datos desde SQL Server y fuentes externas (CEPALSTAT).
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="insight-card">
    <div class="insight-title">🔹 Capa Silver (Transformación)</div>
    <div class="insight-text">
    Limpieza, filtrado dinámico y preparación de datos para análisis.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="insight-card">
    <div class="insight-title">🔹 Capa Gold (Modelo Analítico)</div>
    <div class="insight-text">
    Modelo estrella optimizado para generación de KPIs y análisis estratégico.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==============================
# 📊 KPIs (CAPA GOLD - CONSUMO DE NEGOCIO)
# ==============================

st.subheader("📌 Indicadores Clave")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Empleabilidad Promedio", f"{df_filtrado['tasa_empleabilidad'].mean():.2f}%")

with col2:
    st.metric("Desempleo Promedio", f"{df_filtrado['desempleo'].mean():.2f}%")

with col3:
    st.metric("Nivel TIC Promedio", f"{df_filtrado['tic'].mean():.2f}%")

# KPI estratégico derivado (análisis avanzado)
brecha = df_filtrado["tic"] - df_filtrado["tasa_empleabilidad"]
st.metric("📉 Brecha Digital Laboral", f"{brecha.mean():.2f}")

st.markdown("---")

# ==============================
# 📈 VISUALIZACIONES (CAPA GOLD → PRESENTACIÓN)
# ==============================

st.subheader("📈 Evolución de la Empleabilidad")

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=df_filtrado["anio"],
    y=df_filtrado["tasa_empleabilidad"],
    mode="lines+markers",
    line=dict(color="#4cc9f0", width=3, shape="spline")
))

st.plotly_chart(estilo_plotly(fig1), use_container_width=True)

st.markdown("---")

# ==============================
# 📊 COMPARACIONES ESTRATÉGICAS
# ==============================

st.subheader("📊 Brecha Digital vs Mercado Laboral")

col1, col2 = st.columns(2)

with col1:
    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=df_filtrado["anio"],
        y=df_filtrado["tic"],
        name="Nivel TIC",
        line=dict(color="#ff4ecd", width=3, shape="spline")
    ))

    fig2.add_trace(go.Scatter(
        x=df_filtrado["anio"],
        y=df_filtrado["tasa_empleabilidad"],
        name="Empleabilidad",
        line=dict(color="#4cc9f0", width=3, shape="spline")
    ))

    st.plotly_chart(estilo_plotly(fig2), use_container_width=True)

with col2:
    fig3 = go.Figure()

    fig3.add_trace(go.Scatter(
        x=df_filtrado["anio"],
        y=df_filtrado["desempleo"],
        name="Desempleo",
        line=dict(color="#f72585", width=3, shape="spline")
    ))

    fig3.add_trace(go.Scatter(
        x=df_filtrado["anio"],
        y=df_filtrado["tasa_empleabilidad"],
        name="Empleabilidad",
        line=dict(color="#4cc9f0", width=3, shape="spline")
    ))

    st.plotly_chart(estilo_plotly(fig3), use_container_width=True)

st.markdown("---")

# ==============================
# 🎯 ANÁLISIS DE RELACIÓN (INSIGHT DATA)
# ==============================

st.subheader("🎯 Relación entre TIC y Empleabilidad")

fig4 = go.Figure()
fig4.add_trace(go.Scatter(
    x=df_filtrado["tic"],
    y=df_filtrado["tasa_empleabilidad"],
    mode="markers+text",
    text=df_filtrado["anio"],
    marker=dict(color="#ff4ecd", size=10)
))

st.plotly_chart(estilo_plotly(fig4), use_container_width=True)

st.markdown("---")

# ==============================
# 🧠 INSIGHTS (CAPA DE VALOR DE NEGOCIO)
# ==============================

st.subheader("🧠 Insights Estratégicos")

corr_tic = df_filtrado["tic"].corr(df_filtrado["tasa_empleabilidad"])
corr_des = df_filtrado["desempleo"].corr(df_filtrado["tasa_empleabilidad"])

anio_inicio = int(df_filtrado["anio"].min())
anio_fin = int(df_filtrado["anio"].max())

# INSIGHT 1
insight_tic = f"""
Durante el periodo {anio_inicio}-{anio_fin}, la relación entre TIC y empleabilidad (corr: {corr_tic:.2f}) permite identificar el nivel de alineación entre habilidades digitales y mercado laboral.
"""

# INSIGHT 2
insight_des = f"""
Durante el mismo periodo, la relación entre desempleo y empleabilidad (corr: {corr_des:.2f}) refleja las condiciones estructurales del mercado laboral.
"""

# INSIGHT 3
insight_general = f"""
El análisis evidencia que la empleabilidad depende de múltiples factores y no únicamente del acceso a tecnología.
"""

st.markdown(f"""
<div class="insight-card">
<div class="insight-title">💻 Brecha Digital</div>
<div class="insight-text">{formatear_texto(insight_tic)}</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="insight-card">
<div class="insight-title">📉 Mercado Laboral</div>
<div class="insight-text">{formatear_texto(insight_des)}</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="insight-card">
<div class="insight-title">🧠 Lectura Global</div>
<div class="insight-text">{formatear_texto(insight_general)}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==============================
# 🌆 REFLEXIÓN FINAL (DECISIÓN)
# ==============================

mensaje_final = """
El valor del BI no está en los datos, sino en las decisiones que permite tomar.
"""

st.markdown(f"""
<div class="insight-card">
<div class="insight-title">🌆 Reflexión Final</div>
<div class="insight-text">{formatear_texto(mensaje_final)}</div>
</div>
""", unsafe_allow_html=True)