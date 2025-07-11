import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Nin0ff-Meta",
    page_icon="🔥",
    layout="wide"
)

# ===== CONSTANTES =====
ELEMENTS = ["Fire", "Wind", "Lightning", "Earth", "Medical", "Weapon", "Taijutsu"]
BASE_ATTRIBUTE = 5  # Todos atributos começam em 5

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

# ===== INTERFACE =====
st.title("🔥 Metanin Renewal Calculator")

# Sidebar - Configurações
with st.sidebar:
    st.header("Configuração do Personagem")
    
    # Elementos
    primary = st.selectbox("Elemento Primário", ELEMENTS, index=0)
    secondary = st.selectbox("Elemento Secundário", ELEMENTS, index=1)
    
    # Charm
    charms = [
        "Nenhum", "Capricorn", "Aquarius", "Leo", "Saggitarius", 
        "Virgo", "Cancer", "Pisces", "Libra", "Scorpio", "Gemini", "Taurus"
    ]
    charm = st.selectbox("Charm do Signo", charms)
    
    # Guild Level
    guild_level = st.slider("Status Level Guild", 0, 10, 0)
    
    # Atributos (base começa em 5)
    st.header("Atributos Base")
    str_base = st.number_input("STR", min_value=5, value=5)
    frt_base = st.number_input("FRT", min_value=5, value=5)
    int_base = st.number_input("INT", min_value=5, value=5)
    agi_base = st.number_input("AGI", min_value=5, value=5)
    chk_base = st.number_input("CHK", min_value=5, value=5)
    
    # Calcula atributos finais com bônus
    strength = apply_bonuses(str_base, charm, guild_level, "STR")
    fortitude = apply_bonuses(frt_base, charm, guild_level, "FRT")
    intellect = apply_bonuses(int_base, charm, guild_level, "INT")
    agility = apply_bonuses(agi_base, charm, guild_level, "AGI")
    chakra = apply_bonuses(chk_base, charm, guild_level, "CHK")
    
    # Mostra atributos finais
    st.header("Atributos com Bônus")
    st.write(f"STR: {str_base} → **{strength}**")
    st.write(f"FRT: {frt_base} → **{fortitude}**")
    st.write(f"INT: {int_base} → **{intellect}**")
    st.write(f"AGI: {agi_base} → **{agility}**")
    st.write(f"CHK: {chk_base} → **{chakra}**")
    
    # Calcula nível
    total_points = (str_base + frt_base + int_base + agi_base + chk_base) - (5 * 5)  # Remove base 5
    level = calculate_level(total_points)
    st.header("Nível do Personagem")
    st.metric("Level", level)

# ===== BANCO DE TÉCNICAS =====
techniques_db = {
    "Fire": {
        "Phoenix Fireball": {"base": 27, "scaling": "INT", "cost": 10, "cooldown": 16},
        "Big Flame Bullet": {"base": 35, "scaling": "INT", "cost": 30, "cooldown": 18},
        "Fire Wall": {"base": 22, "scaling": "INT", "cost": 15, "cooldown": 12},
        "Combusting Vortex": {"base": 40, "scaling": "INT", "cost": 45, "cooldown": 25},
        "Flame Dragon": {"base": 45, "scaling": "INT", "cost": 50, "cooldown": 30}
    },
    "Wind": {
        "Wind Shuriken (INT)": {"base": 25, "scaling": "INT", "cost": 12, "cooldown": 10},
        "Wind Scythe (INT)": {"base": 32, "scaling": "INT", "cost": 20, "cooldown": 15},
        "Slashing Tornado (STR)": {"base": 30, "scaling": "STR", "cost": 25, "cooldown": 18},
        "Wind Cyclone (STR)": {"base": 40, "scaling": "STR", "cost": 35, "cooldown": 25}
    },
    "Weapon": {
        "Kunai": {"base": 1, "scaling": "STR", "cost": 0, "cooldown": 0},
        "Shuriken": {"base": 1, "scaling": "INT", "cost": 0, "cooldown": 0},
        "Senbon": {"base": 1, "scaling": "CHK", "cost": 0, "cooldown": 0}
    }
}

# ===== TABELA DE TÉCNICAS =====
st.header(f"Técnicas de {primary}")

# Filtra técnicas do elemento primário
tech_data = techniques_db.get(primary, {})
if not tech_data:
    st.warning("Nenhuma técnica disponível para este elemento")
else:
    # Prepara os dados para a tabela
    techniques_list = []
    scaling_map = {"STR": strength, "INT": intellect, "CHK": chakra}
    
    for name, data in tech_data.items():
        scaling_value = scaling_map[data["scaling"]]
        damage = data["base"] + (scaling_value * 0.6)
        dps = damage / data["cooldown"] if data["cooldown"] > 0 else 0
        
        techniques_list.append({
            "Técnica": name,
            "Elemento": primary,
            "Dano Base": data["base"],
            "Scaling": data["scaling"],
            "Dano Total": f"{damage:.1f}",
            "DPS": f"{dps:.1f}",
            "Custo Chakra": data["cost"],
            "Cooldown": data["cooldown"]
        })

    # Exibe a tabela
    df = pd.DataFrame(techniques_list)
    st.dataframe(
        df,
        column_config={
            "Dano Total": st.column_config.NumberColumn(format="%.1f"),
            "DPS": st.column_config.NumberColumn(format="%.1f")
        },
        hide_index=True,
        use_container_width=True
    )

# ===== RODAPÉ =====
st.divider()
st.caption("✨ Dica: Clique no cabeçalho da tabela para ordenar os resultados")
