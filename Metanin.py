import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import base64

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
    "Medical": "🧪", "Weapon": "🗡️", "Taijutsu": "🥋"
}
COLORS = {
    "Fire": "#FF5555", "Wind": "#55FF55", "Lightning": "#FFFF55",
    "Earth": "#FFAA55", "Medical": "#55FFAA", "Weapon": "#AAAAAA", "Taijutsu": "#AA55FF"
}
ELEMENTS = list(EMOJI_MAP.keys())

IMAGE_URL = "https://via.placeholder.com/80"  # Substitua pelo link desejado

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

def apply_bonuses(base, charm, guild_level, attr):
    value_with_guild = base * (1 + guild_level * 0.01)
    charm_bonuses = {
        "Capricorn": {"FRT": 5}, "Aquarius": {"INT": 5}, "Leo": {"AGI": 5},
        "Saggitarius": {a: 1 for a in ["STR", "FRT", "INT", "AGI", "CHK"]},
        "Virgo": {"CHK": 5}, "Cancer": {"STR": 1}, "Pisces": {a: 1 for a in ["STR", "FRT", "INT", "AGI", "CHK"]},
        "Libra": {"INT": 0.05}, "Scorpio": {"AGI": 1}, "Gemini": {"CHK": 1}, "Taurus": {"FRT": 1}
    }
    bonus = charm_bonuses.get(charm, {}).get(attr, 0)
    return int(value_with_guild * (1 + bonus)) if isinstance(bonus, float) else int(value_with_guild + bonus)

def style_element(row):
    nome_elemento = row["Elemento"].split(" ", 1)[-1]  # Remove emoji
    color = COLORS.get(nome_elemento, "#FFFFFF")
    return [f"background-color: {color}; color: #000000" for _ in row]

# ===== INTERFACE PRINCIPAL =====
st.title("🔥 Nin0ff-Meta Calculator")

# ===== SIDEBAR =====
with st.sidebar:
    st.header("⚙️ Configuração", divider="red")

    cols = st.columns(2)
    with cols[0]:
        primary = st.selectbox("Primário", ELEMENTS, format_func=label_with_emoji)
    with cols[1]:
        available_secondary = [e for e in ELEMENTS if e != primary]
        secondary = st.selectbox("Secundário", available_secondary, format_func=label_with_emoji)

    charms = ["Nenhum"] + list(SIGN_EMOJIS.keys())
    charm = st.selectbox("Charm", charms, index=0, format_func=label_charm)


    guild_level = st.slider("Guild Level Status", 0, 10, 0)

    st.header("🧬 Atributos Base", divider="gray")
    cols = st.columns(2)
    attributes_base = {}
    with cols[0]:
        attributes_base["STR"] = st.number_input("STR", min_value=5, value=5, step=1)
        attributes_base["FRT"] = st.number_input("FRT", min_value=5, value=5, step=1)
        attributes_base["INT"] = st.number_input("INT", min_value=5, value=5, step=1)
    with cols[1]:
        attributes_base["AGI"] = st.number_input("AGI", min_value=5, value=5, step=1)
        attributes_base["CHK"] = st.number_input("CHK", min_value=5, value=5, step=1)

    attributes = {
        attr: apply_bonuses(val, charm, guild_level, attr)
        for attr, val in attributes_base.items()
    }

    total_spent = sum(attributes_base.values()) - (5 * 5)
    level = calculate_level(total_spent)
    total_available = calculate_available_points(level)
    remaining_points = max(0, total_available - total_spent)

    st.header("📊 Status", divider="gray")
    st.metric("Pontos Gastos", f"{total_spent}/{MAX_POINTS}")
    st.metric("Pontos Disponíveis", remaining_points)
    st.metric("Nível", level)

    if total_spent > MAX_POINTS:
        st.error(f"Limite de {MAX_POINTS} pontos excedido!")
    elif total_spent > total_available:
        st.warning("Pontos gastos excedem os disponíveis para este nível")

# ===== TÉCNICAS =====
techniques_db = {
    "Fire": {
        "Phoenix Fireball": {"base": 27, "scaling": "INT", "cost": 10, "cooldown": 16},
        "Big Flame Bullet": {"base": 35, "scaling": "INT", "cost": 30, "cooldown": 18},
        "Fire Wall": {"base": 22, "scaling": "INT", "cost": 15, "cooldown": 12},
        "Combusting Vortex": {"base": 40, "scaling": "INT", "cost": 45, "cooldown": 25}
    },
    "Wind": {
        "Wind Shuriken": {"base": 25, "scaling": "INT", "cost": 12, "cooldown": 10},
        "Wind Scythe": {"base": 32, "scaling": "INT", "cost": 20, "cooldown": 15},
        "Slashing Tornado": {"base": 30, "scaling": "STR", "cost": 25, "cooldown": 18}
    },
    "Weapon": {
        "Kunai": {"base": 1, "scaling": "STR", "cost": 0, "cooldown": 0},
        "Shuriken": {"base": 1, "scaling": "INT", "cost": 0, "cooldown": 0},
        "Senbon": {"base": 1, "scaling": "CHK", "cost": 0, "cooldown": 0}
    }
}

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
            "Elemento": f"{EMOJI_MAP.get(element, '')} {element}",
            "Dano Base": data["base"],
            "Scaling": data["scaling"],
            "Dano Total": f"{damage:.1f}",
            "DPS": f"{dps:.1f}",
            "Chakra": data["cost"],
            "Cooldown": data["cooldown"]
        })

    return pd.DataFrame(tech_list)

try:
    df_primary = create_tech_df(primary)
    df_secondary = create_tech_df(secondary)
    df_combined = pd.concat([df_primary, df_secondary]).reset_index(drop=True)

    st.header(f"📜 Técnicas de {label_with_emoji(primary)} + {label_with_emoji(secondary)}")
    if not df_combined.empty:
        styled_df = df_combined.style.apply(style_element, axis=1).format(precision=1)
        st.dataframe(
            styled_df,
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
    st.error(f"Erro ao gerar tabela: {str(e)}")

# ===== IMAGEM CIRCULAR FIXADA =====
try:
    response = requests.get(IMAGE_URL)
    img_data = base64.b64encode(response.content).decode()

    st.markdown(f"""
        <style>
            .circle-img {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 80px;
                height: 80px;
                border-radius: 50%;
                overflow: hidden;
                box-shadow: 0 0 10px rgba(0,0,0,0.3);
                z-index: 9999;
            }}
        </style>
        <div class="circle-img">
            <img src="data:image/png;base64,{img_data}" width="100%">
        </div>
    """, unsafe_allow_html=True)
except:
    st.warning("Imagem de avatar não carregada.")

# ===== RODAPÉ =====
st.divider()
st.caption("🎮 Dica: Clique nos cabeçalhos para ordenar | Atualize a página para resetar")
