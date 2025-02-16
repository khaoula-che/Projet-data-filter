import csv
import json
import xml.etree.ElementTree as ET
import yaml


def load_csv(file):
    with open(file, 'r', encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))  # Utilisation directe sans boucle


def save_csv(file, data):
    if not data:
        print("Aucune donnée à sauvegarder")
        return
    keys = data[0].keys()
    with open(file, 'w', encoding='utf-8', newline='') as f:
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
    return [{child.tag: child.text for child in item} for item in root]  # Utilisation de la compréhension de liste


def save_xml(file, data):
    root = ET.Element("root")
    for i in data:
        item = ET.SubElement(root, "item")
        for key, value in i.items():
            child = ET.SubElement(item, key)
            child.text = str(value) if value is not None else ""  # Éviter "None"
    tree = ET.ElementTree(root)
    tree.write(file, encoding="utf-8", xml_declaration=True)


def load_yaml(file):
    with open(file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or []


def save_yaml(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False)
