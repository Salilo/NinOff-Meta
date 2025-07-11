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

IMAGE_URL = "https://pbs.twimg.com/media/EU0zpJrUwAA-d9i.jpg:large"  # Substitua pelo link desejado

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

# ===== LAYOUT PRINCIPAL =====
st.title("🔥 Nin0ff-Meta Calculator")

# Atributos base (mantenha como está)
cols = st.columns(2)
attributes_base = {}
with cols[0]:
    attributes_base["STR"] = st.number_input("STR", min_value=5, value=5, step=1, key="str_base")
    attributes_base["FRT"] = st.number_input("FRT", min_value=5, value=5, step=1, key="frt_base")
    attributes_base["INT"] = st.number_input("INT", min_value=5, value=5, step=1, key="int_base")
with cols[1]:
    attributes_base["AGI"] = st.number_input("AGI", min_value=5, value=5, step=1, key="agi_base")
    attributes_base["CHK"] = st.number_input("CHK", min_value=5, value=5, step=1, key="chk_base")
    
# ===== SIDEBAR ÚNICA =====
with st.sidebar:
    # Crie colunas dentro da sidebar
    col1, col2 = st.columns(2)
    
    # Coluna esquerda (configurações)
    with col1:
        st.header("⚙️ Configuração", divider="red")
        st.write("")  # Espaço vazio
        
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

    # Coluna direita (atributos finais)
    with col2:
        st.header("🧬 Atributos Finais", divider="blue")
        
        # Calcular atributos finais
        attributes = {
            "STR": apply_bonuses(attributes_base["STR"], charm, guild_level, "STR", faction_bonus),
            "FRT": apply_bonuses(attributes_base["FRT"], charm, guild_level, "FRT", faction_bonus),
            "INT": apply_bonuses(attributes_base["INT"], charm, guild_level, "INT", faction_bonus),
            "AGI": apply_bonuses(attributes_base["AGI"], charm, guild_level, "AGI", faction_bonus),
            "CHK": apply_bonuses(attributes_base["CHK"], charm, guild_level, "CHK", faction_bonus)
        }

        # Exibir os atributos
        st.metric("STR (Força)", attributes["STR"])
        st.metric("FRT (Resistência)", attributes["FRT"])
        st.metric("INT (Inteligência)", attributes["INT"])
        st.metric("AGI (Agilidade)", attributes["AGI"])
        st.metric("CHK (Controle)", attributes["CHK"])

        # Seletor de armas
        st.header("⚔️ Seleção de Arma", divider="gray")
        weapon_list = ["Nenhuma"] + list(weapons_db.keys())
        selected_weapon = st.selectbox("Escolha sua arma:", weapon_list, index=0)
        
        # Verificação de requisitos
        if selected_weapon and selected_weapon != "Nenhuma":
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
    "Fire": {
        "Phoenix Fireball Technique": {"base": 25, "scaling": "INT", "cost": 10, "cooldown": 12, "level": 10},
        "Big Flame Bullet Technique": {"base": 30, "scaling": "INT", "cost": 15, "cooldown": 14, "level": 15},
        "Fire Wall Technique": {"base": 28, "scaling": "INT", "cost": 12, "cooldown": 10, "level": 20},
        "Combusting Vortex": {"base": 35, "scaling": "INT", "cost": 18, "cooldown": 16, "level": 25},
        "Great Fireball Technique": {"base": 40, "scaling": "INT", "cost": 25, "cooldown": 20, "level": 30},
        "Flame Dragon Technique": {"base": 48, "scaling": "INT", "cost": 30, "cooldown": 24, "level": 35}
    },
    "Wind": {
        # INT Wind
        "Wind Shuriken Technique": {"base": 22, "scaling": "INT", "cost": 8, "cooldown": 10, "level": 10},
        "Wind Scythe Technique": {"base": 26, "scaling": "INT", "cost": 12, "cooldown": 12, "level": 15},
        "Drilling Air Bullet Technique": {"base": 30, "scaling": "INT", "cost": 14, "cooldown": 14, "level": 20},
        "Hurricane Blade Technique": {"base": 34, "scaling": "INT", "cost": 17, "cooldown": 15, "level": 25},
        "Vacuum Sphere Technique": {"base": 38, "scaling": "INT", "cost": 20, "cooldown": 17, "level": 30},
        "Wind Claw Technique": {"base": 42, "scaling": "INT", "cost": 23, "cooldown": 18, "level": 35},

        # STR Wind (Fan Style)
        "Slashing Tornado Technique": {"base": 28, "scaling": "STR", "cost": 12, "cooldown": 11, "level": 10},
        "Task of the Dragon Technique": {"base": 32, "scaling": "STR", "cost": 15, "cooldown": 13, "level": 15},
        "Slicing Wind Technique": {"base": 36, "scaling": "STR", "cost": 18, "cooldown": 15, "level": 20},
        "Wind Mask Technique": {"base": 40, "scaling": "STR", "cost": 22, "cooldown": 16, "level": 25},
        "Wind Barrage Technique": {"base": 44, "scaling": "STR", "cost": 25, "cooldown": 18, "level": 30},
        "Wind Cyclone": {"base": 50, "scaling": "STR", "cost": 30, "cooldown": 20, "level": 35}
    },
    "Lightning": {
        "Lightning Senbon Technique": {"base": 24, "scaling": "INT", "cost": 10, "cooldown": 10, "level": 10},
        "Lightning Spear Technique": {"base": 28, "scaling": "INT", "cost": 14, "cooldown": 12, "level": 15},
        "Lightning Cutter Technique": {"base": 32, "scaling": "INT", "cost": 17, "cooldown": 14, "level": 20},
        "Feast of Lightning Technique": {"base": 36, "scaling": "INT", "cost": 20, "cooldown": 15, "level": 25},
        "Lightning Current Technique": {"base": 40, "scaling": "INT", "cost": 24, "cooldown": 17, "level": 30},
        "Binding Pillars Techinque": {"base": 46, "scaling": "INT", "cost": 28, "cooldown": 20, "level": 35}
    },
    "Earth": {
        "Earth Pillar Technique": {"base": 26, "scaling": "STR", "cost": 12, "cooldown": 11, "level": 10},
        "Earth Prison Technique": {"base": 30, "scaling": "STR", "cost": 14, "cooldown": 13, "level": 15},
        "Earth Split Technique": {"base": 34, "scaling": "STR", "cost": 17, "cooldown": 15, "level": 20},
        "Ravaging Earth Spikes Technique": {"base": 38, "scaling": "STR", "cost": 20, "cooldown": 17, "level": 25},
        "Mud River Technique": {"base": 42, "scaling": "STR", "cost": 24, "cooldown": 18, "level": 30},
        "Earth Wall Technique": {"base": 48, "scaling": "STR", "cost": 28, "cooldown": 20, "level": 35}
    },
    "Water": {
        # INT Water
        "Water Bullet Technique": {"base": 22, "scaling": "INT", "cost": 9, "cooldown": 10, "level": 10},
        "Water Slash Technique": {"base": 26, "scaling": "INT", "cost": 12, "cooldown": 12, "level": 15},
        "Colliding Wave Technique": {"base": 30, "scaling": "INT", "cost": 15, "cooldown": 14, "level": 20},
        "Water Substitution Technique": {"base": 34, "scaling": "INT", "cost": 18, "cooldown": 15, "level": 25},
        "Water Prison Technique": {"base": 38, "scaling": "INT", "cost": 22, "cooldown": 17, "level": 30},
        "Great Water Shark Technique": {"base": 44, "scaling": "INT", "cost": 26, "cooldown": 20, "level": 35},

        # STR Water
        "Soap Bubble Technique": {"base": 24, "scaling": "STR", "cost": 10, "cooldown": 10, "level": 10},
        "Bubble Solution Spitting Technique": {"base": 28, "scaling": "STR", "cost": 13, "cooldown": 12, "level": 15},
        "Bubble Spray Technique": {"base": 32, "scaling": "STR", "cost": 16, "cooldown": 13, "level": 20},
        "Bubble Clone Technique": {"base": 36, "scaling": "STR", "cost": 20, "cooldown": 15, "level": 25},
        "Soap Explosion Technique": {"base": 40, "scaling": "STR", "cost": 23, "cooldown": 17, "level": 30},
        "Great Bubble Shark Technique": {"base": 46, "scaling": "STR", "cost": 27, "cooldown": 20, "level": 35}
    },
    "Medical": {
        "Treat Wounds Technique": {"base": 10, "scaling": "INT", "cost": 5, "cooldown": 10, "level": 10},
        "Poison Senbon Technique": {"base": 18, "scaling": "INT", "cost": 7, "cooldown": 12, "level": 15},
        "Poison Scalpel Technique": {"base": 22, "scaling": "INT", "cost": 9, "cooldown": 14, "level": 20},
        "Mystical Palm Technique": {"base": 26, "scaling": "INT", "cost": 11, "cooldown": 15, "level": 25},
        "Status Extraction Technique": {"base": 30, "scaling": "INT", "cost": 14, "cooldown": 17, "level": 30},
        "Chakra Scalpel Technique": {"base": 34, "scaling": "INT", "cost": 16, "cooldown": 20, "level": 35},
        "Antibodies Activation": {"base": 38, "scaling": "INT", "cost": 18, "cooldown": 22, "level": 35},
        "Poison Cloud Technique": {"base": 42, "scaling": "INT", "cost": 20, "cooldown": 24, "level": 35},
        "Cell Regeneration Activation": {"base": 46, "scaling": "INT", "cost": 23, "cooldown": 26, "level": 35},
        "Cursed Seal Activation": {"base": 50, "scaling": "INT", "cost": 26, "cooldown": 28, "level": 35},
        "Chakra Transfer Technique": {"base": 54, "scaling": "INT", "cost": 28, "cooldown": 30, "level": 35}
    },
    "Weapon": {
        # INT
        "Explosive Kunai Technique": {"base": 20, "scaling": "INT", "cost": 10, "cooldown": 10, "level": 10},
        "Triple Explosive Tag Technique": {"base": 24, "scaling": "INT", "cost": 12, "cooldown": 12, "level": 15},
        "Hidden Explosive Tag Technique": {"base": 28, "scaling": "INT", "cost": 14, "cooldown": 14, "level": 20},
        "Shadow Shuriken Technique": {"base": 32, "scaling": "INT", "cost": 16, "cooldown": 16, "level": 25},
        "Exploding Spiked Ball Technique": {"base": 36, "scaling": "INT", "cost": 18, "cooldown": 18, "level": 30},
        "Bear Trap Technique": {"base": 40, "scaling": "INT", "cost": 20, "cooldown": 20, "level": 35},

        # STR
        "Shockwave Slash Technique": {"base": 25, "scaling": "STR", "cost": 11, "cooldown": 11, "level": 10},
        "Risky Blade Dance Technique": {"base": 29, "scaling": "STR", "cost": 13, "cooldown": 13, "level": 15},
        "Blade Piercing Technique": {"base": 33, "scaling": "STR", "cost": 15, "cooldown": 15, "level": 20},
        "Wild Slashes Technique": {"base": 37, "scaling": "STR", "cost": 17, "cooldown": 17, "level": 25},
        "Crescent Moon Beheading Technique": {"base": 41, "scaling": "STR", "cost": 19, "cooldown": 19, "level": 30},
        "Dance of the Crescent Moon Technique": {"base": 45, "scaling": "STR", "cost": 22, "cooldown": 22, "level": 35}
    },
    "Taijutsu": {
        # AGI
        "Seismic Dash Technique": {"base": 26, "scaling": "AGI", "cost": 11, "cooldown": 10, "level": 10},
        "Breaking Kick Technique": {"base": 30, "scaling": "AGI", "cost": 13, "cooldown": 12, "level": 15},
        "Speed Mirage Technique": {"base": 34, "scaling": "AGI", "cost": 15, "cooldown": 14, "level": 20},
        "Youthful Spring Technique": {"base": 38, "scaling": "AGI", "cost": 18, "cooldown": 16, "level": 25},
        "Morning Peacock Technique": {"base": 42, "scaling": "AGI", "cost": 21, "cooldown": 18, "level": 30},
        "Whirlwind Kick Technique": {"base": 46, "scaling": "AGI", "cost": 24, "cooldown": 20, "level": 35},

        # STR
        "Pressure Point Needle Technique": {"base": 28, "scaling": "STR", "cost": 12, "cooldown": 10, "level": 10},
        "Water Needle Training": {"base": 32, "scaling": "STR", "cost": 14, "cooldown": 12, "level": 15},
        "Palm Bottom Technique": {"base": 36, "scaling": "STR", "cost": 16, "cooldown": 14, "level": 20},
        "Vacuum Palm Technique": {"base": 40, "scaling": "STR", "cost": 19, "cooldown": 16, "level": 25},
        "Mountain Crusher Technique": {"base": 44, "scaling": "STR", "cost": 22, "cooldown": 18, "level": 30},
        "Revolving Heavens Technique": {"base": 48, "scaling": "STR", "cost": 25, "cooldown": 20, "level": 35},
        "16 Palms Technique": {"base": 52, "scaling": "STR", "cost": 28, "cooldown": 22, "level": 35}
    },
    "Common": {
        "Body Flicker Technique": {"base": 0, "scaling": "N/A", "cost": 5, "cooldown": 10, "level": 1},
        "Charging Chakra": {"base": 0, "scaling": "N/A", "cost": 0, "cooldown": 5, "level": 1},
        "Cloak of Invisibility Technique": {"base": 0, "scaling": "N/A", "cost": 10, "cooldown": 15, "level": 1},
        "Clone Technique": {"base": 0, "scaling": "N/A", "cost": 8, "cooldown": 10, "level": 1},
        "Fuuma Wind Shuriken Technique": {"base": 20, "scaling": "STR", "cost": 10, "cooldown": 10, "level": 1},
        "Kunai Shadow Clone Technique": {"base": 20, "scaling": "INT", "cost": 10, "cooldown": 10, "level": 1},
        "Substitution Technique": {"base": 0, "scaling": "N/A", "cost": 10, "cooldown": 20, "level": 1},
        "Sensory Technique": {"base": 0, "scaling": "N/A", "cost": 10, "cooldown": 10, "level": 1},
        "Summoning Technique": {"base": 0, "scaling": "N/A", "cost": 25, "cooldown": 30, "level": 1},
        "Transformation Technique": {"base": 0, "scaling": "N/A", "cost": 8, "cooldown": 10, "level": 1},
        "Chakra Seal Technique": {"base": 0, "scaling": "N/A", "cost": 12, "cooldown": 20, "level": 1}
    }
}

if selected_weapon and selected_weapon != "Nenhuma":
    weapon_data = weapons_db[selected_weapon]
    meets_requirements = all(attributes.get(req, 0) >= val for req, val in weapon_data["requirements"].items())
    
    if meets_requirements:
        st.success("✅ Requisitos atendidos")
    else:
        st.error("❌ Requisitos não atendidos")
    
    # Cálculo de dano da arma
    scaling_value = attributes[weapon_data["scaling"]]
    weapon_damage = weapon_data["base_damage"] + (scaling_value * 0.6)
    st.metric("Dano da Arma", f"{weapon_damage:.1f}")

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

# ===== DANOS BÁSICOS =====
st.subheader("🗡️ Dano Básico")
cols = st.columns(4)

# Cálculos dos danos
melee_dmg = attributes["STR"] * 0.8
kunai_dmg = attributes["STR"] * 0.6
shuriken_dmg = attributes["STR"] * 0.5
senbon_dmg = attributes["STR"] * 0.4

# Exibição
with cols[0]:
    st.metric("Melee Dmg", f"{melee_dmg:.1f}")
with cols[1]:
    st.metric("Kunai Dmg", f"{kunai_dmg:.1f}")
with cols[2]:
    st.metric("Shuriken Dmg", f"{shuriken_dmg:.1f}")
with cols[3]:
    st.metric("Senbon Dmg", f"{senbon_dmg:.1f}")

st.write("---")  # Linha divisória

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
            height=min(600, 45 * len(df_combined) + 45))
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

img_url = "https://media.discordapp.net/attachments/225436696831983616/1393220653553025064/eIOxkDA.png?ex=68726158&is=68710fd8&hm=2f8b9ff16895844008dfb2a6ea94457fcefc228f482a81cebf617ee7f4c7bf72&="

try:
    response = requests.get(img_url)
    img = Image.open(BytesIO(response.content))
    
    # Restante do seu código...
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(img, width=360)
    with col2:
        st.markdown("""
        <div style="margin-top: 10px;">
            <h3 style="margin-bottom: 5px;">Nin0ff-Meta Calculator</h3>
            <p style="color: #666; font-size: 0.9em;">By <strong>Rin</strong></p>
            <p style="color: #666; font-size: 1.3em;">any problems contact me on discord</p>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.warning(f"Imagem de créditos não carregada. Erro: {str(e)}")

# ===== RODAPÉ =====
st.divider()
st.caption("🎮 Dica: Clique nos cabeçalhos para ordenar | Atualize a página para resetar")
