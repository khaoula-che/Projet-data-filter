import csv
import json
import numpy as np
import xml.etree.ElementTree as ET
import yaml
import tkinter as tk
import statistics
from tkinter import filedialog, ttk, messagebox
from tkinter import simpledialog
from PIL import Image, ImageTk


class DataManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Filter Project")
        self.data = []

        self.background_images = [
            "welcome.gif",  
            "welcome2.gif"
        ]
        self.current_bg_index = 0 

        self.create_welcome_screen()

    def create_welcome_screen(self):
        """Création de l'écran d'accueil avec un fond GIF et un bouton"""
        self.bg_image = Image.open(self.background_images[self.current_bg_index]) 
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.root.geometry(f"{self.bg_image.width}x{self.bg_image.height}")

        self.welcome_frame = tk.Frame(self.root)
        self.welcome_frame.pack(fill=tk.BOTH, expand=True)

        bg_label = tk.Label(self.welcome_frame, image=self.bg_photo)
        bg_label.place(relwidth=1, relheight=1)  

        welcome_label = tk.Label(self.welcome_frame, text="Bienvenue sur le Projet Data Filter", font=("Arial", 18, "bold"), fg="white")
        welcome_label.pack(pady=20)

        start_button = tk.Button(self.welcome_frame, text="Commencer", font=("Arial", 14), command=self.start_main_app)
        start_button.pack(pady=10)

        change_bg_button = tk.Button(self.welcome_frame, text="Changer de fond", font=("Arial", 12), command=self.change_background)
        change_bg_button.pack(pady=10)

    def start_main_app(self):
        """Cache l'écran d'accueil et lance la page principale"""
        self.welcome_frame.destroy()  
        self.create_main_app()  

    def change_background(self):
        """Change l'image de fond pour simuler un carrousel"""
        self.current_bg_index = (self.current_bg_index + 1) % len(self.background_images)

        self.bg_image = Image.open(self.background_images[self.current_bg_index])
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.root.geometry(f"{self.bg_image.width}x{self.bg_image.height}")

        self.welcome_frame.destroy()
        self.create_welcome_screen()

    def create_main_app(self):
            """Création de l'interface principale de l'application"""
            title_label = tk.Label(self.root, text="Data Filter Project", font=("Arial", 18, "bold"))
            title_label.pack(pady=10)

            button_frame = tk.Frame(self.root)
            button_frame.pack(pady=10)

            self.load_save_button = tk.Button(button_frame, text="Charger les Données", command=self.load_or_save_data)
            self.load_save_button.grid(row=0, column=0, padx=10)

            tk.Button(button_frame, text="Afficher Statistiques", command=self.show_stats).grid(row=0, column=1, padx=10)
            tk.Button(button_frame, text="Filtrer les Données", command=self.filter_data).grid(row=0, column=2, padx=10)
            tk.Button(button_frame, text="Trier les Données", command=self.sort_data).grid(row=0, column=3, padx=10)

            tk.Button(button_frame, text="Annuler Tout", command=self.reset_all).grid(row=1, column=0, padx=10, pady=10)
            tk.Button(button_frame, text="Annuler le Tri", command=self.reset_sort).grid(row=1, column=1, padx=10, pady=10)
            tk.Button(button_frame, text="Annuler les Filtres", command=lambda: self.show_data()).grid(row=1, column=2, padx=10, pady=10)

            self.tree = ttk.Treeview(self.root)
            self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

    def reset_all(self):
            """Réinitialiser toutes les données, tris et filtres"""
            self.data = self.original_data.copy()  
            self.show_data()  
            messagebox.showinfo("Réinitialisation", "Toutes les actions ont été annulées.")

    def reset_sort(self):
        """Annule uniquement les tris effectués et restaure les données d'origine"""
        if hasattr(self, 'original_data'):
            self.data = self.original_data.copy()  
            self.show_data() 
            messagebox.showinfo("Réinitialisation du tri", "Le tri a été annulé.")
        else:
            messagebox.showwarning("Avertissement", "Aucun tri à annuler.")


    def reset_filters(self):
            """Annuler uniquement les filtres appliqués"""
            self.show_data()  
            messagebox.showinfo("Réinitialisation des filtres", "Les filtres ont été annulés.")

    def load_or_save_data(self):
        """Vérifie si des données sont déjà chargées et lance la bonne action"""
        if not self.data:
            self.load_data()
        else:
            self.save_data()

    def load_data(self):
        file_path = filedialog.askopenfilename(title="Sélectionnez un fichier",
                                                filetypes=[("Fichiers CSV", "*.csv"),
                                                           ("Fichiers JSON", "*.json"),
                                                           ("Fichiers XML", "*.xml"),
                                                           ("Fichiers YAML", "*.yaml")])
        if not file_path:
            return

        file_type = file_path.split('.')[-1].lower()
        if file_type == "csv":
            self.data = self.load_csv(file_path)
        elif file_type == "json":
            self.data = self.load_json(file_path)
        elif file_type == "xml":
            self.data = self.load_xml(file_path)
        elif file_type == "yaml":
            self.data = self.load_yaml(file_path)
        else:
            messagebox.showerror("Erreur", "Format non supporté.")
            return

        self.show_data()
        self.load_save_button.config(text="Sauvegarder les Données")

    def save_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                  filetypes=[("Fichiers CSV", "*.csv"),
                                                           ("Fichiers JSON", "*.json"),
                                                           ("Fichiers XML", "*.xml"),
                                                           ("Fichiers YAML", "*.yaml")])
        if not file_path:
            return

        file_type = file_path.split('.')[-1].lower()
        try:
            if file_type == "csv":
                self.save_csv(file_path)
            elif file_type == "json":
                self.save_json(file_path)
            elif file_type == "xml":
                self.save_xml(file_path)
            elif file_type == "yaml":
                self.save_yaml(file_path)
            else:
                messagebox.showerror("Erreur", "Format non supporté.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {str(e)}")

        self.load_save_button.config(text="Charger les Données")

    def load_csv(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return [self._convert_data(row) for row in reader]

    def save_csv(self, file):
        with open(file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
            writer.writeheader()
            writer.writerows(self.data)

    def load_json(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_json(self, file):
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)

    def load_xml(self, file):
        tree = ET.parse(file)
        root = tree.getroot()
        return [{child.tag: child.text for child in item} for item in root]

    def save_xml(self, file):
        root = ET.Element("Data")
        for row in self.data:
            item = ET.SubElement(root, "Item")
            for key, value in row.items():
                child = ET.SubElement(item, key)
                child.text = str(value)
        tree = ET.ElementTree(root)
        tree.write(file)

    def load_yaml(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def save_yaml(self, file):
        with open(file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(self.data, f)

    def _convert_data(self, row):
        """Convertit les types de données pour correspondre aux types natifs."""
        for key, value in row.items():
            if value.isdigit():
                row[key] = int(value)
            elif value.replace('.', '', 1).isdigit():
                row[key] = float(value)
            elif value.lower() == 'true':
                row[key] = True
            elif value.lower() == 'false':
                row[key] = False
            elif value.startswith("[") and value.endswith("]"):
                row[key] = eval(value) 
        return row

    def show_data(self, display_data=None):
        data_to_show = display_data if display_data else self.data
        if not data_to_show:
            return

        self.tree.delete(*self.tree.get_children())

        columns = list(data_to_show[0].keys())
        self.tree["columns"] = columns
        self.tree["show"] = "headings"

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.W, width=120)

        for row in data_to_show:
            values = [row.get(col, "") for col in columns]
            self.tree.insert("", "end", values=values)



    def show_stats(self):
        if not self.data:
            messagebox.showinfo("Info", "Aucune donnée chargée.")
            return

        stats_result = {}
        for key in self.data[0].keys():
            values = [item[key] for item in self.data if key in item]
            numeric_values = [float(v) for v in values if isinstance(v, (int, float))]
            bool_values = [v for v in values if isinstance(v, bool)]
            list_sizes = [len(v) for v in values if isinstance(v, list)]

            if numeric_values:
                stats_result[key] = f"Min: {min(numeric_values)}, Max: {max(numeric_values)}, Moyenne: {sum(numeric_values) / len(numeric_values):.2f}"
            elif bool_values:
                true_count = sum(bool_values)
                false_count = len(bool_values) - true_count
                stats_result[key] = f"True: {true_count / len(bool_values) * 100:.2f}%, False: {false_count / len(bool_values) * 100:.2f}%"
            elif list_sizes:
                stats_result[key] = f"Min: {min(list_sizes)}, Max: {max(list_sizes)}, Moyenne: {sum(list_sizes) / len(list_sizes):.2f}"

        result_text = "\n".join([f"{key}: {value}" for key, value in stats_result.items()])
        messagebox.showinfo("Statistiques", result_text)

    def filter_data(self):
        if not self.data:
            messagebox.showinfo("Info", "Aucune donnée chargée.")
            return

        filter_window = tk.Toplevel(self.root)
        filter_window.title("Filtrer les Données")

        tk.Label(filter_window, text="Sélectionnez la clé, la valeur et l'opérateur pour filtrer :", font=("Arial", 12)).pack(pady=10)

        columns = list(self.data[0].keys())
        key_var = tk.StringVar(value=columns[0])  
        tk.Label(filter_window, text="Sélectionnez la clé :").pack(pady=5)
        key_menu = ttk.Combobox(filter_window, textvariable=key_var, values=columns)
        key_menu.pack(pady=5)

        tk.Label(filter_window, text="Entrez la valeur :").pack(pady=5)
        value_entry = tk.Entry(filter_window)
        value_entry.pack(pady=5)

        operator_var = tk.StringVar(value="==")
        operators = ["==", "!=", "<", ">", "<=", ">=", "startswith", "endswith", "contains", "above_mean", "below_percentile"]
        tk.Label(filter_window, text="Sélectionnez l'opérateur :").pack(pady=5)
        operator_menu = ttk.Combobox(filter_window, textvariable=operator_var, values=operators)
        operator_menu.pack(pady=5)

        def apply_filter():
            key = key_var.get()
            value = value_entry.get()
            operator = operator_var.get()

            try:
                if isinstance(self.data[0].get(key), (int, float)):
                    value = float(value) if '.' in value else int(value)
            except ValueError:
                pass 

            filtered_data = self.filter_data_logic(self.data, key, value, operator)
            
            self.show_data(filtered_data)
            filter_window.destroy()  

        tk.Button(filter_window, text="Appliquer le filtre", command=apply_filter).pack(pady=10)
        tk.Button(filter_window, text="Annuler", command=filter_window.destroy).pack(pady=5)

        filter_window.mainloop()

    def filter_data_logic(self, data, key, value, operator):
        data_filtered = []

        numeric_values = [item[key] for item in data if key in item and isinstance(item[key], (int, float))]
        global_mean = statistics.mean(numeric_values) if numeric_values else 0
        global_percentile_75 = np.percentile(numeric_values, 75) if numeric_values else 0

        for item in data:
            if key in item:
                item_value = item[key]

                if isinstance(item_value, str) and isinstance(value, str):
                    if operator == "==" and item_value == value or \
                            operator == "!=" and item_value != value or \
                            operator == "startswith" and item_value.startswith(value) or \
                            operator == "endswith" and item_value.endswith(value) or \
                            operator == "contains" and value.lower() in item_value.lower():
                        data_filtered.append(item)

                elif isinstance(item_value, (int, float)) and isinstance(value, (int, float)):
                    if operator == "==" and item_value == value or \
                            operator == "!=" and item_value != value or \
                            operator == "<" and item_value < value or \
                            operator == ">" and item_value > value or \
                            operator == "<=" and item_value <= value or \
                            operator == ">=" and item_value >= value or \
                            operator == "above_mean" and item_value > global_mean or \
                            operator == "below_percentile" and item_value < global_percentile_75:
                        data_filtered.append(item)

                elif isinstance(item_value, list) and isinstance(value, (int, float)):
                    if operator == "len" and len(item_value) == value or \
                            operator == "<" and len(item_value) < value or \
                            operator == ">" and len(item_value) > value or \
                            operator == "<=" and len(item_value) <= value or \
                            operator == ">=" and len(item_value) >= value or \
                            (operator == "min" and min(item_value) >= value) or \
                            (operator == "max" and max(item_value) > value) or \
                            (operator == "mean" and sum(item_value) / len(item_value) > value) or \
                            operator == "all" and all(isinstance(x, (int, float)) and x > value for x in item_value):
                        data_filtered.append(item)

        return data_filtered


    def sort_data(self):
        if not self.data:
            messagebox.showinfo("Info", "Aucune donnée chargée.")
            return

        sort_window = tk.Toplevel(self.root)
        sort_window.title("Choisir les critères de tri")
    
        tk.Label(sort_window, text="Sélectionnez les colonnes et l'ordre de tri :", font=("Arial", 12)).pack(pady=10)

        columns = list(self.data[0].keys())
        columns_var = tk.StringVar(value=columns) 

        column_listbox = tk.Listbox(sort_window, listvariable=columns_var, selectmode=tk.MULTIPLE, height=6)
        column_listbox.pack(pady=10)

        order_var = tk.StringVar(value="ascend") 
        tk.Label(sort_window, text="Ordre de tri :").pack(pady=10)
        order_frame = tk.Frame(sort_window)
        order_frame.pack(pady=10)
        tk.Radiobutton(order_frame, text="Croissant", variable=order_var, value="ascend").pack(side=tk.LEFT)
        tk.Radiobutton(order_frame, text="Décroissant", variable=order_var, value="descend").pack(side=tk.LEFT)
        self.original_data = self.data.copy() 


        def sort_action():
            selected_columns = [columns[i] for i in column_listbox.curselection()]
        
            if not selected_columns:
                messagebox.showerror("Erreur", "Veuillez sélectionner au moins une colonne pour trier.")
                return
        
            reverse = order_var.get() == "descend"

            self.data.sort(key=lambda x: tuple(x.get(col) for col in selected_columns), reverse=reverse)

            sort_window.destroy()
            self.show_data()

        tk.Button(sort_window, text="Trier", command=sort_action).pack(pady=20)

        tk.Button(sort_window, text="Annuler", command=sort_window.destroy).pack(pady=5)

        sort_window.mainloop()



if __name__ == "__main__":
    root = tk.Tk()
    app = DataManagerApp(root)
    root.mainloop()
