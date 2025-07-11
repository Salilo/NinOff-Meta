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
    
    # Elementos
    cols = st.columns(2)
    with cols[0]:
        primary = st.selectbox("Primário", ELEMENTS, index=0)
    with cols[1]:
        secondary = st.selectbox("Secundário", ELEMENTS, index=1)
    
    # Charm
    charms = ["Nenhum"] + list({
        "Capricorn": "+5 FRT", "Aquarius": "+5 INT", "Leo": "+5 AGI",
        "Saggitarius": "+1 ALL", "Virgo": "+5 CHK", "Cancer": "+1 STR",
        "Pisces": "+1 ALL", "Libra": "+5% INT", "Scorpio": "+1 AGI",
        "Gemini": "+1 CHK", "Taurus": "+1 FRT"
    }.keys())
    charm = st.selectbox("Charm", charms, index=0)
    
    # Guild Level
    guild_level = st.slider("Guild Level", 0, 10, 0)
    
    # Atributos
    st.header("🧬 Atributos Base", divider="gray")
    cols = st.columns(2)
    attributes = {}
    with cols[0]:
        attributes["STR"] = st.number_input("STR", min_value=5, value=5, step=1)
        attributes["FRT"] = st.number_input("FRT", min_value=5, value=5, step=1)
        attributes["INT"] = st.number_input("INT", min_value=5, value=5, step=1)
    with cols[1]:
        attributes["AGI"] = st.number_input("AGI", min_value=5, value=5, step=1)
        attributes["CHK"] = st.number_input("CHK", min_value=5, value=5, step=1)
    
    # Cálculos
    total_points_spent = sum(attributes.values()) - (5 * 5)
    level = calculate_level(total_points_spent)
    points_per_level = 5 if level <= 50 else 4
    total_points_available = (level - 1) * 5 + max(0, level - 50) * (points_per_level - 5)
    
    st.header("📊 Status", divider="gray")
    st.metric("Pontos Gastos", total_points_spent)
    st.metric("Pontos Disponíveis", max(0, total_points_available - total_points_spent))
    st.metric("Nível", level)

# ===== BANCO DE TÉCNICAS =====
techniques_db = {
    "Fire": {
        "Phoenix Fireball": {"base": 27, "scaling": "INT", "cost": 10, "cooldown": 16},
        "Big Flame Bullet": {"base": 35, "scaling": "INT", "cost": 30, "cooldown": 18}
    },
    "Wind": {
        "Wind Shuriken": {"base": 25, "scaling": "INT", "cost": 12, "cooldown": 10},
        "Slashing Tornado": {"base": 30, "scaling": "STR", "cost": 25, "cooldown": 18}
    },
    "Weapon": {
        "Kunai": {"base": 1, "scaling": "STR", "cost": 0, "cooldown": 0},
        "Shuriken": {"base": 1, "scaling": "INT", "cost": 0, "cooldown": 0}
    }
}

# ===== TABELA CORRIGIDA =====
def create_tech_df(element):
    tech_data = techniques_db.get(element, {})
    scaling_map = {"STR": attributes["STR"], "INT": attributes["INT"], "CHK": attributes["CHK"]}
    
    tech_list = []
    for name, data in tech_data.items():
        scaling_value = scaling_map[data["scaling"]]
        damage = data["base"] + (scaling_value * 0.6)
        dps = damage / data["cooldown"] if data["cooldown"] > 0 else 0
        
        tech_list.append({
            "Técnica": name,
            "Elemento": element,
            "Dano Base": data["base"],
            "Scaling": data["scaling"],
            "Dano Total": damage,
            "DPS": dps,
            "Chakra": data["cost"],
            "Cooldown": data["cooldown"]
        })
    
    return pd.DataFrame(tech_list)

# Processamento seguro da tabela
try:
    df_primary = create_tech_df(primary)
    df_secondary = create_tech_df(secondary)
    df_combined = pd.concat([df_primary, df_secondary]).reset_index(drop=True)
    
    # Aplicação segura de estilos
    def apply_safe_styler(df):
        return df.style \
            .apply(style_element, axis=1) \
            .format({
                "Dano Total": "{:.1f}",
                "DPS": "{:.1f}"
            })
    
    st.header(f"📜 Técnicas de {primary} + {secondary}")
    if not df_combined.empty:
        st.dataframe(
            apply_safe_styler(df_combined),
            column_config={
                "Dano Total": st.column_config.NumberColumn(format="%.1f"),
                "DPS": st.column_config.NumberColumn(format="%.1f")
            },
            hide_index=True,
            use_container_width=True,
            height=min(600, 45 * len(df_combined) + 45)
        )
    else:
        st.warning("Nenhuma técnica disponível para estes elementos")
except Exception as e:
    st.error(f"Erro ao processar técnicas: {str(e)}")

# ===== RODAPÉ =====
st.divider()
st.caption("🎮 Dica: Ordene clicando nos cabeçalhos | Atualize para resetar")
