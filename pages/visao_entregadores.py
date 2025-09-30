# Imports gerais
from pathlib import Path
import pandas as pd
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static
import folium

# Streamlit opcional
try:
    import streamlit as st
    STREAMLIT_ON = True
except ImportError:
    STREAMLIT_ON = False

# Outros pacotes
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Visão Entregadores",
    page_icon="🚴",
    layout="wide"
)

st.title("Visão Entregadores")

# Carregar CSV
df = pd.read_csv(r'dataset\train.csv')
print(df.head())

# --- Limpeza de dados ---
def limpar_dados(df):
    tb = df.copy()
    tb = tb[tb['Road_traffic_density'] != 'NaN ']
    tb = tb[tb['multiple_deliveries'] != 'NaN ']
    tb = tb[tb['Delivery_person_Age'] != 'NaN ']

    cols_str = ['ID', 'Delivery_person_ID', 'Road_traffic_density', 
                'Type_of_order', 'Type_of_vehicle', 'City', 'Festival']
    for c in cols_str:
        tb[c] = tb[c].str.strip()

    tb['Delivery_person_Age'] = tb['Delivery_person_Age'].astype(int)
    tb['Delivery_person_Ratings'] = tb['Delivery_person_Ratings'].astype(float)
    tb['Order_Date'] = pd.to_datetime(tb['Order_Date'], format='%d-%m-%Y')
    return tb

tb1 = limpar_dados(df)

# ===========
# Barra lateral
# ===========
image = Image.open('Curry.png')
st.sidebar.image(image, width=240)

st.sidebar.markdown('# Curry On Wheels Company')
st.sidebar.markdown('## The fastest delivery in town')
st.sidebar.markdown("""---""")

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY'
)

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

weather_conditions = st.sidebar.multiselect(
    'Quais as condições climáticas?',
    [
        'conditions Cloudy', 'conditions Fog', 'conditions Sandstorms',
        'conditions Stormy', 'conditions Sunny', 'conditions Windy'
    ],
    default=[
        'conditions Cloudy', 'conditions Fog', 'conditions Sandstorms',
        'conditions Stormy', 'conditions Sunny', 'conditions Windy'
    ]
)

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Márcio Neves Caemerer')

# ===========
# Filtros
# ===========
tb1 = tb1.loc[tb1['Order_Date'] < date_slider, :]
tb1 = tb1.loc[tb1['Road_traffic_density'].isin(traffic_options), :]
tb1 = tb1.loc[tb1['Weatherconditions'].isin(weather_conditions), :]

# ===========
# Layout
# ===========
st.header("Marketplace - Visão Empresa")

# --- Métricas Gerais ---
with st.container():
    st.subheader('Métricas Gerais')
    col1, col2, col3, col4 = st.columns(4, gap='medium')

    with col1:
        maior_idade = tb1['Delivery_person_Age'].max()
        st.metric('Maior idade', maior_idade)

    with col2:
        menor_idade = tb1['Delivery_person_Age'].min()
        st.metric('Menor idade', menor_idade)

    with col3:
        melhor_condicao = tb1['Vehicle_condition'].max()
        st.metric('Melhor condição', melhor_condicao)

    with col4:
        pior_condicao = tb1['Vehicle_condition'].min()
        st.metric('Pior condição', pior_condicao)

# --- Avaliações ---
with st.container():
    st.markdown("""---""")
    st.subheader('Avaliações')
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('##### Avaliação média por entregador')
        tb1_aux = tb1[['Delivery_person_ID', 'Delivery_person_Ratings']] \
            .groupby('Delivery_person_ID').mean().reset_index()
        st.dataframe(tb1_aux)

    with col2:
        st.markdown('##### Avaliação média por trânsito')
        tb1_aux = tb1[['Delivery_person_Ratings', 'Road_traffic_density']] \
            .groupby('Road_traffic_density') \
            .agg({'Delivery_person_Ratings': ['mean', 'std']})
        tb1_aux.columns = ['Média', 'Desvio padrão']
        tb1_aux = tb1_aux.reset_index()
        st.dataframe(tb1_aux)

    with col3:
        st.markdown('##### Avaliação média por clima')
        tb1_aux = tb1[['Weatherconditions', 'Delivery_person_Ratings']] \
            .groupby('Weatherconditions') \
            .agg({'Delivery_person_Ratings': ['mean', 'std']})
        tb1_aux.columns = ['Média', 'Desvio padrão']
        tb1_aux = tb1_aux.reset_index()
        st.dataframe(tb1_aux)

# --- Velocidade de entrega ---
with st.container():
    st.markdown("""---""")
    st.subheader('Velocidade de entrega')
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('##### Top entregadores mais rápidos')
        tb1_aux = tb1[['Delivery_person_ID', 'City', 'Time_taken(min)']] \
            .groupby(['City', 'Delivery_person_ID']).min() \
            .sort_values(['City', 'Time_taken(min)'], ascending=True) \
            .reset_index().groupby('City').head(10)
        st.dataframe(tb1_aux)

    with col2:
        st.markdown('##### Top entregadores mais lentos')
        tb1_aux = tb1[['Delivery_person_ID', 'City', 'Time_taken(min)']] \
            .groupby(['City', 'Delivery_person_ID']).max() \
            .sort_values(['City', 'Time_taken(min)'], ascending=True) \
            .reset_index().groupby('City').head(10)
        st.dataframe(tb1_aux)
