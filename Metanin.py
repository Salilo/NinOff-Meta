import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from PIL import Image, ImageTk
import os

class MetaninRenewalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Metanin Renewal - Advanced Damage Calculator")
        self.root.geometry("1200x850")
        self.root.configure(bg="#2c3e50")
        
        # Configuração de estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar cores
        self.setup_colors()
        self.setup_styles()
        
        # Configuração inicial
        self.level = 1
        self.max_level = 60
        self.points_per_level_1_50 = 5
        self.points_per_level_50_60 = 4
        self.max_points = 285
        self.total_points_spent = 0
        self.charm = None
        self.primary_element = None
        self.secondary_element = None
        self.guild_level = 0  # Nível do Status Level Guild (0-10)
        
        # Atributos base
        self.base_attributes = {
            "Strength": 0,
            "Fortitude": 0,
            "Intellect": 0,
            "Agility": 0,
            "Chakra": 0
        }
        
        # Bônus de charm (com descrição)
        self.charm_bonuses = {
            "Capricorn": {"Fortitude": 5, "desc": "+5 FRT"},
            "Aquarius": {"Intellect": 5, "desc": "+5 INT"},
            "Leo": {"Agility": 5, "desc": "+5 AGI"},
            "Saggitarius": {attr: 1 for attr in ["Strength", "Fortitude", "Intellect", "Agility", "Chakra"]},
            "Virgo": {"Chakra": 5, "desc": "+5 CHK"},
            "Cancer": {"Strength": 1, "desc": "+1 STR"},
            "Pisces": {attr: 1 for attr in ["Strength", "Fortitude", "Intellect", "Agility", "Chakra"]},
            "Libra": {"Intellect": 0.05, "desc": "+5% INT"},
            "Scorpio": {"Agility": 1, "desc": "+1 AGI"},
            "Gemini": {"Chakra": 1, "desc": "+1 CHK"},
            "Taurus": {"Fortitude": 1, "desc": "+1 FRT"}
        }
        self.charm_bonuses["Saggitarius"]["desc"] = "+1 ALL"
        self.charm_bonuses["Pisces"]["desc"] = "+1 ALL"
        
        # Elementos disponíveis e suas cores
        self.elements = {
            "Fire": {"color": "#e74c3c", "bg": "#2a0a06", "highlight": "#ff6b5b"},
            "Wind": {"color": "#1abc9c", "bg": "#06201a", "highlight": "#2cecc71"},
            "Lightning": {"color": "#f1c40f", "bg": "#2a2306", "highlight": "#ffe44f"},
            "Earth": {"color": "#e67e22", "bg": "#2a1606", "highlight": "#ff9e44"},
            "Medical": {"color": "#2ecc71", "bg": "#062012", "highlight": "#4eff9d"},
            "Weapon": {"color": "#95a5a6", "bg": "#1a1f20", "highlight": "#bdc3c7"},
            "Taijutsu": {"color": "#9b59b6", "bg": "#1e062a", "highlight": "#bf7fd9"}
        }
        
        # Técnicas por elemento (com custo de chakra e cooldown)
        self.techniques = {
            "Fire": {
                "Phoenix Fireball Technique": {"base_damage": 27, "scaling": "Intellect", "chakra_cost": 10, "cooldown": 16},
                "Big Flame Bullet Technique": {"base_damage": 35, "scaling": "Intellect", "chakra_cost": 30, "cooldown": 18},
                "Fire Wall Technique": {"base_damage": 22, "scaling": "Intellect", "chakra_cost": 15, "cooldown": 12},
                "Combusting Vortex": {"base_damage": 40, "scaling": "Intellect", "chakra_cost": 45, "cooldown": 25},
                "Great Fireball Technique": {"base_damage": 30, "scaling": "Intellect", "chakra_cost": 25, "cooldown": 20},
                "Flame Dragon Technique": {"base_damage": 45, "scaling": "Intellect", "chakra_cost": 50, "cooldown": 30}
            },
            "Wind": {
                "Wind Shuriken Technique (INT)": {"base_damage": 25, "scaling": "Intellect", "chakra_cost": 12, "cooldown": 10},
                "Wind Scythe Technique (INT)": {"base_damage": 32, "scaling": "Intellect", "chakra_cost": 20, "cooldown": 15},
                "Drilling Air Bullet Technique (INT)": {"base_damage": 28, "scaling": "Intellect", "chakra_cost": 18, "cooldown": 12},
                "Hurricane Blade Technique (INT)": {"base_damage": 38, "scaling": "Intellect", "chakra_cost": 30, "cooldown": 20},
                "Vacuum Sphere Technique (INT)": {"base_damage": 42, "scaling": "Intellect", "chakra_cost": 35, "cooldown": 25},
                "Wind Claw Technique (INT)": {"base_damage": 20, "scaling": "Intellect", "chakra_cost": 10, "cooldown": 8},
                "Slashing Tornado Technique (STR)": {"base_damage": 30, "scaling": "Strength", "chakra_cost": 25, "cooldown": 18},
                "Task of the Dragon Technique (STR)": {"base_damage": 45, "scaling": "Strength", "chakra_cost": 40, "cooldown": 30},
                "Slicing Wind Technique (STR)": {"base_damage": 25, "scaling": "Strength", "chakra_cost": 15, "cooldown": 12},
                "Wind Mask Technique (STR)": {"base_damage": 15, "scaling": "Strength", "chakra_cost": 10, "cooldown": 10},
                "Wind Barrage Technique (STR)": {"base_damage": 35, "scaling": "Strength", "chakra_cost": 30, "cooldown": 20},
                "Wind Cyclone (STR)": {"base_damage": 40, "scaling": "Strength", "chakra_cost": 35, "cooldown": 25}
            },
            "Lightning": {},
            "Earth": {},
            "Medical": {},
            "Weapon": {
                "Kunai": {"base_damage": 1, "scaling": "Strength", "chakra_cost": 0, "cooldown": 0},
                "Shuriken": {"base_damage": 1, "scaling": "Intellect", "chakra_cost": 0, "cooldown": 0},
                "Senbon": {"base_damage": 1, "scaling": "Chakra", "chakra_cost": 0, "cooldown": 0}
            },
            "Taijutsu": {}
        }
        
        # DPS tracking
        self.dps_data = {}
        self.total_chakra_cost = 0
        
        # Carregar imagem do personagem (se existir)
        self.character_image = None
        self.load_character_image()
        
        self.create_widgets()
        self.update_points_display()
    
    def load_character_image(self):
        """Tenta carregar a imagem do personagem se existir"""
        image_path = "character.png"
        if os.path.exists(image_path):
            try:
                image = Image.open(image_path)
                image = image.resize((150, 200), Image.Resampling.LANCZOS)
                self.character_image = ImageTk.PhotoImage(image)
            except:
                self.character_image = None
    
    def setup_colors(self):
        self.bg_color = "#2c3e50"
        self.frame_bg = "#34495e"
        self.text_color = "#ecf0f1"
        self.accent_color = "#3498db"
        self.button_color = "#2980b9"
        
    def setup_styles(self):
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color)
        self.style.configure('TLabelFrame', background=self.bg_color, foreground=self.accent_color)
        self.style.configure('TLabelFrame.Label', background=self.bg_color, foreground=self.accent_color)
        self.style.configure('TButton', background=self.button_color, foreground=self.text_color)
        self.style.map('TButton', background=[('active', self.accent_color)])
        self.style.configure('TNotebook', background=self.bg_color)
        self.style.configure('TNotebook.Tab', background="#7f8c8d", foreground=self.text_color)
        self.style.map('TNotebook.Tab', background=[('selected', self.accent_color)])
        self.style.configure('TEntry', fieldbackground=self.frame_bg, foreground=self.text_color)
        self.style.configure('TSpinbox', fieldbackground=self.frame_bg, foreground=self.text_color)
        self.style.configure('TCombobox', fieldbackground=self.frame_bg, foreground=self.text_color)
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame esquerdo (atributos e configurações)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="y", padx=5, pady=5)
        
        # Frame direito (técnicas e resultados)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Configuração do personagem com imagem
        config_frame = ttk.LabelFrame(left_frame, text="Character Configuration")
        config_frame.pack(fill="x", padx=5, pady=5)
        
        # Frame para imagem e elementos
        top_config_frame = ttk.Frame(config_frame)
        top_config_frame.pack(fill="x", pady=5)
        
        # Imagem do personagem (se carregada)
        if self.character_image:
            img_label = ttk.Label(top_config_frame, image=self.character_image)
            img_label.pack(side="left", padx=5)
        
        # Frame para elementos e charm
        elements_frame = ttk.Frame(top_config_frame)
        elements_frame.pack(side="right", fill="both", expand=True)
        
        # Elementos
        ttk.Label(elements_frame, text="Primary Element:").grid(row=0, column=0, sticky="w")
        self.primary_element_var = tk.StringVar()
        primary_element_menu = ttk.OptionMenu(elements_frame, self.primary_element_var, "", *self.elements.keys())
        primary_element_menu.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.primary_element_var.trace("w", self.update_element_techniques)
        
        ttk.Label(elements_frame, text="Secondary Element:").grid(row=1, column=0, sticky="w")
        self.secondary_element_var = tk.StringVar()
        secondary_element_menu = ttk.OptionMenu(elements_frame, self.secondary_element_var, "", *self.elements.keys())
        secondary_element_menu.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.secondary_element_var.trace("w", self.update_element_techniques)
        
        # Charm
        ttk.Label(elements_frame, text="Zodiac Charm:").grid(row=2, column=0, sticky="w")
        self.charm_var = tk.StringVar()
        
        # Criar menu de charms com descrição dos bônus
        charm_menu = ttk.Combobox(elements_frame, textvariable=self.charm_var, state="readonly")
        charm_menu['values'] = [f"{name} ({data['desc']})" for name, data in self.charm_bonuses.items()]
        charm_menu.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        charm_menu.bind("<<ComboboxSelected>>", self.update_charm_selection)
        
        # Status Level Guild
        ttk.Label(elements_frame, text="Status Level Guild:").grid(row=3, column=0, sticky="w")
        self.guild_level_var = tk.IntVar(value=0)
        guild_spin = ttk.Spinbox(elements_frame, from_=0, to=10, textvariable=self.guild_level_var, width=5)
        guild_spin.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        self.guild_level_var.trace("w", self.update_guild_level)
        
        # Atributos com botões de +/-
        attr_frame = ttk.LabelFrame(left_frame, text="Attributes")
        attr_frame.pack(fill="x", padx=5, pady=5)
        
        self.attr_entries = {}
        self.attr_vars = {}
        row = 0
        for attr in self.base_attributes:
            # Frame para cada atributo
            attr_row = ttk.Frame(attr_frame)
            attr_row.grid(row=row, column=0, sticky="ew", pady=2)
            
            ttk.Label(attr_row, text=f"{attr}:").pack(side="left", padx=5)
            
            # Botão -
            minus_btn = ttk.Button(attr_row, text="-", width=2, 
                                 command=lambda a=attr: self.change_attribute(a, -1))
            minus_btn.pack(side="left")
            
            # Valor do atributo
            self.attr_vars[attr] = tk.IntVar(value=0)
            attr_entry = ttk.Entry(attr_row, textvariable=self.attr_vars[attr], width=5)
            attr_entry.pack(side="left", padx=2)
            self.attr_vars[attr].trace("w", self.update_points_spent)
            
            # Botão +
            plus_btn = ttk.Button(attr_row, text="+", width=2,
                                command=lambda a=attr: self.change_attribute(a, 1))
            plus_btn.pack(side="left")
            
            # Label para mostrar valor com bônus
            self.attr_entries[attr] = ttk.Label(attr_row, text="0")
            self.attr_entries[attr].pack(side="left", padx=5)
            
            row += 1
        
        # Informações do personagem
        info_frame = ttk.LabelFrame(left_frame, text="Character Info")
        info_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(info_frame, text="Level:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.level_label = ttk.Label(info_frame, text="1")
        self.level_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_frame, text="Points Available:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.points_label = ttk.Label(info_frame, text="0")
        self.points_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_frame, text="Points Spent:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.spent_label = ttk.Label(info_frame, text="0")
        self.spent_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # DPS Calculator
        dps_frame = ttk.LabelFrame(left_frame, text="DPS Calculator")
        dps_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(dps_frame, text="Rotation DPS:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.dps_label = ttk.Label(dps_frame, text="0.0", font=('Helvetica', 10, 'bold'))
        self.dps_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(dps_frame, text="Total Chakra Cost:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.chakra_cost_label = ttk.Label(dps_frame, text="0", font=('Helvetica', 10, 'bold'))
        self.chakra_cost_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Técnicas
        self.technique_notebook = ttk.Notebook(right_frame)
        self.technique_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Resultados
        result_frame = ttk.LabelFrame(right_frame, text="Damage Results")
        result_frame.pack(fill="x", padx=5, pady=5)
        
        self.melee_damage_label = ttk.Label(result_frame, text="Melee Damage: -")
        self.melee_damage_label.pack(anchor="w", padx=5, pady=2)
        
        self.technique_damage_label = ttk.Label(result_frame, text="Technique Damage: -")
        self.technique_damage_label.pack(anchor="w", padx=5, pady=2)
        
        # Tabela de técnicas com dano
        self.technique_table = ttk.Treeview(right_frame, columns=('Technique', 'Element', 'Damage', 'DPS', 'Chakra', 'Cooldown'), show='headings')
        self.technique_table.heading('Technique', text='Technique', command=lambda: self.sort_table('Technique', False))
        self.technique_table.heading('Element', text='Element')
        self.technique_table.heading('Damage', text='Damage', command=lambda: self.sort_table('Damage', True))
        self.technique_table.heading('DPS', text='DPS', command=lambda: self.sort_table('DPS', True))
        self.technique_table.heading('Chakra', text='Chakra Cost')
        self.technique_table.heading('Cooldown', text='Cooldown (s)')
        self.technique_table.column('Technique', width=200)
        self.technique_table.column('Element', width=80)
        self.technique_table.column('Damage', width=80)
        self.technique_table.column('DPS', width=80)
        self.technique_table.column('Chakra', width=80)
        self.technique_table.column('Cooldown', width=80)
        self.technique_table.pack(fill="x", padx=5, pady=5)
        
        # Botão para editar técnica
        ttk.Button(right_frame, text="Edit Selected Technique", command=self.edit_technique).pack(pady=5)
    
    def change_attribute(self, attr, change):
        """Altera o valor de um atributo usando os botões +/-"""
        current = self.attr_vars[attr].get()
        new_val = max(0, current + change)
        self.attr_vars[attr].set(new_val)
    
    def update_charm_selection(self, event):
        """Atualiza a seleção de charm quando o usuário seleciona um"""
        selected = self.charm_var.get()
        # Extrai o nome do charm (removendo a descrição entre parênteses)
        charm_name = selected.split(' (')[0]
        self.charm_var.set(charm_name)
        self.update_attributes()
    
    def update_guild_level(self, *args):
        """Atualiza o nível do Status Level Guild"""
        self.guild_level = self.guild_level_var.get()
        self.update_attributes()
    
    def update_points_spent(self, *args):
        """Calcula o total de pontos gastos e atualiza o nível"""
        total = sum(var.get() for var in self.attr_vars.values())
        self.total_points_spent = total
        self.spent_label.config(text=str(total))
        
        # Calcular nível baseado nos pontos gastos
        level = 1
        points_needed = 0
        
        while level <= self.max_level:
            if level <= 50:
                points_per_level = self.points_per_level_1_50
            else:
                points_per_level = self.points_per_level_50_60
            
            points_needed += points_per_level
            
            if total >= points_needed:
                level += 1
            else:
                break
        
        self.level = min(level, self.max_level)
        self.level_label.config(text=str(self.level))
        self.update_points_display()
        self.update_attributes()
    
    def update_points_display(self):
        """Atualiza a exibição de pontos disponíveis"""
        points_available = self.calculate_total_points() - self.total_points_spent
        self.points_label.config(text=str(points_available))
    
    def calculate_total_points(self):
        """Calcula o total de pontos ganhos até o nível atual"""
        total = 0
        for level in range(1, self.level + 1):
            if level <= 50:
                total += self.points_per_level_1_50
            else:
                total += self.points_per_level_50_60
        return min(total, self.max_points)
    
    def update_attributes(self, *args):
        """Atualiza os atributos com bônus de charm e guild level"""
        charm = self.charm_var.get()
        
        # Resetar atributos para valores base
        for attr in self.base_attributes:
            base_value = self.attr_vars[attr].get()
            
            # Aplicar bônus do Status Level Guild (1% por nível)
            guild_bonus = base_value * (self.guild_level * 0.01)
            self.base_attributes[attr] = base_value + int(guild_bonus)
            
            # Aplicar bônus de charm
            if charm in self.charm_bonuses:
                bonuses = self.charm_bonuses[charm]
                if attr in bonuses:
                    bonus = bonuses[attr]
                    if isinstance(bonus, float):
                        # Bônus percentual (como Libra 5% Intellect)
                        self.base_attributes[attr] = int(self.base_attributes[attr] * (1 + bonus))
                    else:
                        # Bônus fixo
                        self.base_attributes[attr] += bonus
            
            # Atualizar display
            self.attr_entries[attr].config(text=str(self.base_attributes[attr]))
        
        # Atualizar danos
        self.update_melee_damage()
        self.update_technique_table()
    
    def update_element_techniques(self, *args):
        """Atualiza as abas de técnicas baseado nos elementos selecionados"""
        primary = self.primary_element_var.get()
        secondary = self.secondary_element_var.get()
        
        # Remover todas as abas existentes
        for tab in self.technique_notebook.tabs():
            self.technique_notebook.forget(tab)
        
        # Adicionar abas para elementos selecionados
        if primary:
            self.add_technique_tab(primary)
        if secondary and secondary != primary:
            self.add_technique_tab(secondary)
        
        # Sempre mostrar aba de Weapon
        if "Weapon" not in [primary, secondary]:
            self.add_technique_tab("Weapon")
        
        self.update_technique_table()
    
    def add_technique_tab(self, element):
        """Adiciona uma aba para um elemento específico"""
        tab = ttk.Frame(self.technique_notebook)
        
        # Configurar cor da aba baseada no elemento
        tab_style = f"{element}.Tab"
        self.style.configure(tab_style, 
                           background=self.elements[element]["bg"], 
                           foreground=self.elements[element]["color"])
        
        self.technique_notebook.add(tab, text=element)
        
        # Lista de técnicas em Treeview (estilo tabela)
        columns = ('Technique', 'Base Damage', 'Scaling', 'Chakra Cost', 'Cooldown')
        tech_tree = ttk.Treeview(tab, columns=columns, show='headings')
        
        # Configurar cabeçalhos
        tech_tree.heading('Technique', text='Technique')
        tech_tree.heading('Base Damage', text='Base Damage')
        tech_tree.heading('Scaling', text='Scaling')
        tech_tree.heading('Chakra Cost', text='Chakra Cost')
        tech_tree.heading('Cooldown', text='Cooldown (s)')
        
        # Configurar largura das colunas
        tech_tree.column('Technique', width=200)
        tech_tree.column('Base Damage', width=80)
        tech_tree.column('Scaling', width=80)
        tech_tree.column('Chakra Cost', width=80)
        tech_tree.column('Cooldown', width=80)
        
        # Adicionar técnicas
        for tech, data in self.techniques.get(element, {}).items():
            tech_tree.insert('', 'end', values=(
                tech,
                data['base_damage'],
                data['scaling'],
                data['chakra_cost'],
                data['cooldown']
            ))
        
        tech_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Botão para calcular dano
        ttk.Button(tab, text="Calculate Damage", 
                  command=lambda: self.calculate_selected_technique(element, tech_tree)).pack(pady=5)
    
    def calculate_selected_technique(self, element, tech_tree):
        """Calcula o dano da técnica selecionada na Treeview"""
        selected = tech_tree.focus()
        if not selected:
            return
        
        item = tech_tree.item(selected)
        technique = item['values'][0]
        self.calculate_technique_damage(element, technique)
    
    def sort_table(self, column, numeric):
        """Ordena a tabela pela coluna especificada"""
        data = [(self.technique_table.set(child, column), child) 
               for child in self.technique_table.get_children('')]
        
        # Ordenar numericamente ou alfabeticamente
        if numeric:
            # Para valores numéricos (Damage, DPS)
            data.sort(key=lambda t: float(t[0]) if t[0] else 0, reverse=True)
        else:
            # Para texto (Technique, Element)
            data.sort()
        
        # Reorganizar itens na tabela
        for index, (val, child) in enumerate(data):
            self.technique_table.move(child, '', index)
    
    def update_melee_damage(self):
        """Atualiza o cálculo do dano melee baseado nos atributos"""
        weapon_damages = []
        
        # Calcular dano para cada arma
        for weapon, data in self.techniques["Weapon"].items():
            base = data["base_damage"]
            scaling_attr = data["scaling"]
            scaling_value = self.base_attributes.get(scaling_attr, 0)
            
            # Fórmula: base + (atributo * 0.6)
            damage = base + (scaling_value * 0.6)
            weapon_damages.append(f"{weapon}: {damage:.1f}")
        
        self.melee_damage_label.config(text="Melee Damage: " + " | ".join(weapon_damages))
    
    def update_technique_table(self):
        """Atualiza a tabela de técnicas com dano calculado"""
        self.technique_table.delete(*self.technique_table.get_children())
        self.dps_data = {}
        total_damage = 0
        total_time = 0
        self.total_chakra_cost = 0
        
        # Verificar quais elementos estão ativos
        active_elements = []
        if self.primary_element_var.get():
            active_elements.append(self.primary_element_var.get())
        if self.secondary_element_var.get() and self.secondary_element_var.get() != self.primary_element_var.get():
            active_elements.append(self.secondary_element_var.get())
        if "Weapon" not in active_elements:
            active_elements.append("Weapon")
        
        # Calcular dano para todas as técnicas ativas
        for element in active_elements:
            element_color = self.elements[element]["color"]
            for tech, data in self.techniques.get(element, {}).items():
                base_damage = data.get("base_damage", 0)
                scaling_attr = data.get("scaling", "Intellect")
                scaling_value = self.base_attributes.get(scaling_attr, 0)
                chakra_cost = data.get("chakra_cost", 0)
                cooldown = data.get("cooldown", 0)
                
                # Fórmula de dano: base + (atributo * 0.6)
                damage = base_damage + (scaling_value * 0.6)
                
                # Calcular DPS (Damage Per Second)
                dps = damage / cooldown if cooldown > 0 else 0
                
                # Adicionar à tabela com cor do elemento
                item_id = self.technique_table.insert('', 'end', values=(
                    tech,
                    element,
                    f"{damage:.1f}",
                    f"{dps:.1f}",
                    chakra_cost,
                    cooldown
                ))
                
                # Aplicar cor ao elemento e dano
                self.technique_table.tag_configure(element, foreground=element_color)
                self.technique_table.item(item_id, tags=(element,))
                
                # Acumular custo total de chakra
                self.total_chakra_cost += chakra_cost
                
                # Armazenar para cálculo de DPS total
                if cooldown > 0:  # Ignora armas que não têm cooldown
                    self.dps_data[tech] = {
                        "damage": damage,
                        "cooldown": cooldown
                    }
                    total_damage += damage
                    total_time += cooldown
        
        # Atualizar labels de DPS e custo de chakra
        if total_time > 0:
            rotation_dps = total_damage / total_time
            self.dps_label.config(text=f"{rotation_dps:.1f}")
        self.chakra_cost_label.config(text=f"{self.total_chakra_cost}")
    
    def calculate_technique_damage(self, element, technique):
        """Calcula o dano de uma técnica específica"""
        if not technique:
            self.technique_damage_label.config(text="Select a technique")
            return
        
        tech_data = self.techniques[element].get(technique)
        if not tech_data:
            self.technique_damage_label.config(text="Technique not found")
            return
        
        base_damage = tech_data.get("base_damage", 0)
        scaling_attr = tech_data.get("scaling", "Intellect")
        scaling_value = self.base_attributes.get(scaling_attr, 0)
        chakra_cost = tech_data.get("chakra_cost", 0)
        cooldown = tech_data.get("cooldown", 0)
        
        # Fórmula de dano: base + (atributo * 0.6)
        damage = base_damage + (scaling_value * 0.6)
        
        # Calcular DPS
        dps = damage / cooldown if cooldown > 0 else 0
        
        self.technique_damage_label.config(text=f"Technique Damage: {damage:.1f}")
        
        # Atualizar a tabela para destacar a técnica selecionada
        self.update_technique_table()
        for item in self.technique_table.get_children():
            if self.technique_table.item(item)['values'][0] == technique:
                self.technique_table.selection_set(item)
                self.technique_table.focus(item)
                self.technique_table.see(item)
                break
    
    def edit_technique(self):
        """Abre uma janela para editar os parâmetros da técnica selecionada"""
        selected = self.technique_table.focus()
        if not selected:
            return
        
        item = self.technique_table.item(selected)
        technique_name = item['values'][0]
        element = item['values'][1]
        
        # Encontrar a técnica nos dados
        tech_data = self.techniques[element].get(technique_name)
        if not tech_data:
            return
        
        # Criar janela de edição
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit {technique_name}")
        edit_window.geometry("300x250")
        
        ttk.Label(edit_window, text="Base Damage:").grid(row=0, column=0, padx=5, pady=5)
        base_damage_var = tk.IntVar(value=tech_data['base_damage'])
        ttk.Entry(edit_window, textvariable=base_damage_var).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(edit_window, text="Chakra Cost:").grid(row=1, column=0, padx=5, pady=5)
        chakra_cost_var = tk.IntVar(value=tech_data['chakra_cost'])
        ttk.Entry(edit_window, textvariable=chakra_cost_var).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(edit_window, text="Cooldown (s):").grid(row=2, column=0, padx=5, pady=5)
        cooldown_var = tk.IntVar(value=tech_data['cooldown'])
        ttk.Entry(edit_window, textvariable=cooldown_var).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(edit_window, text="Scaling Attribute:").grid(row=3, column=0, padx=5, pady=5)
        scaling_var = tk.StringVar(value=tech_data['scaling'])
        scaling_menu = ttk.OptionMenu(edit_window, scaling_var, tech_data['scaling'], 
                                     "Strength", "Fortitude", "Intellect", "Agility", "Chakra")
        scaling_menu.grid(row=3, column=1, padx=5, pady=5)
        
        def save_changes():
            tech_data['base_damage'] = base_damage_var.get()
            tech_data['chakra_cost'] = chakra_cost_var.get()
            tech_data['cooldown'] = cooldown_var.get()
            tech_data['scaling'] = scaling_var.get()
            self.update_technique_table()
            self.calculate_technique_damage(element, technique_name)
            edit_window.destroy()
        
        ttk.Button(edit_window, text="Save", command=save_changes).grid(row=4, column=0, columnspan=2, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = MetaninRenewalApp(root)
    root.mainloop()