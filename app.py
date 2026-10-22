import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dashboard de videojuegos",
    page_icon="🎮",
    layout="wide"
)


# =========================
# 1. CARGAR LA BASE DE DATOS
# =========================

@st.cache_data
def cargar_datos():
    df = pd.read_csv(
        "ultimate_video_game_industry_dataset_v3_20000.csv"
    )

    df["release_date"] = pd.to_datetime(
        df["release_date"], errors="coerce"
    )

    # Evitar errores si existen datos faltantes
    columnas_numericas = [
        "estimated_revenue_million",
        "copies_sold_million",
        "metacritic_score",
        "user_score",
        "steam_rating_percent",
        "budget_million_usd",
        "release_year"
    ]

    for columna in columnas_numericas:
        df[columna] = pd.to_numeric(
            df[columna], errors="coerce"
        )

    return df


df = cargar_datos()


# =========================
# 2. ENCABEZADO
# =========================

st.title("🎮 Dashboard de la industria de videojuegos")
st.write(
    "Explora los videojuegos por género, año de lanzamiento, "
    "calificaciones y rendimiento comercial."
)

st.caption(
    f"Base de datos: {len(df):,} registros"
)


# =========================
# 3. FILTROS LATERALES
# =========================

st.sidebar.header("Filtros")

generos = st.sidebar.multiselect(
    "Género",
    options=sorted(df["genre"].dropna().unique()),
    default=sorted(df["genre"].dropna().unique())
)

anios = st.sidebar.slider(
    "Año de lanzamiento",
    min_value=int(df["release_year"].min()),
    max_value=int(df["release_year"].max()),
    value=(
        int(df["release_year"].min()),
        int(df["release_year"].max())
    )
)

exitos = st.sidebar.multiselect(
    "Éxito comercial",
    options=sorted(
        df["commercial_success"].dropna().unique()
    ),
    default=sorted(
        df["commercial_success"].dropna().unique()
    )
)

desarrolladores = st.sidebar.multiselect(
    "Tamaño del desarrollador",
    options=sorted(
        df["developer_size"].dropna().unique()
    ),
    default=sorted(
        df["developer_size"].dropna().unique()
    )
)


# =========================
# 4. BUSCADOR
# =========================

busqueda = st.text_input(
    "🔎 Buscar videojuego, franquicia o desarrollador",
    placeholder="Ejemplo: Minecraft"
)


# =========================
# 5. APLICAR FILTROS
# =========================

filtrado = df[
    df["genre"].isin(generos)
    & df["release_year"].between(anios[0], anios[1])
    & df["commercial_success"].isin(exitos)
    & df["developer_size"].isin(desarrolladores)
].copy()

if busqueda.strip():
    texto = busqueda.strip()

    coincide = (
        filtrado["title"].str.contains(
            texto, case=False, na=False
        )
        | filtrado["franchise"].str.contains(
            texto, case=False, na=False
        )
        | filtrado["developer"].str.contains(
            texto, case=False, na=False
        )
    )

    filtrado = filtrado[coincide]


# =========================
# 6. INDICADORES PRINCIPALES
# =========================

st.subheader("Indicadores generales")

col1, col2, col3, col4 = st.columns(4)

ingresos = filtrado[
    "estimated_revenue_million"
].sum()

unidades = filtrado[
    "copies_sold_million"
].sum()

calificacion = filtrado[
    "metacritic_score"
].mean()

col1.metric(
    "Ingresos estimados",
    f"${ingresos:,.2f} M USD"
)

col2.metric(
    "Copias vendidas",
    f"{unidades:,.2f} M"
)

col3.metric(
    "Videojuegos registrados",
    f"{len(filtrado):,}"
)

col4.metric(
    "Metacritic promedio",
    f"{calificacion:.1f}/100"
    if pd.notna(calificacion)
    else "Sin datos"
)


# =========================
# 7. GRÁFICAS
# =========================

st.divider()

if filtrado.empty:
    st.warning(
        "No hay videojuegos que coincidan con los filtros."
    )
else:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Ingresos por género")

        ingresos_genero = (
            filtrado.groupby("genre")[
                "estimated_revenue_million"
            ]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(ingresos_genero)

    with col2:
        st.subheader("Ingresos por año")

        ingresos_anio = (
            filtrado.groupby("release_year")[
                "estimated_revenue_million"
            ]
            .sum()
            .sort_index()
        )

        st.line_chart(ingresos_anio)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Rendimiento comercial")

        rendimiento = (
            filtrado.groupby("commercial_success")
            .size()
            .sort_values(ascending=False)
        )

        st.bar_chart(rendimiento)

    with col4:
        st.subheader("Calificación por género")

        puntuaciones = (
            filtrado.groupby("genre")[
                "metacritic_score"
            ]
            .mean()
            .dropna()
            .sort_values(ascending=False)
        )

        st.bar_chart(puntuaciones)


# =========================
# 8. TABLA DE VIDEOJUEGOS
# =========================

st.divider()
st.subheader("📋 Catálogo de videojuegos")

columnas = [
    "title",
    "franchise",
    "release_year",
    "genre",
    "developer",
    "launch_price_usd",
    "copies_sold_million",
    "estimated_revenue_million",
    "metacritic_score",
    "commercial_success"
]

if st.checkbox("Mostrar base de datos"):
    st.dataframe(
        filtrado[columnas],
        use_container_width=True,
        hide_index=True
    )

    csv = filtrado[columnas].to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "📥 Descargar datos filtrados",
        data=csv,
        file_name="videojuegos_filtrados.csv",
        mime="text/csv"
    )


# =========================
# 9. TOP 10 VIDEOJUEGOS
# =========================

st.divider()
st.subheader("🏆 Top 10 por ingresos estimados")

top_10 = filtrado.nlargest(
    10, "estimated_revenue_million"
)[
    [
        "title",
        "genre",
        "estimated_revenue_million",
        "copies_sold_million",
        "metacritic_score"
    ]
]

st.dataframe(
    top_10,
    use_container_width=True,
    hide_index=True
)