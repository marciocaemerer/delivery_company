# ======================================
# Imports
# ======================================
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from PIL import Image
from haversine import haversine
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go

# Streamlit
try:
    import streamlit as st
    STREAMLIT_ON = True
except ImportError:
    STREAMLIT_ON = False

# ======================================
# Configurações iniciais
# ======================================
st.set_page_config(page_title="Visão Restaurante", page_icon="🍽️", layout="wide")
st.title("Visão Restaurante")

# ======================================
# Carregar dados
# ======================================
df = pd.read_csv(r"dataset\train.csv")

def limpar_dados(df):
    tb = df.copy()
    tb = tb[tb['Road_traffic_density'] != 'NaN ']
    tb = tb[tb['multiple_deliveries'] != 'NaN ']
    tb = tb[tb['Delivery_person_Age'] != 'NaN ']

    # Remover espaços
    cols_str = ['ID','Delivery_person_ID','Road_traffic_density',
                'Type_of_order','Type_of_vehicle','City','Festival']
    for c in cols_str:
        tb[c] = tb[c].str.strip()

    # Tipos corretos
    tb['Delivery_person_Age'] = tb['Delivery_person_Age'].astype(int)
    tb['Delivery_person_Ratings'] = tb['Delivery_person_Ratings'].astype(float)
    tb['Order_Date'] = pd.to_datetime(tb['Order_Date'], format='%d-%m-%Y')

    return tb

tb1 = limpar_dados(df)

# Criar cópia para cálculo do tempo
tb2 = tb1.copy()
tb2['Time_taken(min)'] = tb2['Time_taken(min)'].apply(lambda x: x.split()[1]).astype(int)

# ======================================
# Barra lateral
# ======================================
image = Image.open("Curry.png")
st.sidebar.image(image, width=240)

st.sidebar.markdown("# Curry On Wheels Company")
st.sidebar.markdown("## The fastest delivery in town")
st.sidebar.markdown("---")

date_slider = st.sidebar.slider(
    "Até qual valor?",
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format="DD-MM-YYYY"
)

traffic_options = st.sidebar.multiselect(
    "Condições do trânsito:",
    ["Low","Medium","High","Jam"],
    default=["Low","Medium","High","Jam"]
)

weather_conditions = st.sidebar.multiselect(
    "Condições climáticas:",
    ["conditions Cloudy","conditions Fog","conditions Sandstorms",
     "conditions Stormy","conditions Sunny","conditions Windy"],
    default=["conditions Cloudy","conditions Fog","conditions Sandstorms",
             "conditions Stormy","conditions Sunny","conditions Windy"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Márcio Neves Caemerer")

# ======================================
# Filtros
# ======================================
tb1 = tb1[tb1['Order_Date'] < date_slider]
tb1 = tb1[tb1['Road_traffic_density'].isin(traffic_options)]
tb1 = tb1[tb1['Weatherconditions'].isin(weather_conditions)]

# ======================================
# Métricas principais
# ======================================
st.header("Métricas Gerais")

col1, col2, col3, col4 = st.columns(4)

with col1:
    entregadores = tb1['Delivery_person_ID'].nunique()
    st.metric("Entregadores únicos", entregadores)

with col2:
    cols = ['Restaurant_latitude','Restaurant_longitude',
            'Delivery_location_latitude','Delivery_location_longitude']
    tb1['distance'] = tb1[cols].apply(
        lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),
        axis=1
    )
    media_dist = np.round(tb1['distance'].mean(),2)
    st.metric("Distância média (km)", media_dist)

with col3:
    tb_fest = tb2[tb2['Festival']=="Yes"]
    aux = tb_fest.groupby('Festival')['Time_taken(min)'].agg(['mean','std']).reset_index()
    st.metric("Tempo médio (Festival)", f"{aux.loc[0,'mean']:.2f}")

with col4:
    st.metric("Desvio padrão (Festival)", f"{aux.loc[0,'std']:.2f}")

col5, col6 = st.columns(2)

with col5:
    tb_nf = tb2[tb2['Festival']=="No"]
    aux = tb_nf.groupby('Festival')['Time_taken(min)'].agg(['mean','std']).reset_index()
    st.metric("Tempo médio (Não Festival)", f"{aux.loc[0,'mean']:.2f}")

with col6:
    st.metric("Desvio padrão (Não Festival)", f"{aux.loc[0,'std']:.2f}")

# ======================================
# Gráfico tempo por cidade
# ======================================
st.subheader("Tempo de entrega por cidade")

tb_aux = (
    tb2[['City','Time_taken(min)']]
    .groupby('City')
    .agg({'Time_taken(min)':['mean','std']})
    .reset_index()
)
tb_aux.columns = ['City','tempo_medio','desvio_padrao']

fig = go.Figure(data=[go.Pie(labels=tb_aux['City'], values=tb_aux['tempo_medio'],
                             pull=[0,0.05,0])])
st.plotly_chart(fig, use_container_width=True)
