import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dashboard de ventas",
    page_icon="📊",
    layout="wide"
)


@st.cache_data
def cargar_datos():
    df = pd.read_csv("ventas.csv")
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Total"] = df["Precio"] * df["Cantidad"]
    df["Mes"] = df["Fecha"].dt.strftime("%Y-%m")
    return df

df = cargar_datos()


st.title("Dashboard de ventas")
st.write("Consulta y analiza los registros de ventas.")


st.sidebar.header("Controles")

categorias = st.sidebar.multiselect(
    "Filtrar por categoria",
    options=sorted(df["Categoria"].unique()),
    default=sorted(df["Categoria"].unique())
)

meses = st.sidebar.multiselect(
    "Filtrar por mes",
    options=sorted(df["Mes"].unique()),
    default=sorted(df["Mes"].unique())
)

pagos = st.sidebar.multiselect(
    "Filtrar por metodo de pago",
    options=sorted(df["Pago"].unique()),
    default=sorted(df["Pago"].unique())
)


busqueda = st.text_input("Buscar producto")


filtrado = df[
    df["Categoria"].isin(categorias)
    & df["Mes"].isin(meses)
    & df["Pago"].isin(pagos)
]

if busqueda:
    filtrado = filtrado[
        filtrado["Producto"].str.contains(
            busqueda, case=False, na=False
        )
    ]

col1, col2, col3 = st.columns(3)

col1.metric(
    "Ventas totales",
    f"${filtrado['Total'].sum():,.2f}"
)
col2.metric(
    "Unidades vendidas",
    int(filtrado["Cantidad"].sum())
)
col3.metric(
    "Registros",
    len(filtrado)
)

st.divider()

if st.checkbox("Mostrar dataset"):
    st.subheader("Base de datos de ventas")
    st.dataframe(filtrado, use_container_width=True)

if st.checkbox("Mostrar grafica de ventas por categoria"):
    st.subheader("Ventas por categoria")
    ventas_categoria = (
        filtrado.groupby("Categoria")["Total"].sum()
    )
    st.bar_chart(ventas_categoria)


if st.checkbox("Mostrar grafica de ventas por mes"):
    st.subheader("Ventas por mes")
    ventas_mes = (
        filtrado.groupby("Mes")["Total"].sum().sort_index()
    )
    st.line_chart(ventas_mes)

if st.checkbox("Mostrar grafica por metodo de pago"):
    st.subheader("Ventas por metodo de pago")
    ventas_pago = filtrado.groupby("Pago")["Total"].sum()
    st.bar_chart(ventas_pago)


st.divider()
st.subheader("Acerca de")

st.write("Autora: Angélica Martínez Hernández")
st.write("Carrera: Licenciatura en Ingeniería de Software")
st.write("Matrícula: zS26004664")
st.write("Ciudad natal: Coscomatepec, Veracruz, México")


st.subheader("Ubicacion de mi ciudad natal")

mapa = pd.DataFrame({
    "lat": [19.072775],
    "lon": [-97.04685]
})

st.map(
    mapa,
    latitude="lat",
    longitude="lon",
    zoom=12
)