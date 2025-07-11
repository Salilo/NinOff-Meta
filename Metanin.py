import streamlit as st
import pandas as pd
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Metanin Renewal Calculator",
    page_icon="🔥",
    layout="wide"
)

# ===== CONSTANTES =====
ELEMENTS = ["Fire", "Wind", "Lightning", "Earth", "Medical", "Weapon", "Taijutsu"]
BASE_ATTRIBUTE = 5  # Todos atributos começam em 5
COLORS = {
    "Fire": "#FF5555",
    "Wind": "#55FF55",
    "Lightning": "#FFFF55",
    "Earth": "#FFAA55",
    "Medical": "#55FFAA",
    "Weapon": "#AAAAAA",
    "Taijutsu": "#AA55FF"
}

# ===== FUNÇÕES =====
def calculate_level(total_points):
    """Calcula o nível baseado nos pontos gastos"""
    level = 1
    points_needed = 0
    
    while level <= 60:
        points_per_level = 5 if level <= 50 else 4
        points_needed += points_per_level
        if total_points >= points_needed:
            level += 1
        else:
            break
    return min(level, 60)

def apply_bonuses(base_value, charm, guild_level, attr_name):
    """Aplica bônus de charm e guild level"""
    # Bônus do Guild Level (1% por nível)
    value_with_guild = base_value * (1 + guild_level * 0.01)
    
    # Bônus do Charm
    charm_bonuses = {
        "Capricorn": {"FRT": 5},
        "Aquarius": {"INT": 5},
        "Leo": {"AGI": 5},
        "Saggitarius": {attr: 1 for attr in ["STR", "FRT", "INT", "AGI", "CHK"]},
        "Virgo": {"CHK": 5},
        "Cancer": {"STR": 1},
        "Pisces": {attr: 1 for attr in ["STR", "FRT", "INT", "AGI", "CHK"]},
        "Libra": {"INT": 0.05},  # 5%
        "Scorpio": {"AGI": 1},
        "Gemini": {"CHK": 1},
        "Taurus": {"FRT": 1}
    }
    
    bonus = charm_bonuses.get(charm, {}).get(attr_name, 0)
    
    if isinstance(bonus, float):
        return int(value_with_guild * (1 + bonus))
    else:
        return int(value_with_guild + bonus)

def style_element(row):
    """Aplica cores aos elementos na tabela"""
    color = COLORS[row["Elemento"]]
    return [f"background-color: {color}; color: #000000" for _ in row]

# ===== INTERFACE =====
st.title("🔥 Metanin Renewal Calculator")

# Sidebar - Configurações (otimizada)
with st.sidebar:
    st.header("⚙️ Configuração", divider="red")
    
    # Elementos em colunas compactas
    col1, col2 = st.columns(2)
    with col1:
        primary = st.selectbox("Primário", ELEMENTS, index=0, key="primary")
    with col2:
        secondary = st.selectbox("Secundário", ELEMENTS, index=1, key="secondary")
    
    # Charm compacto
    charms = [
        "Nenhum", "Capricorn", "Aquarius", "Leo", "Saggitarius", 
        "Virgo", "Cancer", "Pisces", "Libra", "Scorpio", "Gemini", "Taurus"
    ]
    charm = st.selectbox("Charm", charms, index=0)
    
    # Guild Level compacto
    guild_level = st.slider("Guild Level", 0, 10, 0, help="+1% em todos atributos por nível")
    
    # Atributos em colunas compactas
    st.header("🧬 Atributos Base", divider="gray")
    cols = st.columns(2)
    attributes = {}
    with cols[0]:
        attributes["STR"] = st.number_input("STR", min_value=5, value=5, step=1, key="str")
        attributes["FRT"] = st.number_input("FRT", min_value=5, value=5, step=1, key="frt")
        attributes["INT"] = st.number_input("INT", min_value=5, value=5, step=1, key="int")
    with cols[1]:
        attributes["AGI"] = st.number_input("AGI", min_value=5, value=5, step=1, key="agi")
        attributes["CHK"] = st.number_input("CHK", min_value=5, value=5, step=1, key="chk")
    
    # Calcula pontos
    total_points_spent = sum(attributes.values()) - (5 * 5)
    total_points_available = (calculate_level(total_points_spent) - 1) * 5
    if calculate_level(total_points_spent) > 50:
        total_points_available += (calculate_level(total_points_spent) - 50) * 4
    
    # Mostra resumo
    st.header("📊 Status", divider="gray")
    st.metric("Pontos Gastos", total_points_spent)
    st.metric("Pontos Disponíveis", max(0, total_points_available - total_points_spent))
    st.metric("Nível", calculate_level(total_points_spent))

# ===== BANCO DE TÉCNICAS =====
techniques_db = {
    "Fire": {
        "Phoenix Fireball": {"base": 27, "scaling": "INT", "cost": 10, "cooldown": 16},
        "Big Flame Bullet": {"base": 35, "scaling": "INT", "cost": 30, "cooldown": 18},
        "Fire Wall": {"base": 22, "scaling": "INT", "cost": 15, "cooldown": 12}
    },
    "Wind": {
        "Wind Shuriken (INT)": {"base": 25, "scaling": "INT", "cost": 12, "cooldown": 10},
        "Wind Scythe (INT)": {"base": 32, "scaling": "INT", "cost": 20, "cooldown": 15},
        "Slashing Tornado (STR)": {"base": 30, "scaling": "STR", "cost": 25, "cooldown": 18}
    },
    "Weapon": {
        "Kunai": {"base": 1, "scaling": "STR", "cost": 0, "cooldown": 0},
        "Shuriken": {"base": 1, "scaling": "INT", "cost": 0, "cooldown": 0},
        "Senbon": {"base": 1, "scaling": "CHK", "cost": 0, "cooldown": 0}
    }
}

# ===== TABELA DE TÉCNICAS =====
def create_technique_table(element):
    """Cria dataframe com técnicas de um elemento"""
    tech_data = techniques_db.get(element, {})
    techniques_list = []
    scaling_map = {"STR": attributes["STR"], "INT": attributes["INT"], "CHK": attributes["CHK"]}
    
    for name, data in tech_data.items():
        scaling_value = scaling_map[data["scaling"]]
        damage = data["base"] + (scaling_value * 0.6)
        dps = damage / data["cooldown"] if data["cooldown"] > 0 else 0
        
        techniques_list.append({
            "Técnica": name,
            "Elemento": element,
            "Dano Base": data["base"],
            "Scaling": data["scaling"],
            "Dano Total": damage,
            "DPS": dps,
            "Chakra": data["cost"],
            "Cooldown": data["cooldown"]
        })
    
    return pd.DataFrame(techniques_list)

# Tabela combinada (primário + secundário)
df_primary = create_technique_table(primary)
df_secondary = create_technique_table(secondary)
df_combined = pd.concat([df_primary, df_secondary])

# Estilo da tabela
def color_scaling(val):
    color = {
        "STR": "#FF9999",
        "INT": "#99FF99",
        "CHK": "#9999FF"
    }.get(val, "#FFFFFF")
    return f"background-color: {color}"

st.header(f"📜 Técnicas de {primary} + {secondary}")
if not df_combined.empty:
    st.dataframe(
        df_combined.style
            .apply(style_element, axis=1)
            .applymap(color_scaling, subset=["Scaling"])
            .format({
                "Dano Total": "{:.1f}",
                "DPS": "{:.1f}"
            }),
        column_order=["Técnica", "Elemento", "Dano Base", "Scaling", "Dano Total", "DPS", "Chakra", "Cooldown"],
        hide_index=True,
        use_container_width=True,
        height=min(600, 45 * len(df_combined) + 45)
    )
else:
    st.warning("Nenhuma técnica disponível para estes elementos")

# ===== RODAPÉ =====
st.divider()
st.caption("🎮 Dica: Ordene a tabela clicando nos cabeçalhos | Atualize a página para resetar")
