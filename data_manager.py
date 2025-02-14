import csv
import json
import xml.etree.ElementTree as ET
import yaml

def load_csv(file):
    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

def save_csv(file, data):
    with open(file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
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
    return [{child.tag: child.text for child in item} for item in root]

def save_xml(file, data):
    root = ET.Element("Data")
    for row in data:
        item = ET.SubElement(root, "Item")
        for key, value in row.items():
            child = ET.SubElement(item, key)
            child.text = str(value)
    tree = ET.ElementTree(root)
    tree.write(file)

def load_yaml(file):
    with open(file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_yaml(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f)
