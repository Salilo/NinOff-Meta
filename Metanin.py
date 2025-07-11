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
    "Water": "💧", "Medical": "🧪", "Weapon": "🗡️", "Taijutsu": "🥋"
}
COLORS = {
    "Fire": "#FF5555", "Wind": "#55FF55", "Lightning": "#FFFF55",
    "Earth": "#FFAA55", "Water": "#55AAFF", "Medical": "#55FFAA", 
    "Weapon": "#AAAAAA", "Taijutsu": "#AA55FF", "Common": "#DDDDDD"
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
    nome_elemento = row["Elemento"].split(" ", 1)[-1]  # Remove emoji
    color = COLORS.get(nome_elemento, "#FFFFFF")
    return [f"background-color: {color}; color: #000000" for _ in row]

def style_weapon(row):
    meets_req = row["Atende Requisitos"]
    color = "#55FF55" if meets_req else "#FF5555"
    return [f"background-color: {color}; color: #000000" for _ in row]

# ===== BANCO DE DADOS DE ARMAS =====
weapons_db = {
    "Kunai Dagger": {
        "base_damage": 9,
        "scaling": "STR",
        "requirements": {"INT": 10},
        "description": "Kunai padrão para combate à distância"
    },
    "Poison-Laced Kunai": {
        "base_damage": 9,
        "scaling": "STR",
        "requirements": {"INT": 10},
        "description": "Envenena o alvo ao acertar"
    },
    "Wooden Katana": {
        "base_damage": 2,
        "scaling": "STR",
        "requirements": {"STR": 12},
        "description": "Katana de madeira para treinamento"
    }
}

# ===== INTERFACE PRINCIPAL =====
st.title("🔥 Nin0ff-Meta Calculator")

# ===== SIDEBAR =====
with st.sidebar:
    st.header("⚙️ Configuração", divider="red")

    # Faction Bonuses
    st.subheader("🏛️ Faction Bonuses")
    faction = st.radio("Selecione sua facção:", 
                      ["Nenhuma", "Akatsuki (+25)", "Kage (+20)", "Leaf 12 Guardian (+10)"],
                      index=0)
    
    faction_bonus = 0
    if "Akatsuki" in faction:
        faction_bonus = 25
    elif "Kage" in faction:
        faction_bonus = 20
    elif "Leaf" in faction:
        faction_bonus = 10

    cols = st.columns(2)
    with cols[0]:
        primary = st.selectbox("Primário", ELEMENTS, format_func=label_with_emoji)
    with cols[1]:
        available_secondary = [e for e in ELEMENTS if e != primary]
        secondary = st.selectbox("Secundário", available_secondary, format_func=label_with_emoji)

    charms = ["Nenhum"] + list(SIGN_EMOJIS.keys())
    charm = st.selectbox("Charm", charms, index=0, format_func=label_charm)

    guild_level = st.slider("Guild Level Status", 0, 10, 0)

    # Atributos
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

    # Atributos com bônus
    attributes = {
        attr: apply_bonuses(val, charm, guild_level, attr, faction_bonus)
        for attr, val in attributes_base.items()
    }

    # Cálculos de pontos
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

    # Mostrar atributos finais
    st.header("🎯 Atributos Finais", divider="gray")
    for attr, value in attributes.items():
        st.write(f"{attr}: {value}")

    # Seletor de armas
    st.header("⚔️ Seleção de Arma", divider="gray")
    weapon_list = list(weapons_db.keys())
    selected_weapon = st.selectbox("Escolha sua arma:", weapon_list)
    
    # Verifica requisitos da arma
    weapon_data = weapons_db[selected_weapon]
    meets_requirements = all(attributes.get(req, 0) >= val for req, val in weapon_data["requirements"].items())
    
    if meets_requirements:
        st.success("✅ Requisitos atendidos")
    else:
        st.error("❌ Requisitos não atendidos")
    
    st.write(f"**Dano Base:** {weapon_data['base_damage']}")
    st.write(f"**Escalonamento:** {weapon_data['scaling']}")
    st.write(f"**Descrição:** {weapon_data['description']}")

    # Botão para mostrar técnicas comuns
    show_common = st.toggle("Mostrar Técnicas Comuns", value=False)

# ===== TÉCNICAS =====
techniques_db = {
    # ... (mantenha seu banco de técnicas existente aqui)
    # Adicionei Water ao dicionário ELEMENTS e EMOJI_MAP no início
}

# ===== CÁLCULO DE DANO DE ARMA =====
if selected_weapon:
    weapon_data = weapons_db[selected_weapon]
    scaling_value = attributes[weapon_data["scaling"]]
    weapon_damage = weapon_data["base_damage"] + (scaling_value * 0.6)
    st.sidebar.metric("Dano da Arma", f"{weapon_damage:.1f}")

# ===== EXIBIÇÃO DE TÉCNICAS =====
def create_tech_df(element):
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

# Técnicas dos elementos principais
try:
    df_primary = create_tech_df(primary)
    df_secondary = create_tech_df(secondary)
    df_combined = pd.concat([df_primary, df_secondary]).reset_index(drop=True)

    st.header(f"📜 Técnicas de {label_with_emoji(primary)} + {label_with_emoji(secondary)}")
    if not df_combined.empty:
        styled_df = df_combined.style.apply(style_element, axis=1).format({
            "Dano Total": "{:.1f}",
            "DPS": "{:.1f}"
        })
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

# Técnicas comuns (se ativado)
if show_common:
    try:
        df_common = create_tech_df("Common")
        if not df_common.empty:
            st.header(f"📜 Técnicas Comuns")
            styled_common = df_common.style.apply(style_element, axis=1).format({
                "Dano Total": "{:.1f}",
                "DPS": "{:.1f}"
            })
            st.dataframe(
                styled_common,
                column_config={
                    "Dano Total": st.column_config.NumberColumn(format="%.1f"),
                    "DPS": st.column_config.NumberColumn(format="%.1f")
                },
                hide_index=True,
                use_container_width=True
            )
    except Exception as e:
        st.error(f"Erro ao gerar tabela de técnicas comuns: {str(e)}")

# ===== CRÉDITOS E IMAGEM =====
try:
    response = requests.get(IMAGE_URL)
    img = Image.open(BytesIO(response.content))
    
    # Redimensiona a imagem
    img.thumbnail((150, 150))
    
    # Cria layout de créditos elegante
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(img, width=100)
    with col2:
        st.markdown("""
        <div style="margin-top: 20px;">
            <h3 style="margin-bottom: 5px;">Nin0ff-Meta Calculator</h3>
            <p style="color: #666; font-size: 0.9em;">Desenvolvido por <strong>Rin</strong></p>
            <p style="color: #666; font-size: 0.8em;">Versão 2.0 | 2023</p>
        </div>
        """, unsafe_allow_html=True)
except:
    st.warning("Imagem de créditos não carregada.")

# ===== RODAPÉ =====
st.divider()
st.caption("🎮 Dica: Clique nos cabeçalhos para ordenar | Atualize a página para resetar")
