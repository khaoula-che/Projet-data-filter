import csv
import json
import xml.etree.ElementTree as ET
import yaml
import statistics
import numpy as np


# charger des donnees depuis un csv et retoune une liste de dict
def load_csv(file):
    data = []
    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for key, value in row.items():
                if value is None:  # Empêche les erreurs sur les valeurs vides
                    continue

                if value.startswith("[") and value.endswith("]"):
                    try:
                        row[key] = json.loads(value.replace("'", '"'))
                    except json.JSONDecodeError:
                        pass  # Si erreur, on laisse en texte

                elif value.replace('.', '', 1).isdigit():
                    if '.' in value:
                        row[key] = float(value)
                    else:
                        row[key] = int(value)

            data.append(row)
    return data


def save_csv(file, data):
    if not data:
        print("Aucune donnees à sauvegarder")
        return
    keys = data[0].keys()
    with open(file, 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)


def load_json(file):
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def load_xml(file):
    tree = ET.parse(file)
    root = tree.getroot()
    data = []
    for i in root:
        record = {}
        for child in i:
            if child.text.isdigit():
                record[child.tag] = int(child.text)
            elif child.text.replace('.', '', 1).isdigit():
                record[child.tag] = float(child.text)
            elif child.text.startswith("[") and child.text.endswith("]"):
                record[child.tag] = json.loads(child.text.replace("'", "\""))
            else:
                record[child.tag] = child.text

        data.append(record)
    return data


def save_xml(file, data):
    root = ET.Element("root")
    for i in data:
        item = ET.SubElement(root, "item")
        for key, value in i.items():
            child = ET.SubElement(item, key)
            child.text = str(value)
    tree = ET.ElementTree(root)
    tree.write(file)


def load_yaml(file):
    with open(file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_yaml(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False)


def mean(values):
    return round(sum(values) / len(values))


def stats(data):
    stats_result = {}

    for key in data[0].keys():
        values = [item[key] for item in data if key in item]

        values_num = [v for v in values if isinstance(v, (int, float))]
        values_bool = [v for v in values if isinstance(v, bool) or str(v).lower() in ['true', 'false']]
        values_list = [v for v in values if
                       isinstance(v, list) or (isinstance(v, str) and v.startswith('[') and v.endswith(']'))]

        stats_result[key] = {}

        if values_num:
            stats_result[key].update({
                'min': min(values_num),
                'max': max(values_num),
                'mean': round(sum(values_num) / len(values_num), 2)
            })

        if values_bool:
            count_true = sum(1 for v in values_bool if str(v).lower() == 'true')
            total = len(values_bool)
            stats_result[key].update({
                'true_percentage': round((count_true / total) * 100, 2),
                'false_percentage': round(100 - (count_true / total) * 100, 2)
            })

        if values_list:
            list_sizes = [len(json.loads(v.replace("'", '"'))) if isinstance(v, str) else len(v) for v in values_list]
            stats_result[key].update({
                'min_size': min(list_sizes),
                'max_size': max(list_sizes),
                'mean_size': round(sum(list_sizes) / len(list_sizes), 2)
            })

    return stats_result


def filter_data(data, key, value, operator):
    data_filtered = []

    numeric_values = [item[key] for item in data if key in item and isinstance(item[key], (int, float))]
    global_mean = statistics.mean(numeric_values) if numeric_values else 0
    global_percentile = np.percentile(numeric_values, value) if numeric_values else 0

    for item in data:
        if key in item:
            item_value = item[key]

            # Comparaison pour les chaînes de caractères
            if isinstance(item_value, str) and isinstance(value, str):
                if operator == "==" and item_value == value or \
                        operator == "!=" and item_value != value or \
                        operator == "startswith" and item_value.startswith(value) or \
                        operator == "endswith" and item_value.endswith(value) or \
                        operator == "contains" and value.lower() in item_value.lower():
                    data_filtered.append(item)

            # Comparaison pour les nombres
            elif isinstance(item_value, (int, float)) and isinstance(value, (int, float)):
                if operator == "==" and item_value == value or \
                        operator == "!=" and item_value != value or \
                        operator == "<" and item_value < value or \
                        operator == ">" and item_value > value or \
                        operator == "<=" and item_value <= value or \
                        operator == ">=" and item_value >= value or \
                        operator == "above_mean" and item_value > global_mean or \
                        operator == "below_percentile" and item_value < global_percentile:
                    data_filtered.append(item)

            # Comparaison pour les listes
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


def compare_data(data, field_1, field_2, operator):

    data_filtered = []

    for item in data:
        if field_1 in item and field_2 in item:
            value_1 = item[field_1]
            value_2 = item[field_2]

            # Comparaison pour les chaînes de caractères
            if isinstance(value_1, str) and isinstance(value_2, str):
                if (operator == "==" and value_1 == value_2) or \
                   (operator == "!=" and value_1 != value_2) or \
                   (operator == "<" and value_1 < value_2) or \
                   (operator == ">" and value_1 > value_2) or \
                   (operator == "<=" and value_1 <= value_2) or \
                   (operator == ">=" and value_1 >= value_2):
                    data_filtered.append(item)

            # Comparaison pour les nombres (int, float)
            elif isinstance(value_1, (int, float)) and isinstance(value_2, (int, float)):
                if (operator == "==" and value_1 == value_2) or \
                   (operator == "!=" and value_1 != value_2) or \
                   (operator == "<" and value_1 < value_2) or \
                   (operator == ">" and value_1 > value_2) or \
                   (operator == "<=" and value_1 <= value_2) or \
                   (operator == ">=" and value_1 >= value_2):
                    data_filtered.append(item)

    return data_filtered

file_csv = "data.csv"
file_json = "data.json"
file_xml = "data.xml"
file_yaml = "data.yaml"

data_csv = load_csv(file_csv)
data_json = load_json(file_json)
data_xml = load_xml(file_xml)
data_yaml = load_yaml(file_yaml)

import pprint

pp = pprint.PrettyPrinter(indent=4)

print("\n *** Étudiants nommés Marie :")
pp.pprint(filter_data(data_csv, "firstname", "Marie", "=="))

print("\n *** Étudiants ayant une note minimale de 17 :")
pp.pprint(filter_data(data_csv, "grades", 17, "min"))

print("\n *** Étudiants ayant exactement 4 notes :")
pp.pprint(filter_data(data_csv, "grades", 4, "len"))

print("\n *** Étudiants avec une moyenne de notes supérieure à 15 :")
pp.pprint(filter_data(data_csv, "grades", 15, "mean"))

print("\n *** Étudiants dont toutes les notes sont > 10 :")
pp.pprint(filter_data(data_csv, "grades", 10, "all"))

print("\n *** Étudiants dont le prénom commence par 'A' :")
pp.pprint(filter_data(data_csv, "firstname", "A", "startswith"))

print("\n *** Étudiants dont le prénom contient 'ou' :")
pp.pprint(filter_data(data_csv, "firstname", "ou", "contains"))

print("\n *** Étudiants âgés de plus de 25 ans :")
pp.pprint(filter_data(data_csv, "age", 25, ">"))

print("\n *** Étudiants qui sont apprentis :")
pp.pprint(filter_data(data_csv, "apprentice", "True", "=="))

print("\n *** Étudiants ayant plus de 3 notes :")
pp.pprint(filter_data(data_csv, "grades", 3, ">="))

print("\n *** Étudiants ayant toutes leurs notes supérieures à 15 :")
pp.pprint(filter_data(data_csv, "grades", 15, "all"))

print("\n *** Étudiants ayant un nom de famille se terminant par 't' :")
pp.pprint(filter_data(data_csv, "lastname", "t", "endswith"))