import csv
import json
import xml.etree.ElementTree as ET
import yaml


def load_csv(file):
    data = []
    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data


def save_csv(file, data):
    if not data:
        print("Aucune donnees à sauvegarder")
        return
    keys = data[0].keys()
    with open(file, 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, file=keys)
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
        item = {child.tag: child.text for child in i}
        data.append(item)
    return data


def save_xml(file, data):
    root = ET.Element("root")
    for i in data:
        item = ET.SubElement(root, "item")
        for key, value in item.items():
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