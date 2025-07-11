import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

# ===== CONFIGURAÇÃO =====
st.set_page_config(
    page_title="Metanin Renewal Calculator",
    page_icon="🔥",
    layout="wide"
)

# ===== CONSTANTES =====
ELEMENTS = ["Fire", "Wind", "Lightning", "Earth", "Medical", "Weapon", "Taijutsu"]
BASE_ATTRIBUTE = 5
COLORS = {
    "Fire": "#FF5555",
    "Wind": "#55FF55",
    "Lightning": "#FFFF55",
    "Earth": "#FFAA55",
    "Medical": "#55FFAA",
    "Weapon": "#AAAAAA",
    "Taijutsu": "#AA55FF"
}

# URL da imagem (substitua pelo seu link)
IMAGE_URL = "https://i.imgur.com/OSmLbzu.png"  # ← COLOQUE SEU LINK AQUI

# ===== CARREGAR IMAGEM DO LINK =====
def load_image_from_url(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except:
        return None

# ===== CABEÇALHO PERSONALIZADO =====
col1, col2 = st.columns([0.9, 0.1])
with col1:
    st.title("🔥 Metanin Renewal Calculator")
with col2:
    st.markdown("""
    <div style="text-align: right;">
        <small>by Rin</small><br>
    </div>
    """, unsafe_allow_html=True)
    
    # Exibe imagem do link
    if IMAGE_URL:
        avatar_img = load_image_from_url(IMAGE_URL)
        if avatar_img:
            st.image(avatar_img, width=80)
        else:
            st.warning("Imagem não encontrada")

# [...] (O RESTANTE DO CÓDIGO PERMANECE IGUAL AO ANTERIOR)

# ===== SIDEBAR =====
with st.sidebar:
    st.header("⚙️ Configuração", divider="red")
    
    # [...] (CONTINUE COM O RESTO DO CÓDIGO ORIGINAL)
