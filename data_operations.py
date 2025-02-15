import numpy as np
import statistics
from tkinter import messagebox, Toplevel, Label, StringVar, Entry, Button, ttk
import tkinter as tk

def show_stats(data):
    if not data:
        messagebox.showinfo("Info", "Aucune donnée chargée.")
        return

    stats_result = {}
    for key in data[0].keys():
        values = [item[key] for item in data if key in item]
        numeric_values = []
        for v in values:
            try:
                numeric_values.append(float(v))
            except ValueError:
                continue
        if numeric_values:
            stats_result[key] = f"Min: {min(numeric_values)}, Max: {max(numeric_values)}, Moyenne: {sum(numeric_values) / len(numeric_values):.2f}"
    
    if stats_result:
        result_text = "\n".join([f"{key}: {value}" for key, value in stats_result.items()])
        messagebox.showinfo("Statistiques", result_text)

def filter_data(app):
    if not app.data:
        messagebox.showinfo("Info", "Aucune donnée chargée.")
        return

    app.original_data = app.data.copy()

    filter_window = Toplevel(app.root)
    filter_window.title("Filtrer les Données")

    Label(filter_window, text="Sélectionnez la clé, la valeur et l'opérateur pour filtrer :", font=("Arial", 12)).pack(pady=10)
    
    columns = list(app.data[0].keys())
    key_var = StringVar(value=columns[0])
    Label(filter_window, text="Sélectionnez la clé :").pack(pady=5)
    key_menu = ttk.Combobox(filter_window, textvariable=key_var, values=columns)
    key_menu.pack(pady=5)

    Label(filter_window, text="Entrez la valeur :").pack(pady=5)
    value_entry = Entry(filter_window)
    value_entry.pack(pady=5)

    operator_var = StringVar(value="==")
    operators = ["==", "!=", "<", ">", "<=", ">=", "startswith", "endswith", "contains", "above_mean", "below_percentile"]
    Label(filter_window, text="Sélectionnez l'opérateur :").pack(pady=5)
    operator_menu = ttk.Combobox(filter_window, textvariable=operator_var, values=operators)
    operator_menu.pack(pady=5)

    def apply_filter():
        key = key_var.get()
        value = value_entry.get()
        operator = operator_var.get()

        try:
            if isinstance(app.data[0].get(key), (int, float)):
                value = float(value) if '.' in value else int(value)
        except ValueError:
            pass 

        filtered_data = filter_data_logic(app.data, key, value, operator)
        app.data = filtered_data  
        app.show_data()
        filter_window.destroy()

    Button(filter_window, text="Appliquer le filtre", command=apply_filter).pack(pady=10)
    Button(filter_window, text="Annuler", command=filter_window.destroy).pack(pady=5)

    filter_window.mainloop()

def filter_data_logic(data, key, value, operator):
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
def sort_data(app):
    if not app.data:
        messagebox.showinfo("Info", "Aucune donnée chargée.")
        return

    sort_window = Toplevel(app.root)
    sort_window.title("Choisir les critères de tri")

    Label(sort_window, text="Sélectionnez les colonnes et l'ordre de tri :", font=("Arial", 12)).pack(pady=10)

    columns = list(app.data[0].keys())
    columns_var = StringVar(value=columns)

    column_listbox = tk.Listbox(sort_window, listvariable=columns_var, selectmode=tk.MULTIPLE, height=6)
    column_listbox.pack(pady=10)

    order_var = StringVar(value="ascend")
    Label(sort_window, text="Ordre de tri :").pack(pady=10)
    order_frame = tk.Frame(sort_window)
    order_frame.pack(pady=10)
    tk.Radiobutton(order_frame, text="Croissant", variable=order_var, value="ascend").pack(side=tk.LEFT)
    tk.Radiobutton(order_frame, text="Décroissant", variable=order_var, value="descend").pack(side=tk.LEFT)
    app.original_data = app.data.copy()

    def sort_action():
        selected_columns = [columns[i] for i in column_listbox.curselection()]
    
        if not selected_columns:
            messagebox.showerror("Erreur", "Veuillez sélectionner au moins une colonne pour trier.")
            return
    
        reverse = order_var.get() == "descend"

        app.data.sort(key=lambda x: tuple(x.get(col) for col in selected_columns), reverse=reverse)

        sort_window.destroy()
        app.show_data()

    Button(sort_window, text="Trier", command=sort_action).pack(pady=20)
    Button(sort_window, text="Annuler", command=sort_window.destroy).pack(pady=5)

    sort_window.mainloop()
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
