# ==============================================
# Imports gerais
# ==============================================
from pathlib import Path
from datetime import datetime
import pandas as pd
from PIL import Image
import folium

# Streamlit e dependências
try:
    import streamlit as st
    from streamlit_folium import folium_static
    STREAMLIT_ON = True
except ImportError:
    STREAMLIT_ON = False

# Outros pacotes
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio


# ==============================================
# Configurações iniciais do Streamlit
# ==============================================
st.set_page_config(
    page_title="Visão Empresa",  # título que aparece na aba do navegador
    page_icon="🏢",              # ícone da página
    layout="wide"                # layout opcional
)

st.title("Visão Empresa")  # título principal da página


# ==============================================
# Carregar CSV
# ==============================================
# BASE_PATH = Path(r"C:\Users\marci\OneDrive\Documentos\Márcio\Cursos\Comunidade DS\Formação Cientista de dados\Z.Repos\FTC_python\dataset")
# CSV_FILE = BASE_PATH / "train.csv"

df = pd.read_csv("dataset/train.csv")

print(df.head())  # funciona no terminal / Jupyter


# ==============================================
# Função de limpeza de dados
# ==============================================
def limpar_dados(df):
    tb = df.copy()

    # Remover NaN 'string' (se houver)
    tb = tb[tb["Road_traffic_density"] != "NaN "]
    tb = tb[tb["multiple_deliveries"] != "NaN "]
    tb = tb[tb["Delivery_person_Age"] != "NaN "]

    # Remover espaços no fim das strings
    cols_str = [
        "ID", "Delivery_person_ID", "Road_traffic_density",
        "Type_of_order", "Type_of_vehicle", "City", "Festival"
    ]
    for c in cols_str:
        tb[c] = tb[c].str.strip()

    # Converter tipos
    tb["Delivery_person_Age"] = tb["Delivery_person_Age"].astype(int)
    tb["Delivery_person_Ratings"] = tb["Delivery_person_Ratings"].astype(float)
    tb["Order_Date"] = pd.to_datetime(tb["Order_Date"], format="%d-%m-%Y")

    return tb


tb1 = limpar_dados(df)


# ==============================================
# Barra lateral
# ==============================================
st.header("Marketplace - Visão empresa")

image = Image.open("Curry.png")
st.sidebar.image(image, width=240)

st.sidebar.markdown("# Cury On Wheels Company")
st.sidebar.markdown("## The fastest delivery in town")
st.sidebar.markdown("---")

date_slider = st.sidebar.slider(
    "Até qual valor?",
    value=datetime(2022, 4, 13),      # valor inicial
    min_value=datetime(2022, 2, 11),  # mínimo
    max_value=datetime(2022, 4, 6),   # máximo
    format="DD-MM-YYYY"
)

# st.header(date_slider)

traffic_options = st.sidebar.multiselect(
    "Quais as condições do trânsito",
    ["Low", "Medium", "High", "Jam"],
    default=["Low", "Medium", "High", "Jam"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Márcio Neves Caemerer")


# ==============================================
# Filtros
# ==============================================
# filtro de data
linhas_selecionadas = tb1["Order_Date"] < date_slider
tb1 = tb1.loc[linhas_selecionadas, :]

# filtro de trânsito
linhas_selecionadas = tb1["Road_traffic_density"].isin(traffic_options)
tb1 = tb1.loc[linhas_selecionadas, :]

st.dataframe(tb1)


# ==============================================
# Layout principal (abas)
# ==============================================
tab1, tab2, tab3 = st.tabs(["Visão Gerencial", "Visão Tática", "Visão Geográfica"])


# ---------- Tab 1: Visão Gerencial ----------
with tab1:
    with st.container():
        st.markdown("Pedidos por dia")

        df_aux = (
            tb1.loc[:, ["ID", "Order_Date"]]
            .groupby("Order_Date")
            .count()
            .reset_index()
        )

        fig = px.bar(df_aux, x="Order_Date", y="ID")
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("Distribuição de densidade de pedidos")
            tb_aux = (
                tb1.loc[:, ["Road_traffic_density", "ID"]]
                .groupby("Road_traffic_density")
                .count()
                .reset_index()
            )
            tb_aux = tb_aux.loc[tb_aux["Road_traffic_density"] != "NaN ", :]

            tb_aux["percent"] = tb_aux["ID"] / tb_aux["ID"].sum()

            fig = px.pie(tb_aux, names="Road_traffic_density", values="ID")
            fig.update_traces(textinfo="label+value+percent")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("Pedidos por cidade e densidade de tráfego")
            lista = ["ID", "City", "Road_traffic_density"]
            tb_aux = tb1.loc[:, lista].copy()
            tb_aux = tb_aux.loc[tb_aux["City"] != "NaN", :]
            tb_aux = tb_aux.loc[tb_aux["Road_traffic_density"] != "NaN", :]
            tb_aux = tb_aux.groupby(["City", "Road_traffic_density"]).count().reset_index()

            fig = px.scatter(
                tb_aux,
                x="City",
                y="Road_traffic_density",
                size="ID",
                color="City"
            )
            st.plotly_chart(fig, use_container_width=True)


# ---------- Tab 2: Visão Tática ----------
with tab2:
    with st.container():
        st.markdown("Pedidos por semana")
        tb1["Week_of_year"] = tb1["Order_Date"].dt.strftime("%U")

        tb_aux = (
            tb1.loc[:, ["Week_of_year", "ID"]]
            .groupby("Week_of_year")
            .count()
            .reset_index()
        )
        fig = px.line(tb_aux, x="Week_of_year", y="ID")
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown("Pedidos por entregador por semana")
        tb_aux01 = (
            tb1.loc[:, ["ID", "Week_of_year"]]
            .groupby("Week_of_year")
            .count()
            .reset_index()
        )
        tb_aux02 = (
            tb1.loc[:, ["Delivery_person_ID", "Week_of_year"]]
            .groupby("Week_of_year")
            .nunique()
            .reset_index()
        )

        tb_aux = pd.merge(tb_aux01, tb_aux02, how="inner")
        tb_aux["order_per_deliver"] = tb_aux01["ID"] / tb_aux02["Delivery_person_ID"]

        fig = px.line(tb_aux, x="Week_of_year", y="order_per_deliver")
        st.plotly_chart(fig, use_container_width=True)


# ---------- Tab 3: Visão Geográfica ----------
with tab3:
    st.markdown("Mapa")

    columns = [
        "City",
        "Road_traffic_density",
        "Delivery_location_latitude",
        "Delivery_location_longitude",
    ]
    columns_groupby = ["City", "Road_traffic_density"]

    tb_aux = tb1.loc[:, columns].groupby(columns_groupby).median().reset_index()
    tb_aux = tb_aux[tb_aux["Road_traffic_density"] != "NaN"]
    tb_aux = tb_aux[tb_aux["City"] != "NaN"]

    map_ = folium.Map(zoom_start=11)

    for _, location_info in tb_aux.iterrows():
        folium.Marker(
            [location_info["Delivery_location_latitude"],
             location_info["Delivery_location_longitude"]],
            popup=location_info[["City", "Road_traffic_density"]]
        ).add_to(map_)

    folium_static(map_, width=1024, height=600)
