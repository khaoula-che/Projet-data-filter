import statistics
from tkinter import messagebox, Toplevel, Label, StringVar, Entry, Button, ttk
import tkinter as tk
import numpy as np
from tkinter import messagebox
import ast  # Pour convertir une chaîne en liste

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
    filter_window.geometry("400x300")  # Ajuste la taille pour garantir l'affichage

    Label(filter_window, text="Sélectionnez la clé, la valeur et l'opérateur pour filtrer :", font=("Arial", 12)).pack(pady=10)

    columns = list(app.data[0].keys())
    key_var = StringVar(value=columns[0])

    Label(filter_window, text="Sélectionnez la clé :").pack(pady=5)
    key_menu = ttk.Combobox(filter_window, textvariable=key_var, values=columns)
    key_menu.pack(pady=5)

    Label(filter_window, text="Entrez la valeur (seuil) :").pack(pady=5)
    value_entry = Entry(filter_window)
    value_entry.pack(pady=5)

    operator_var = StringVar(value="==")
    operators = ["==", "!=", "<", ">", "<=", ">=", "startswith", "endswith", "contains",
                 "above_mean", "below_percentile", "len", "min", "max", "mean", "all", "at_least_X_above", "firstname_before_lastname", "computed_value"]

    Label(filter_window, text="Sélectionnez l'opérateur :").pack(pady=5)
    operator_menu = ttk.Combobox(filter_window, textvariable=operator_var, values=operators)
    operator_menu.pack(pady=5)

    # ajout d'un champ X pour personnaliser le nombre de valeurs requises
    x_label = Label(filter_window, text="Nombre minimum de valeurs supérieures à (X) :", font=("Arial", 10))
    x_entry = Entry(filter_window)

    def update_x_entry(event):
        #afficher le champ X seulement si l'opérateur 'at_least_X_above' est sélectionné
        if operator_var.get() == "at_least_X_above":
            x_label.pack(pady=5)
            x_entry.pack(pady=5)
        else:
            x_label.pack_forget()
            x_entry.pack_forget()

    operator_menu.bind("<<ComboboxSelected>>", update_x_entry)

    def apply_filter():
        key = key_var.get()
        value = value_entry.get().strip()
        operator = operator_var.get()

        # gestion pour 'above_mean' et 'below_percentile' : ingorer `value` si l'opérateur ne nécessite pas de valeur utilisateur
        if operator in ["above_mean", "below_percentile"]:
            value = None

        # gestion pour 'firstname_before_lastname' : ingorer key et value si l'opérateur est "firstname_before_lastname"
        key_to_use = key if operator != "firstname_before_lastname" else None
        value_to_use = value if operator not in ["firstname_before_lastname", "above_mean",
                                                 "below_percentile"] else None

        # gestion pour 'computed_value': ingnorer la cle pour computed_value
        if operator == "computed_value":
            key_to_use = None  # Clé inutile pour `computed_value`


        #  verifications et conversion de X
        x_value = None
        if operator == "at_least_X_above":
            try:
                x_value = int(x_entry.get())
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer un nombre valide pour X.")
                return


        # Execution du filtrage
        filtered_data = filter_data_logic(app.data, key_to_use, value_to_use, operator, x_value)

        # message d'erreur
        if not filtered_data:
            key_display = key_to_use if key_to_use is not None else "aucune clé"
            value_display = value_to_use if value_to_use is not None else "aucune valeur"

            messagebox.showinfo("Résultat du Filtrage",
                                f"Aucun élément ne correspond à '{operator}' avec {key_display} et {value_display}.")
            return

        # mettre à jour les données
        app.data = filtered_data
        app.show_data()
        filter_window.destroy()

    # affichage des boutons
    button_frame = tk.Frame(filter_window)
    button_frame.pack(pady=10)

    Button(button_frame, text="Appliquer le filtre", command=apply_filter).pack(side=tk.LEFT, padx=5)
    Button(button_frame, text="Annuler", command=filter_window.destroy).pack(side=tk.RIGHT, padx=5)

    filter_window.mainloop()



def try_convert_float(value):
    """Convertit une valeur en float si possible, sinon retourne None."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def filter_data_logic(data, key, value, operator, x_value=None):
    print(f"DEBUG: key={key}, value={value}, operator={operator}")
    data_filtered = []

    # Cas particulier : le filtrage par "firstname_before_lastname"
    if operator == "firstname_before_lastname":
        for item in data:
            if "firstname" in item and "lastname" in item:
                firstname = str(item["firstname"]).strip().lower()
                lastname = str(item["lastname"]).strip().lower()
                print(f"DEBUG: Comparing {firstname} < {lastname} ? {firstname < lastname}")

                if firstname and lastname and firstname < lastname:
                    data_filtered.append(item)

        return data_filtered  # retour immédiat

    # Cas particulier : le filtrage sur les statistiques globales (`above_mean`, `below_percentile`)
    if operator in ["above_mean", "below_percentile"]:
        print(f"DEBUG: Liste des valeurs avant conversion: {[item[key] for item in data if key in item]}")

        numeric_values = []
        for item in data:
            if key in item:
                raw_value = item[key]

                if isinstance(raw_value, str) and raw_value.startswith("[") and raw_value.endswith("]"):
                    try:
                        raw_value = ast.literal_eval(raw_value)  # Convertir en liste
                    except (ValueError, SyntaxError):
                        continue  # Ignorer en cas d'erreur

                if isinstance(raw_value, list):
                    numeric_values.extend([try_convert_float(x) for x in raw_value if try_convert_float(x) is not None])
                else:
                    converted_value = try_convert_float(raw_value)
                    if converted_value is not None:
                        numeric_values.append(converted_value)

        if not numeric_values:
            messagebox.showerror("Erreur", "Aucune valeur numérique trouvée pour calculer la moyenne ou le percentile.")
            return []

        global_mean = statistics.mean(numeric_values)
        global_percentile_75 = np.percentile(numeric_values, 75)
        print(f"DEBUG: Moyenne globale = {global_mean}")
        print(f"DEBUG: 75e percentile = {global_percentile_75}")

    # Cas particulier : le filtrage sur une combinaison de champs
    if operator == "computed_value":
        try:
            threshold = float(value)  # Vérifier que `value` est un nombre valide
        except ValueError:
            messagebox.showerror("Erreur", f"Le seuil '{value}' n'est pas un nombre valide.")
            return []

        for item in data:
            if "price" in item and "quantity" in item:  # Vérifier l'existence des clés
                price = try_convert_float(item["price"])
                quantity = try_convert_float(item["quantity"])

                if price is not None and quantity is not None:
                    computed_value = price * quantity
                    print(f"DEBUG: ({price} * {quantity}) = {computed_value}")

                    if computed_value > threshold:
                        data_filtered.append(item)

        return data_filtered  # Retourner les résultats immédiatement

    # Boucle sur les éléments de data
    for item in data:
        print(f"DEBUG: item={item}")
        if key in item:
            item_value = item[key]

            # Conversion des listes
            if isinstance(item_value, str) and item_value.startswith("[") and item_value.endswith("]"):
                try:
                    item_value = ast.literal_eval(item_value)
                except (ValueError, SyntaxError):
                    continue

            item_value_converted = try_convert_float(item_value)

            # Filtrage above_mean et below_percentile
            if operator in ["above_mean", "below_percentile"]:
                if isinstance(item_value, list):
                    item_mean = sum(try_convert_float(x) for x in item_value if try_convert_float(x) is not None) / len(item_value)
                else:
                    item_mean = item_value_converted

                if operator == "above_mean" and item_mean is not None and item_mean > global_mean:
                    data_filtered.append(item)
                elif operator == "below_percentile" and item_mean is not None and item_mean < global_percentile_75:
                    data_filtered.append(item)

            # Gestion des nombres (age, price ...)
            elif isinstance(item_value_converted, (int, float)) and operator in ["==", "!=", "<", ">", "<=", ">=", "min", "max"]:
                try:
                    value = float(value)
                    if (operator == "==" and item_value_converted == value) or \
                       (operator == "!=" and item_value_converted != value) or \
                       (operator == "<" and item_value_converted < value) or \
                       (operator == ">" and item_value_converted > value) or \
                       (operator == "<=" and item_value_converted <= value) or \
                       (operator == ">=" and item_value_converted >= value) or \
                       (operator == "min" and item_value_converted >= value) or \
                       (operator == "max" and item_value_converted <= value):
                        data_filtered.append(item)
                except ValueError:
                    messagebox.showerror("Erreur", f"La valeur '{value}' n'est pas un nombre valide.")
                    return []

            # Gestion des chaines de cara (firstname, lastname...)
            elif isinstance(item_value, str):
                try:
                    if operator in ["==", "!="]:
                        if str(value).isdigit():
                            value = int(value)
                            if (operator == "==" and len(item_value) == value) or \
                               (operator == "!=" and len(item_value) != value):
                                data_filtered.append(item)
                        else:
                            if (operator == "==" and item_value.lower() == value.lower()) or \
                               (operator == "!=" and item_value.lower() != value.lower()):
                                data_filtered.append(item)

                    elif operator in ["<", ">", "<=", ">=", "min", "max"]:
                        if str(value).isdigit():
                            value = int(value)
                            if (operator == "<" and len(item_value) < value) or \
                               (operator == ">" and len(item_value) > value) or \
                               (operator == "<=" and len(item_value) <= value) or \
                               (operator == ">=" and len(item_value) >= value) or \
                               (operator == "min" and len(item_value) >= value) or \
                               (operator == "max" and len(item_value) <= value):
                                data_filtered.append(item)
                        else:
                            if (operator == "<" and item_value.lower() < value.lower()) or \
                               (operator == ">" and item_value.lower() > value.lower()) or \
                               (operator == "<=" and item_value.lower() <= value.lower()) or \
                               (operator == ">=" and item_value.lower() >= value.lower()):
                                data_filtered.append(item)

                    elif (operator == "startswith" and item_value.lower().startswith(value.lower())) or \
                         (operator == "endswith" and item_value.lower().endswith(value.lower())) or \
                         (operator == "contains" and value.lower() in item_value.lower()):
                        data_filtered.append(item)

                except ValueError:
                    messagebox.showerror("Erreur", f"La valeur '{value}' n'est pas valide pour filtrer les chaînes de caractères.")
                    return []

            # Gestion des listes
            elif isinstance(item_value, list):
                try:
                    value = try_convert_float(value)
                    if value is None or not isinstance(value, (int, float)):
                        raise ValueError(f"Valeur '{value}' invalide pour le filtrage.")

                    # Filtrage basé sur la longueur de la liste
                    if (operator == "==" and len(item_value) == value) or \
                            (operator == "!=" and len(item_value) != value) or \
                            (operator == "<" and len(item_value) < value) or \
                            (operator == "<=" and len(item_value) <= value) or \
                            (operator == ">" and len(item_value) > value) or \
                            (operator == ">=" and len(item_value) >= value):
                        data_filtered.append(item)

                    # Filtrage basé sur les valeurs contenues dans la liste
                    elif (operator == "contains" and value in item_value) or \
                       (operator == "min" and min(item_value) >= value) or \
                       (operator == "max" and max(item_value) > value) or \
                       (operator == "mean" and sum(item_value) / len(item_value) > value):
                        data_filtered.append(item)

                except ValueError:
                    messagebox.showerror("Erreur", f"La valeur '{value}' n'est pas valide pour filtrer les listes.")
                    return []

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