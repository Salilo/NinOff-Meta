import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Metanin Renewal Calculator",
    page_icon="🔥",
    layout="wide"
)

# Título do App
st.title("🔥 Metanin Renewal Calculator")

# ===== SIDEBAR (Configurações) =====
with st.sidebar:
    st.header("Configuração do Personagem")
    
    # 1. Elementos
    elements = ["Fire", "Wind", "Lightning", "Earth", "Medical", "Weapon", "Taijutsu"]
    primary = st.selectbox("Elemento Primário", elements)
    secondary = st.selectbox("Elemento Secundário", elements)
    
    # 2. Charm
    charms = {
        "Nenhum": "",
        "Capricorn": "+5 FRT",
        "Aquarius": "+5 INT",
        "Leo": "+5 AGI",
        "Saggitarius": "+1 ALL",
        "Virgo": "+5 CHK",
        "Cancer": "+1 STR",
        "Pisces": "+1 ALL"
    }
    charm = st.selectbox("Charm do Signo", list(charms.keys()))
    
    # 3. Status Level Guild
    guild_level = st.slider("Status Level Guild", 0, 10, 0)
    
    # 4. Atributos
    st.header("Atributos")
    strength = st.number_input("STR", min_value=0, value=5)
    fortitude = st.number_input("FRT", min_value=0, value=95)
    intellect = st.number_input("INT", min_value=0, value=130)
    agility = st.number_input("AGI", min_value=0, value=5)
    chakra = st.number_input("CHK", min_value=0, value=75)

# ===== TÉCNICAS =====
techniques_db = {
    "Fire": {
        "Phoenix Fireball": {"base": 27, "scaling": "INT", "cost": 10, "cooldown": 16},
        "Big Flame Bullet": {"base": 35, "scaling": "INT", "cost": 30, "cooldown": 18},
        "Fire Wall": {"base": 22, "scaling": "INT", "cost": 15, "cooldown": 12}
    },
    "Wind": {
        "Wind Shuriken (INT)": {"base": 25, "scaling": "INT", "cost": 12, "cooldown": 10},
        "Slashing Tornado (STR)": {"base": 30, "scaling": "STR", "cost": 25, "cooldown": 18}
    }
}

# Mostra técnicas do elemento primário
st.header(f"Técnicas de {primary}")
tech_list = techniques_db.get(primary, {})

if tech_list:
    selected_tech = st.selectbox("Selecione uma técnica", list(tech_list.keys()))
    
    # Pega os dados da técnica
    tech_data = tech_list[selected_tech]
    
    # Cálculo do dano
    scaling_map = {
        "STR": strength,
        "INT": intellect,
        "CHK": chakra
    }
    scaling_value = scaling_map[tech_data["scaling"]]
    damage = tech_data["base"] + (scaling_value * 0.6)
    dps = damage / tech_data["cooldown"]
    
    # Mostra os resultados
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Dano Total", f"{damage:.1f}")
    with col2:
        st.metric("DPS", f"{dps:.1f}")
    with col3:
        st.metric("Custo de Chakra", tech_data["cost"])
else:
    st.warning("Nenhuma técnica disponível para este elemento")

# ===== RODAPÉ =====
st.divider()
st.caption("Feito com Streamlit | Atualize a página para resetar")
