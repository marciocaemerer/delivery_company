import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",   # <--- TÍTULO explícito
    page_icon="🎲"
)

st.title("Página Inicial")  # ainda aparece no corpo

# image_path = r'C:\Users\marci\Logo MNC.PNG'
# image_path = r'C:\Users\marci\OneDrive\Documentos\Márcio\Power B.I\Portfólio\Logo MNC.PNG'
image = Image.open('Curry.png')
# image = "https://img.freepik.com/vetores-premium/modelo-de-vetor-de-design-de-logotipo-de-entrega-expressa_441059-203.jpg"
st.sidebar.image(image,width = 120)

st.sidebar.markdown('# Curry On Wheels Company')
st.sidebar.markdown('## The fastest delivery in town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('### Márcio Neves Caemerer')



