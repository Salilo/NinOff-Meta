import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

# ===== CONFIGURAÇÃO =====
st.set_page_config(
    page_title="Nin0ff-Meta",
    page_icon="🔥",
    layout="wide"
)

# ===== CONSTANTES =====
ELEMENTS = ["Fire", "Wind", "Lightning", "Earth", "Medical", "Weapon", "Taijutsu"]
BASE_ATTRIBUTE = 5
MAX_POINTS = 285
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
IMAGE_URL = "https://via.placeholder.com/80"  # ← COLOQUE SEU LINK AQUI

# ===== FUNÇÕES =====
def calculate_level(total_points):
    level = 1
    points_needed = 0
    while level <= 60 and points_needed <= MAX_POINTS:
        points_per_level = 5 if level <= 50 else 4
        points_needed += points_per_level
        if total_points >= points_needed and points_needed <= MAX_POINTS:
            level += 1
        else:
            break
    return min(level, 60)

def calculate_available_points(level):
    """Calcula pontos disponíveis baseado no nível"""
    if level <= 50:
        return (level - 1) * 5
    else:
        return (50 * 5) + ((level - 50) * 4)

def apply_bonuses(base_value, charm, guild_level, attr_name):
    value_with_guild = base_value * (1 + guild_level * 0.01)
    charm_bonuses = {
        "Capricorn": {"FRT": 5}, "Aquarius": {"INT": 5}, "Leo": {"AGI": 5},
        "Saggitarius": {attr: 1 for attr in ["STR", "FRT", "INT", "AGI", "CHK"]},
        "Virgo": {"CHK": 5}, "Cancer": {"STR": 1}, "Pisces": {attr: 1 for attr in ["STR", "FRT", "INT", "AGI", "CHK"]},
        "Libra": {"INT": 0.05}, "Scorpio": {"AGI": 1}, "Gemini": {"CHK": 1}, "Taurus": {"FRT": 1}
    }
    bonus = charm_bonuses.get(charm, {}).get(attr_name, 0)
    return int(value_with_guild * (1 + bonus)) if isinstance(bonus, float) else int(value_with_guild + bonus)

def style_element(row):
    color = COLORS[row["Elemento"]]
    return [f"background-color: {color}; color: #000000" for _ in row]

# ===== CABEÇALHO PERSONALIZADO =====
col1, col2 = st.columns([0.9, 0.1])
with col1:
    st.title("🔥 Nin0ff-Meta Calculator")
with col2:
    st.markdown("""
    <div style="text-align: right;">
        <small>by Rin</small><br>
    </div>
    """, unsafe_allow_html=True)
    
    # Carrega imagem do link
    try:
        response = requests.get(IMAGE_URL)
        img = Image.open(BytesIO(response.content))
        st.image(img, width=80)
    except:
        st.warning("Imagem não carregada")

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
    attributes_base = {}
    with cols[0]:
        attributes_base["STR"] = st.number_input("STR", min_value=5, value=5, step=1)
        attributes_base["FRT"] = st.number_input("FRT", min_value=5, value=5, step=1)
        attributes_base["INT"] = st.number_input("INT", min_value=5, value=5, step=1)
    with cols[1]:
        attributes_base["AGI"] = st.number_input("AGI", min_value=5, value=5, step=1)
        attributes_base["CHK"] = st.number_input("CHK", min_value=5, value=5, step=1)
    
    # Calcula atributos com bônus
    attributes = {
        "STR": apply_bonuses(attributes_base["STR"], charm, guild_level, "STR"),
        "FRT": apply_bonuses(attributes_base["FRT"], charm, guild_level, "FRT"),
        "INT": apply_bonuses(attributes_base["INT"], charm, guild_level, "INT"),
        "AGI": apply_bonuses(attributes_base["AGI"], charm, guild_level, "AGI"),
        "CHK": apply_bonuses(attributes_base["CHK"], charm, guild_level, "CHK")
    }
    
    # Cálculos
    total_points_spent = sum(attributes_base.values()) - (5 * 5)
    level = calculate_level(total_points_spent)
    total_points_available = calculate_available_points(level)
    remaining_points = max(0, total_points_available - total_points_spent)
    
    st.header("📊 Status", divider="gray")
    st.metric("Pontos Gastos", f"{total_points_spent}/{MAX_POINTS}")
    st.metric("Pontos Disponíveis", remaining_points)
    st.metric("Nível", level)
    
    # Verifica se excedeu o limite
    if total_points_spent > MAX_POINTS:
        st.error(f"Limite de {MAX_POINTS} pontos excedido!")
    elif total_points_spent > total_points_available:
        st.warning("Pontos gastos excedem os disponíveis para este nível")

# ===== BANCO DE TÉCNICAS =====
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

# ===== TABELA DE TÉCNICAS =====
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
            "Dano Total": f"{damage:.1f}",
            "DPS": f"{dps:.1f}",
            "Chakra": data["cost"],
            "Cooldown": data["cooldown"]
        })
    
    return pd.DataFrame(tech_list)

# Cria e exibe a tabela
try:
    df_primary = create_tech_df(primary)
    df_secondary = create_tech_df(secondary)
    df_combined = pd.concat([df_primary, df_secondary])
    
    st.header(f"📜 Técnicas de {primary} + {secondary}")
    
    if not df_combined.empty:
        # Aplica estilo
        styled_df = df_combined.style.apply(style_element, axis=1).format(precision=1)
        
        # Chamada CORRIGIDA do dataframe - FALTAVA FECHAR PARÊNTESE
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
# ===== RODAPÉ =====
st.divider()
st.caption("🎮 Dica: Clique nos cabeçalhos para ordenar | Atualize a página para resetar")
