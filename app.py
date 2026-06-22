import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os 
from datetime import datetime

# --------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# --------------------------------------------------

st.set_page_config(
    page_title="Campaña San Juan 2026",
    page_icon="🔥",
    layout="wide"
)

# --------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------

@st.cache_data(ttl=60)
def cargar_datos():

    archivo = "data/BD Campaña San Juan.xlsx"

    df = pd.read_excel(archivo)

    return df

df = cargar_datos()

# Convertir fecha
df["Fecha"] = pd.to_datetime(df["Fecha"])

# Crear columna Pack
df["Pack"] = df["Item"].map({
    "T00560": "HOGAR",
    "T00561": "NACIONAL"
})

# Crear columna Tienda
df["Tienda"] = df["Agencia"].map({
    "GS": "Oficina SCZ / GMI",
    "N3": "RECME",
    "N8": "Beijing"
})

# Crear columna Región
df["Region"] = df["Agencia"].map({
    "GS": "Santa Cruz",
    "N3": "Cochabamba",
    "N8": "Cochabamba"
})

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
# --------------------------------------------------
# ÚLTIMA ACTUALIZACIÓN
# --------------------------------------------------

ruta_excel = "data/BD Campaña San Juan.xlsx"

fecha_modificacion = os.path.getmtime(ruta_excel)

ultima_actualizacion = datetime.fromtimestamp(
    fecha_modificacion
)

st.sidebar.markdown("### 🕒 Última Actualización")

st.sidebar.info(
    ultima_actualizacion.strftime(
        "%d/%m/%Y %H:%M"
    )
)
st.sidebar.image("assets/Logo Copelme.jpg", width=150)

st.sidebar.title("Filtros")

fecha_min = df["Fecha"].min()
fecha_max = df["Fecha"].max()

filtro_fecha = st.sidebar.date_input(
    "Periodo",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

filtro_pack = st.sidebar.multiselect(
    "Pack",
    options=df["Pack"].unique(),
    default=df["Pack"].unique()
)

filtro_tienda = st.sidebar.multiselect(
    "Tienda",
    options=df["Tienda"].unique(),
    default=df["Tienda"].unique()
)

# --------------------------------------------------
# FILTRADO
# --------------------------------------------------

df_filtrado = df.copy()

# Fecha
if len(filtro_fecha) == 2:

    fecha_inicio = pd.to_datetime(filtro_fecha[0])
    fecha_fin = pd.to_datetime(filtro_fecha[1])

    df_filtrado = df_filtrado[
        (df_filtrado["Fecha"] >= fecha_inicio) &
        (df_filtrado["Fecha"] <= fecha_fin)
    ]

# Pack
df_filtrado = df_filtrado[
    df_filtrado["Pack"].isin(filtro_pack)
]

# Tienda
df_filtrado = df_filtrado[
    df_filtrado["Tienda"].isin(filtro_tienda)
]

# --------------------------------------------------
# HEADER
# --------------------------------------------------
# --------------------------------------------------
# HEADER VISUAL
# --------------------------------------------------

col_img1, col_titulo, col_img2 = st.columns([1,2,1])

with col_img1:
    st.image("assets/hogar.jpeg")

with col_titulo:

    st.title("🔥 Campaña San Juan 2026")

    st.markdown(
        """
        ### Seguimiento Comercial de Packs Promocionales
        
        **Meta Comercial:** Bs 43.500
        
        Vigencia: 18-Jun al 30-Jun
        """
    )

with col_img2:
    st.image("assets/nacional.jpg")

# --------------------------------------------------
# KPIs
# --------------------------------------------------

ventas = df_filtrado["Venta Bs."].sum()
importe = df_filtrado["Importe Bs"].sum()
paquetes = df_filtrado["Paquetes"].sum()
rollos = df_filtrado["Rollos"].sum()
facturas = df_filtrado["Número de Factura"].nunique()
ticket = ventas / facturas if facturas > 0 else 0
meta = 43500
cumplimiento = ventas / meta

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        "💰 Venta Neta",
        f"Bs {ventas:,.0f}"
    )

with col2:
    st.metric(
        "📦 Importe Bruto",
        f"Bs {importe:,.0f}"
    )

with col3:
    st.metric(
        "📦 Paquetes",
        f"{paquetes:,.0f}"
    )

with col4:
    st.metric(
        "🧻 Rollos",
        f"{rollos:,.0f}"
    )

with col5:
    st.metric(
        "🧾 Facturas",
        f"{facturas:,.0f}"
    )

with col6:
    st.metric(
        "🎯 Cumplimiento",
        f"{cumplimiento:.1%}"
    )
# --------------------------------------------------
# META
# --------------------------------------------------

st.subheader("Avance de la Campaña")

st.progress(min(cumplimiento, 1.0))

st.write(f"Meta: Bs {meta:,.0f}")
st.info(
    f"💳 Ticket Promedio Actual: Bs {ticket:,.0f}"
)

# --------------------------------------------------
# VELOCÍMETRO DE META
# --------------------------------------------------

st.markdown("---")
st.subheader("🎯 Cumplimiento de Meta")

fig_gauge = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=ventas,
        number={"prefix": "Bs "},
        title={"text": "Venta Neta Acumulada"},
        gauge={
            "axis": {"range": [0, meta]},
            "bar": {"color": "#e95429"},
            "steps": [
                {"range": [0, meta*0.5], "color": "#ffcccc"},
                {"range": [meta*0.5, meta*0.8], "color": "#ffe699"},
                {"range": [meta*0.8, meta], "color": "#d9ead3"}
            ]
        }
    )
)

fig_gauge.update_layout(height=350)

st.plotly_chart(
    fig_gauge,
    use_container_width=True
)

# --------------------------------------------------
# PROYECCIÓN DE CIERRE
# --------------------------------------------------

st.markdown("---")
st.subheader("🔮 Proyección de Cierre")

fecha_inicio = pd.Timestamp("2026-06-18")
fecha_fin = pd.Timestamp("2026-06-30")

dias_totales = (fecha_fin - fecha_inicio).days + 1

dias_transcurridos = (
    df_filtrado["Fecha"].max() - fecha_inicio
).days + 1

if dias_transcurridos > 0:

    promedio_diario = ventas / dias_transcurridos

    proyeccion = promedio_diario * dias_totales

else:

    proyeccion = 0

cumplimiento_proyectado = (
    proyeccion / meta
)

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Venta Proyectada",
        f"Bs {proyeccion:,.0f}"
    )

with col2:

    st.metric(
        "Cumplimiento Esperado",
        f"{cumplimiento_proyectado:.1%}"
    )

# --------------------------------------------------
# INSIGHTS
# --------------------------------------------------

st.markdown("---")
st.subheader("🧠 Insights")

# Pack líder

pack_lider = (
    df_filtrado
    .groupby("Pack")["Venta Bs."]
    .sum()
    .idxmax()
)

participacion_pack = (
    df_filtrado
    .groupby("Pack")["Venta Bs."]
    .sum()
    .max()
    /
    ventas
)

st.info(
    f"El pack {pack_lider} lidera la campaña con una participación de {participacion_pack:.1%}."
)

# Tienda líder

tienda_lider = (
    df_filtrado
    .groupby("Tienda")["Venta Bs."]
    .sum()
    .idxmax()
)

participacion_tienda = (
    df_filtrado
    .groupby("Tienda")["Venta Bs."]
    .sum()
    .max()
    /
    ventas
)

st.success(
    f"{tienda_lider} concentra el {participacion_tienda:.1%} de las ventas acumuladas."
)

# Meta

if cumplimiento >= 0.8:

    st.success(
        "La campaña ya alcanzó más del 80% de la meta."
    )

elif cumplimiento >= 0.5:

    st.warning(
        "La campaña supera el 50% de cumplimiento."
    )

else:

    st.error(
        "La campaña aún se encuentra por debajo del 50% de cumplimiento."
    )

# --------------------------------------------------
# EVOLUCIÓN DIARIA
# --------------------------------------------------

st.markdown("---")
st.subheader("📈 Evolución Diaria de Ventas")

ventas_dia = (
    df_filtrado
    .groupby("Fecha", as_index=False)["Venta Bs."]
    .sum()
)

fig_dia = px.line(
    ventas_dia,
    x="Fecha",
    y="Venta Bs.",
    markers=True,
    title="Ventas Diarias"
)

fig_dia.update_layout(
    height=450
)

st.plotly_chart(
    fig_dia,
    use_container_width=True
)

# --------------------------------------------------
# EVOLUCIÓN ACUMULADA
# --------------------------------------------------

ventas_acum = ventas_dia.copy()

ventas_acum["Acumulado"] = (
    ventas_acum["Venta Bs."]
    .cumsum()
)

fig_acum = px.area(
    ventas_acum,
    x="Fecha",
    y="Acumulado",
    title="Ventas Acumuladas"
)

fig_acum.update_layout(
    height=450
)

st.plotly_chart(
    fig_acum,
    use_container_width=True
)

# --------------------------------------------------
# HOGAR VS NACIONAL
# --------------------------------------------------

st.markdown("---")
st.subheader("🥧 Participación por Pack")

pack = (
    df_filtrado
    .groupby("Pack", as_index=False)["Venta Bs."]
    .sum()
)

fig_pack = px.pie(
    pack,
    names="Pack",
    values="Venta Bs.",
    hole=0.6,
    color="Pack",
    color_discrete_map={
        "HOGAR": "#4c0c5c",
        "NACIONAL": "#e95429"
    }
)

st.plotly_chart(
    fig_pack,
    use_container_width=True
)

# --------------------------------------------------
# TIENDAS
# --------------------------------------------------

st.markdown("---")
st.subheader("🏪 Ranking de Tiendas")

tiendas = (
    df_filtrado
    .groupby("Tienda", as_index=False)["Venta Bs."]
    .sum()
    .sort_values(
        "Venta Bs.",
        ascending=True
    )
)

fig_tiendas = px.bar(
    tiendas,
    x="Venta Bs.",
    y="Tienda",
    orientation="h",
    color="Venta Bs."
)

fig_tiendas.update_layout(
    height=500
)

st.plotly_chart(
    fig_tiendas,
    use_container_width=True
)

# --------------------------------------------------
# TABLA DETALLE
# --------------------------------------------------

st.markdown("---")
st.subheader("📋 Detalle de Transacciones")

columnas_mostrar = [
    "Fecha",
    "Agencia",
    "Tienda",
    "Pack",
    "Número de Factura",
    "Item",
    "Descripción Item",
    "Venta Bs."
]

st.dataframe(
    df_filtrado[columnas_mostrar],
    use_container_width=True,
    height=500
)

# --------------------------------------------------
# EXPORTAR EXCEL
# --------------------------------------------------

from io import BytesIO

def convertir_excel(df):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Campaña San Juan"
        )

    return output.getvalue()

archivo_excel = convertir_excel(df_filtrado)

st.download_button(
    label="📥 Descargar Excel",
    data=archivo_excel,
    file_name="Campaña_San_Juan.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --------------------------------------------------
# TOP PRODUCTOS
# --------------------------------------------------

st.markdown("---")
st.subheader("🏆 Top Productos")

productos = (
    df_filtrado
    .groupby("Descripción Item", as_index=False)["Venta Bs."]
    .sum()
    .sort_values(
        "Venta Bs.",
        ascending=True
    )
)

fig_productos = px.bar(
    productos,
    x="Venta Bs.",
    y="Descripción Item",
    orientation="h",
    color="Venta Bs."
)

fig_productos.update_layout(
    height=500
)

st.plotly_chart(
    fig_productos,
    use_container_width=True
)

# --------------------------------------------------
# REGIONES
# --------------------------------------------------

st.markdown("---")
st.subheader("🌎 Ventas por Región")

region = (
    df_filtrado
    .groupby("Region", as_index=False)["Venta Bs."]
    .sum()
)

fig_region = px.treemap(
    region,
    path=["Region"],
    values="Venta Bs.",
    color="Venta Bs."
)

st.plotly_chart(
    fig_region,
    use_container_width=True
)

# --------------------------------------------------
# HEATMAP
# --------------------------------------------------

st.markdown("---")
st.subheader("🔥 Intensidad de Ventas")

heat = (
    df_filtrado
    .groupby(["Fecha","Tienda"])["Venta Bs."]
    .sum()
    .reset_index()
)

fig_heat = px.density_heatmap(
    heat,
    x="Fecha",
    y="Tienda",
    z="Venta Bs."
)

st.plotly_chart(
    fig_heat,
    use_container_width=True
)

