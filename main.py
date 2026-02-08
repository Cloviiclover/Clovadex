import customtkinter as ctk, pandas as pd, matplotlib.pyplot as plt, os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image

#CSV file, sprites folder, and stat columns in CSV file
dex_data = "data.csv"
sprites = "sprites"
stat_col = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]


#CSV reading class
class PokemonData:
    def __init__(self, dex_data):
        self.df = pd.read_csv(dex_data)

    def mon_names(self):
        return self.df["Name"].tolist()

    def mon_to_details(self, name): #Allows for other stats through mon name
        return self.df[self.df["Name"] == name].iloc[0]

    def first_type(self):
        return self.df["Type 1"].value_counts()

    def search_filter(self, search_text="", filters=None):
        df = self.df.copy()

        if filters is None:
            filters = {}

        if search_text:
            search_text = search_text.lower()
            df = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(search_text).any(),axis=1)]

        if filters.get("Legendary"):
            df = df[df["Legendary"].astype(str).str.lower() == "true"]

        if filters.get("Type"):
            df = df[
                (df["Type 1"] == filters["Type"]) |
                (df["Type 2"] == filters["Type"])
            ]

        return df

#Sprite loading
class SpriteLoader:
    def __init__(self, sprites):
        self.sprites = sprites

    def load(self, number, name):
        dex = str(number)
        current_dex_num = []

        if "Mega " in name or "Primal " in name or "Unbound" in name or "Attack Forme" in name or "Defense Forme" in name or "Speed Forme" in name or "Plant Cloak" in name or "Sandy Cloak" in name or "Trash Cloak" in name or "Heat Rotom" in name or "Wash Rotom" in name or "Frost Rotom" in name or "Fan Rotom" in name or "Mow Rotom" in name:
            dex = dex.zfill(5)
        else:
            dex = dex.zfill(4)

        current_dex_num.append(f"{dex}.png")

        for file in current_dex_num:
            path = os.path.join(self.sprites, file)
            if os.path.exists(path):
                img = Image.open(path).resize((160, 160))
                return ctk.CTkImage(light_image=img,dark_image=img,size=(160, 160))
        return None

#Main home page with pie chart
class home(ctk.CTkFrame):
    def __init__(self, master, data: PokemonData):
        super().__init__(master)
        self.data = data
        self.build()

    def build(self):
        title = ctk.CTkLabel(self,text="Welcome to Clovadex!\nFirst Type Pie Chart",font=("Arial", 22))
        title.pack(pady=10)

        type_counts = self.data.first_type()

        fig, ax = plt.subplots(figsize=(5, 5))
        fig.patch.set_alpha(0)
        ax.set_facecolor("none")

        ax.pie(type_counts.values,labels=type_counts.index,autopct="%1.1f%%",startangle=90,textprops={"color": "white"})
        ax.axis("equal")

        canvas = FigureCanvasTkAgg(fig, master=self)
        widget = canvas.get_tk_widget()

        bg_color = self._apply_appearance_mode(self.cget("fg_color"))
        widget.configure(bg=bg_color)

        widget.pack(fill="both", expand=True)
        canvas.draw()

#Pokemon preview page (with stats bar chart)
class preview(ctk.CTkFrame):
    def __init__(self, master, data: PokemonData, sprite_loader: SpriteLoader):
        super().__init__(master)
        self.data = data
        self.sprite_loader = sprite_loader
        self.current_sprite_image = None
        self.build()

    def build(self):
        self.title_label = ctk.CTkLabel(self,text="Select a Pokémon",font=("Arial", 22))
        self.title_label.pack(pady=(10, 5))

        self.sprite_label = ctk.CTkLabel(self, text="")
        self.sprite_label.pack(pady=5)

        img = Image.open("images/clickbro.png") #placeholder image (because it felt too empty)
        self.placeholder_image = ctk.CTkImage(light_image=img,dark_image=img,size=(300, 300))

        self.placeholder_label = ctk.CTkLabel(self,image=self.placeholder_image,text="")
        self.placeholder_label.pack(pady=10)

        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.fig.patch.set_alpha(0)
        
        self.ax.set_facecolor("none")
        self.ax.axis("off")
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        widget = self.canvas.get_tk_widget()

        bg_color = self._apply_appearance_mode(self.cget("fg_color"))
        widget.configure(bg=bg_color)
        widget.pack(fill="both", expand=True)

    def show_pokemon(self, name):
        self.placeholder_label.pack_forget()
        self.ax.clear()
        self.ax.axis("on")

        row = self.data.mon_to_details(name)
        stats = [row[col] for col in stat_col]

        self.ax.bar(stat_col, stats)
        self.ax.set_title(name, color="white")
        self.ax.set_ylabel("Base Stats", color="white")
        self.ax.set_ylim(0, max(stats) + 20)

        self.ax.set_facecolor("none")
        self.ax.tick_params(axis="x", colors="white")
        self.ax.tick_params(axis="y", colors="white")

        self.canvas.draw()
        self.title_label.configure(text=name)

        sprite = self.sprite_loader.load(row["Number"], name)
        self.current_sprite_image = sprite
        self.sprite_label.configure(image=self.current_sprite_image, text="")

#Main app (pokedex program)
class ClovadexApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.active_filters = {}
        self.filter_window = None

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.geometry("1100x650")
        self.title("Clovadex")
        self.iconbitmap("images/icondex.ico")

        self.data = PokemonData(dex_data)
        self.sprite_loader = SpriteLoader(sprites)

        self.view_mode = ctk.StringVar(value="home")

        self.layouts()
        self.sidebar()
        self.menus()

        self.update_pokemon_list()

    def layouts(self):
        self.left_frame = ctk.CTkFrame(self, width=300)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def sidebar(self):
        self.switch_button = ctk.CTkButton(self.left_frame,text="Pokémon Preview",command=self.menu_switch)
        self.switch_button.pack(fill="x", padx=10, pady=(10, 5))

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self.left_frame,textvariable=self.search_var)
        self.search_entry.pack(fill="x", padx=10, pady=5)
        self.search_entry.bind("<KeyRelease>",lambda e: self.update_pokemon_list(self.search_var.get()))

        self.scroll_frame = ctk.CTkScrollableFrame(self.left_frame)
        self.scroll_frame.pack(fill="both", expand=True)

        self.filter_button = ctk.CTkButton(
            self.left_frame,
            text="Filters",
            command=self.filter
        )
        self.filter_button.pack(fill="x", padx=10, pady=5)

    def menus(self):
        self.menu_home = home(self.right_frame, self.data)
        self.menu_preview = preview(self.right_frame, self.data, self.sprite_loader)

        self.menu_home.pack(fill="both", expand=True)

    def menu_switch(self):
        if self.view_mode.get() == "home":
            self.view_mode.set("preview")
            self.menu_home.pack_forget()
            self.menu_preview.pack(fill="both", expand=True)
            self.switch_button.configure(text="Home Page")
        else:
            self.view_mode.set("home")
            self.menu_preview.pack_forget()
            self.menu_home.pack(fill="both", expand=True)
            self.switch_button.configure(text="Pokémon Preview")

    def update_pokemon_list(self, filter_text=""):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        filtered_df = self.data.search_filter(search_text=filter_text, filters=self.active_filters)

        for _, row in filtered_df.iterrows():
            name = row["Name"]
            poke_button = ctk.CTkButton(self.scroll_frame, text=name, command=lambda n=name: self.menu_preview.show_pokemon(n))
            poke_button.pack(fill="x", padx=5, pady=3)


    def filter(self):
        filter_window = ctk.CTkToplevel(self)
        filter_window.title("Filters")
        filter_window.geometry("300x400")

        #Legendary filter
        legendary_var = ctk.BooleanVar(value=self.active_filters.get("Legendary", False))

        legendary_checkbox = ctk.CTkCheckBox(filter_window, text="Legendary Only", variable=legendary_var)
        legendary_checkbox.pack(pady=10)

        #Type filter
        type_label = ctk.CTkLabel(filter_window, text="Type Filter")
        type_label.pack(pady=(20, 5))

        types = sorted(self.data.df["Type 1"].dropna().unique())

        type_var = ctk.StringVar(value=self.active_filters.get("Type", "None"))

        type_dropdown = ctk.CTkOptionMenu(filter_window, values=["None"] + types, variable=type_var)
        type_dropdown.pack(pady=5)

        def apply_filters():
            self.active_filters.clear()

            if legendary_var.get():
                self.active_filters["Legendary"] = True

            if type_var.get() != "None":
                self.active_filters["Type"] = type_var.get()

            self.update_pokemon_list(self.search_var.get())
            filter_window.destroy()

        apply_button = ctk.CTkButton(filter_window, text="Apply Filters", command=apply_filters)
        apply_button.pack(pady=20)

#Fully running the app (the actual pokedex program)
if __name__ == "__main__":
    app = ClovadexApp()
    app.mainloop()
