import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from data_operations import sort_data, filter_data, show_stats, reset_all, reset_filters, reset_sort
from data_manager import load_csv, load_json, load_xml, load_yaml, save_csv, save_json, save_xml, save_yaml

class DataManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Filter Project")
        self.data = []

        self.background_images = ["welcome.gif", "welcome2.gif"]
        self.current_bg_index = 0 

        self.create_welcome_screen()

    def create_welcome_screen(self):
        """Création de l'écran d'accueil avec un fond GIF et un bouton"""
        self.bg_image = Image.open(self.background_images[self.current_bg_index]) 
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.root.geometry(f"{self.bg_image.width}x{self.bg_image.height}")
        self.root.update_idletasks()

        self.welcome_frame = tk.Frame(self.root)
        self.welcome_frame.pack(fill=tk.BOTH, expand=True)

        bg_label = tk.Label(self.welcome_frame, image=self.bg_photo)
        bg_label.place(relwidth=1, relheight=1)  

        welcome_label = tk.Label(self.welcome_frame, text="Bienvenue sur le Projet Data Filter", font=("Arial", 18, "bold"), fg="white", bg="black")
        welcome_label.pack(pady=20)

        start_button = tk.Button(self.welcome_frame, text="Commencer", font=("Arial", 14), command=self.start_main_app)
        start_button.pack(pady=10)

        change_bg_button = tk.Button(self.welcome_frame, text="Changer de fond", font=("Arial", 12), command=self.change_background)
        change_bg_button.pack(pady=10)

    def change_background(self):
        """Change l'image de fond pour simuler un carrousel"""
        self.current_bg_index = (self.current_bg_index + 1) % len(self.background_images)

        self.bg_image = Image.open(self.background_images[self.current_bg_index])
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.root.geometry(f"{self.bg_image.width}x{self.bg_image.height}")
        self.root.update_idletasks()

        self.welcome_frame.destroy()
        self.create_welcome_screen()

    def start_main_app(self):
        """Cache l'écran d'accueil et lance la page principale"""
        self.welcome_frame.destroy()  
        self.create_main_app()

    def create_main_app(self):
        """Création de l'interface principale de l'application"""
        self.root.geometry("800x600")
        self.root.update_idletasks()

        title_label = tk.Label(self.root, text="Data Filter Project", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.load_save_button = tk.Button(button_frame, text="Charger les Données", command=self.load_or_save_data)
        self.load_save_button.grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="Afficher Stats", command=lambda: show_stats(self.data)).grid(row=0, column=1, padx=10)
        tk.Button(button_frame, text="Filtrer Données", command=lambda: filter_data(self)).grid(row=0, column=2, padx=10)
        tk.Button(button_frame, text="Trier Données", command=lambda: sort_data(self)).grid(row=0, column=3, padx=10)

        tk.Button(button_frame, text="Annuler Tout", command=lambda: reset_all(self)).grid(row=1, column=0, padx=10, pady=10)
        tk.Button(button_frame, text="Annuler le Tri", command=lambda: reset_sort(self)).grid(row=1, column=1, padx=10, pady=10)
        tk.Button(button_frame, text="Annuler les Filtres", command=lambda: reset_filters(self)).grid(row=1, column=2, padx=10, pady=10)

        self.tree = ttk.Treeview(self.root)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)


    def show_data(self):
        """Affiche les données dans l'interface"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        if not self.data:
            messagebox.showinfo("Info", "Aucune donnée à afficher.")
            return

        for item in self.data:
            if isinstance(item, dict):
                row = tuple(item.values())
            else:
                row = tuple(item)
            self.tree.insert("", tk.END, values=row)

    def load_data(self):
        file_path = filedialog.askopenfilename(title="Sélectionnez un fichier", filetypes=[("Fichiers CSV", "*.csv"), ("Fichiers JSON", "*.json"), ("Fichiers XML", "*.xml"), ("Fichiers YAML", "*.yaml")])
        if not file_path:
            return
        file_type = file_path.split('.')[-1].lower()
        if file_type == "csv":
            self.data = load_csv(file_path)
        elif file_type == "json":
            self.data = load_json(file_path)
        elif file_type == "xml":
            self.data = load_xml(file_path)
        elif file_type == "yaml":
            self.data = load_yaml(file_path)
        else:
            messagebox.showerror("Erreur", "Format non supporté.")
            return

        self.show_data()
        self.load_save_button.config(text="Sauvegarder les Données")

    def show_data(self):
        if not self.data:
            return
        self.tree.delete(*self.tree.get_children())
        columns = list(self.data[0].keys())
        self.tree["columns"] = columns
        self.tree["show"] = "headings"
        for col in columns:
            self.tree.heading(col, text=col)
        for row in self.data:
            values = [row.get(col, "") for col in columns]
            self.tree.insert("", "end", values=values)

    def save_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[
            ("Fichiers CSV", "*.csv"), ("Fichiers JSON", "*.json"),
            ("Fichiers XML", "*.xml"), ("Fichiers YAML", "*.yaml")])
        
        if not file_path:
            return

        file_type = file_path.split('.')[-1].lower()
        try:
            if file_type == "csv":
                save_csv(file_path, self.data)
            elif file_type == "json":
                save_json(file_path, self.data)
            elif file_type == "xml":
                save_xml(file_path, self.data)
            elif file_type == "yaml":
                save_yaml(file_path, self.data)
            else:
                messagebox.showerror("Erreur", "Format non supporté.")
                return

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {str(e)}")
    def load_or_save_data(self):
        if not self.data:
            self.load_data()
        else:
            self.save_data()
