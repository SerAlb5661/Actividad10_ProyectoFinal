import streamlit as st
import pandas as pd
import pyodbc
import plotly.graph_objects as go

# ==============================
# FUNCIONES AUXILIARES
# ==============================
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
# CONFIGURACIÓN GENERAL
# ==============================
st.set_page_config(
    page_title="BI Educación Bolivia",
    layout="wide",
    page_icon="📊"
)

# ==============================
# CSS
# ==============================
def load_css():
    with open("estilo.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ==============================
# CONEXIÓN
# ==============================
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
# QUERY
# ==============================
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
# FILTRO DINÁMICO
# ==============================
st.sidebar.header("🎛 Filtros")

anio_min, anio_max = int(df["anio"].min()), int(df["anio"].max())

rango = st.sidebar.slider(
    "Selecciona rango de años",
    anio_min,
    anio_max,
    (anio_min, anio_max)
)

df_filtrado = df[(df["anio"] >= rango[0]) & (df["anio"] <= rango[1])]

# ==============================
# HEADER
# ==============================
st.markdown("""
<div class="header">
    <h1>📊 Educación y Brecha Digital Laboral</h1>
    <p>Análisis estratégico de empleabilidad, desempleo y habilidades TIC en Bolivia</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==============================
# ARQUITECTURA MEDALLÓN
# ==============================
st.subheader("🏗️ Arquitectura de Datos (Medallion)")

st.markdown("""
<div class="insight-card">
    <div class="insight-title">🔹 Capa Bronze (Ingesta)</div>
    <div class="insight-text">
    Integración de datos desde SQL Server y datos de CEPALSTAT, consolidando fuentes para análisis.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="insight-card">
    <div class="insight-title">🔹 Capa Silver (Transformación)</div>
    <div class="insight-text">
    Limpieza, normalización y validación de datos, asegurando consistencia y calidad para análisis.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="insight-card">
    <div class="insight-title">🔹 Capa Gold (Modelo Analítico)</div>
    <div class="insight-text">
    Modelo estrella en SQL Server optimizado para análisis de empleabilidad y generación de KPIs.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==============================
# KPIs
# ==============================
st.subheader("📌 Indicadores Clave")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Empleabilidad Promedio", f"{df_filtrado['tasa_empleabilidad'].mean():.2f}%")

with col2:
    st.metric("Desempleo Promedio", f"{df_filtrado['desempleo'].mean():.2f}%")

with col3:
    st.metric("Nivel TIC Promedio", f"{df_filtrado['tic'].mean():.2f}%")

# KPI estratégico
brecha = df_filtrado["tic"] - df_filtrado["tasa_empleabilidad"]
st.metric("📉 Brecha Digital Laboral", f"{brecha.mean():.2f}")

st.markdown("---")

# ==============================
# GRÁFICOS
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

    fig2.update_layout(title="TIC vs Empleabilidad")

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

    fig3.update_layout(title="Desempleo vs Empleabilidad")

    st.plotly_chart(estilo_plotly(fig3), use_container_width=True)

st.markdown("---")

# ==============================
# SCATTER
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
# INSIGHTS
# ==============================
st.subheader("🧠 Insights Estratégicos")

corr_tic = df_filtrado["tic"].corr(df_filtrado["tasa_empleabilidad"])
corr_des = df_filtrado["desempleo"].corr(df_filtrado["tasa_empleabilidad"])

anio_inicio = int(df_filtrado["anio"].min())
anio_fin = int(df_filtrado["anio"].max())

# ==========================
# INSIGHT 1: TIC vs EMPLEABILIDAD (DINÁMICO)
# ==========================

if corr_tic < 0:
    insight_tic = f"""
    Durante el periodo {anio_inicio}-{anio_fin}, la relación negativa entre habilidades TIC y empleabilidad (corr: {corr_tic:.2f}) sugiere que el crecimiento en acceso o formación digital no se ha traducido directamente en mejores oportunidades laborales.

    Esto evidencia una posible desconexión entre la formación tecnológica y las necesidades reales del mercado, donde las habilidades adquiridas no están alineadas con los perfiles demandados.

    Desde una perspectiva estratégica, este resultado indica la necesidad de orientar la educación digital hacia competencias aplicadas, vinculadas a sectores productivos específicos, para lograr un impacto real en la empleabilidad.
    """
else:
    insight_tic = f"""
    Durante el periodo {anio_inicio}-{anio_fin}, la relación positiva entre habilidades TIC y empleabilidad (corr: {corr_tic:.2f}) indica que el desarrollo de competencias digitales está contribuyendo a mejorar la inserción laboral.

    Esto sugiere una transición hacia un mercado laboral más digitalizado, donde las habilidades tecnológicas comienzan a tener un impacto tangible.

    Estratégicamente, esto refuerza la importancia de seguir fortaleciendo la educación en TIC como un motor clave para el crecimiento económico y la empleabilidad sostenible.
    """

# ==========================
# INSIGHT 2: DESEMPLEO vs EMPLEABILIDAD (DINÁMICO)
# ==========================

if corr_des > 0:
    insight_des = f"""
    En el periodo {anio_inicio}-{anio_fin}, la relación positiva entre desempleo y empleabilidad (corr: {corr_des:.2f}) refleja un comportamiento atípico frente a lo esperado en modelos económicos tradicionales.

    Este fenómeno puede estar influenciado por factores estructurales como la informalidad o el subempleo, donde las estadísticas de empleo no capturan completamente la calidad del trabajo.

    A nivel estratégico, esto sugiere que no basta con medir la cantidad de empleo, sino que es fundamental incorporar indicadores de calidad laboral para entender el verdadero estado del mercado.
    """
else:
    insight_des = f"""
    En el periodo {anio_inicio}-{anio_fin}, la relación negativa entre desempleo y empleabilidad (corr: {corr_des:.2f}) confirma la dinámica esperada del mercado laboral.

    Esto indica que las condiciones macroeconómicas están influyendo directamente en la capacidad de inserción laboral.

    Desde una perspectiva estratégica, la reducción del desempleo sigue siendo un factor clave, pero debe ir acompañada de políticas que fortalezcan la calidad y sostenibilidad del empleo generado.
    """

# ==========================
# INSIGHT 3: VISIÓN GLOBAL
# ==========================

insight_general = f"""
El análisis del periodo {anio_inicio}-{anio_fin} muestra que la empleabilidad en Bolivia no depende de un único factor, sino de la interacción entre educación, acceso a tecnología y condiciones del mercado laboral.

Aunque el acceso a TIC ha crecido, su impacto no es automático, lo que evidencia una brecha más profunda relacionada con la alineación entre formación y demanda laboral.

Esto sugiere que el verdadero desafío no es solo reducir la brecha digital, sino construir un ecosistema donde educación, innovación y mercado trabajen de forma coordinada para generar oportunidades reales.
"""

# ==========================
# RENDER INSIGHTS
# ==========================

st.markdown(f"""
<div class="insight-card">
<div class="insight-title">💻 Brecha Digital y Empleo</div>
<div class="insight-text">{formatear_texto(insight_tic)}</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="insight-card">
<div class="insight-title">📉 Dinámica del Mercado Laboral</div>
<div class="insight-text">{formatear_texto(insight_des)}</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="insight-card">
<div class="insight-title">🧠 Lectura Estratégica Global</div>
<div class="insight-text">{formatear_texto(insight_general)}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==============================
# REFLEXIÓN FINAL
# ==============================

mensaje_final = f"""
Durante el periodo analizado ({anio_inicio}-{anio_fin}), los datos muestran que el desafío no es únicamente mejorar indicadores, sino transformar realidades.

Detrás de cada porcentaje hay personas enfrentando barreras para acceder a oportunidades laborales dignas, en un contexto donde la tecnología avanza más rápido que la capacidad de adaptación del sistema educativo.

La brecha digital no es solo una cuestión de acceso, sino de oportunidades reales. Y cerrarla implica tomar decisiones estratégicas que conecten educación, innovación y desarrollo económico.

El valor de este análisis no está únicamente en entender qué ocurre, sino en impulsar acciones que permitan que el crecimiento tecnológico se traduzca en bienestar tangible.

Porque al final, los datos no cambian el mundo… pero las decisiones basadas en ellos sí.
"""

st.markdown(f"""
<div class="insight-card">
<div class="insight-title">🌆 Reflexión Final</div>
<div class="insight-text">{formatear_texto(mensaje_final)}</div>
</div>
""", unsafe_allow_html=True)