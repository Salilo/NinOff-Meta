import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

# ===== CONFIGURAÇÃO INICIAL =====
st.set_page_config(
    page_title="Nin0ff-Meta",
    page_icon="🔥",
    layout="wide"
)

# ===== CONSTANTES =====
MAX_POINTS = 285
SIGN_EMOJIS = {
    "Capricorn": "♑", "Aquarius": "♒", "Pisces": "♓", "Aries": "♈",
    "Taurus": "♉", "Gemini": "♊", "Cancer": "♋", "Leo": "♌",
    "Virgo": "♍", "Libra": "♎", "Scorpio": "♏", "Saggitarius": "♐"
}
EMOJI_MAP = {
    "Fire": "🔥", "Wind": "🍃", "Lightning": "⚡", "Earth": "🪨",
    "Water": "💧", "Medical": "🧪", "Weapon": "🗡️", "Taijutsu": "🥋"
}
COLORS = {
    "Fire": "#FF5555", "Wind": "#55FF55", "Lightning": "#FFFF55",
    "Earth": "#FFAA55", "Water": "#55AAFF", "Medical": "#55FFAA",
    "Weapon": "#AAAAAA", "Taijutsu": "#AA55FF", "Common": "#DDDDDD"
}
ELEMENTS = list(EMOJI_MAP.keys())
IMAGE_URL = "https://via.placeholder.com/80"

# ===== FUNÇÕES =====
def label_charm(name):
    return f"{SIGN_EMOJIS.get(name, '')} {name}" if name != "Nenhum" else "Nenhum"

def label_with_emoji(name):
    return f"{EMOJI_MAP.get(name, '')} {name}"

def calculate_level(total_points):
    level, points_needed = 1, 0
    while level <= 60 and points_needed <= MAX_POINTS:
        points_per_level = 5 if level <= 50 else 4
        points_needed += points_per_level
        if total_points >= points_needed and points_needed <= MAX_POINTS:
            level += 1
        else:
            break
    return min(level, 60)

def calculate_available_points(level):
    return (level - 1) * 5 if level <= 50 else (50 * 5) + ((level - 50) * 4)

def apply_bonuses(base, charm, guild_level, attr, faction_bonus):
    value_with_guild = base * (1 + guild_level * 0.01)
    charm_bonuses = {
        "Capricorn": {"FRT": 5}, "Aquarius": {"INT": 5}, "Leo": {"AGI": 5},
        "Saggitarius": {a: 1 for a in ["STR", "FRT", "INT", "AGI", "CHK"]},
        "Virgo": {"CHK": 5}, "Cancer": {"STR": 1}, "Pisces": {a: 1 for a in ["STR", "FRT", "INT", "AGI", "CHK"]},
        "Libra": {"INT": 0.05}, "Scorpio": {"AGI": 1}, "Gemini": {"CHK": 1}, "Taurus": {"FRT": 1}
    }
    bonus = charm_bonuses.get(charm, {}).get(attr, 0)
    total_bonus = int(value_with_guild * (1 + bonus)) if isinstance(bonus, float) else int(value_with_guild + bonus)
    return total_bonus + faction_bonus

def style_element(row):
    nome_elemento = row["Elemento"].split(" ", 1)[-1]
    color = COLORS.get(nome_elemento, "#FFFFFF")
    return [f"background-color: {color}; color: #000000" for _ in row]

def create_tech_df(element, techniques_db, attributes):
    tech_data = techniques_db.get(element, {})
    scaling_map = {"STR": attributes["STR"], "INT": attributes["INT"], "CHK": attributes["CHK"], "AGI": attributes["AGI"]}

    tech_list = []
    for name, data in tech_data.items():
        scaling_value = scaling_map.get(data["scaling"], 0)
        damage = data["base"] + (scaling_value * 0.6)
        dps = damage / data["cooldown"] if data["cooldown"] > 0 else 0

        tech_list.append({
            "Técnica": name,
            "Elemento": f"{EMOJI_MAP.get(element, '')} {element}",
            "Dano Base": data["base"],
            "Scaling": data["scaling"],
            "Dano Total": damage,
            "DPS": dps,
            "Chakra": data["cost"],
            "Cooldown": data["cooldown"],
            "Nível": data["level"]
        })

    return pd.DataFrame(tech_list)

# ===== SIDEBAR: ENTRADAS =====
with st.sidebar:
    st.header("🧬 Elementos e Charm", divider="gray")
    primary = st.selectbox("Elemento Primário", ELEMENTS, format_func=label_with_emoji)
    secondary = st.selectbox("Elemento Secundário", [e for e in ELEMENTS if e != primary], format_func=label_with_emoji)
    charm = st.selectbox("Charm", ["Nenhum"] + list(SIGN_EMOJIS.keys()), format_func=label_charm)

    st.header("🏰 Guilda e Facção", divider="gray")
    guild_level = st.slider("Nível da Guilda", min_value=0, max_value=10, value=5)
    faction_bonus = st.number_input("Bônus de Facção (+STR, +INT...)", min_value=0, max_value=10, value=0)

    st.header("🧪 Atributos Base", divider="gray")
    base_str = st.number_input("STR", min_value=5, max_value=100, value=10)
    base_int = st.number_input("INT", min_value=5, max_value=100, value=10)
    base_frt = st.number_input("FRT", min_value=5, max_value=100, value=10)
    base_agi = st.number_input("AGI", min_value=5, max_value=100, value=10)
    base_chk = st.number_input("CHK", min_value=5, max_value=100, value=10)

attributes_base = {
    "STR": base_str,
    "INT": base_int,
    "FRT": base_frt,
    "AGI": base_agi,
    "CHK": base_chk
}

# Aqui você deve carregar weapons_db e techniques_db conforme necessário

# A seguir: processamento das técnicas (exemplo)
# df_primary = create_tech_df(primary, techniques_db, attributes)
# st.dataframe(df_primary)

st.info("✅ Código carregado com sucesso. Agora adicione o banco de dados e a lógica de exibição.")
