import csv
import json
import xml.etree.ElementTree as ET
import yaml
from os import write

# charger des donnees depuis un csv et retoune une liste de dict
def load_csv(file):
    data = []
    with open(file, 'r', encoding='utf-8') as f :
        reader = csv.DictReader(f)
        for row in reader : 
            data.append(row)
    return data

def save_csv(file,data):
    if not data : 
        print("Aucune donnees à sauvegarder")
        return
    keys = data[0].keys()
    with open(file, 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, file=keys)
        writer.writeheader()
        writer.writerows(data)

def load_json(file):
    with open(file,'r', encoding='utf-8') as f :
        return json.load(f)
    
def save_json(file, data) :
    with open(file,'w',encoding='utf-8') as f :
        json.dump(data,f, indent=4)

def load_xml(file):
    tree = ET.parse(file)
    root = tree.getroot()
    data = []
    for i in root : 
        item = {child.tag: child.text for child in i}
        data.append(item)
    return data
        
def save_xml(file,data) :
    root = ET.Element("root")
    for i in data :
        item = ET.SubElement(root,"item")
        for key,value in item.items():
            child = ET.SubElement(item,key)
            child.text = str(value)
    tree = ET.ElementTree(root)
    tree.write(file)
def load_yaml(file) :
    with open(file, 'r',encoding='utf-8') as f :
        return yaml.safe_load(f)

def save_yaml(file, data) :
    with open(file,'w', encoding='utf-8') as f :
        yaml.dump(data, f,default_flow_style=False)
def mean(values) :
    return sum(values) / len(values)

def stats(data) :
    stats ={}
    for key in data[0].keys():
        values = [item[key] for item in data if key in item]
        values_num = []
        for v in values : 
           if isinstance(v, (int, float)):
                values_num.append(v)
           elif isinstance(v, str) and v.replace('.', '', 1).isdigit():
                values_num.append(float(v))
        if values_num :
            stats[key] = { 
                'min': min(values_num), 
                'max': max(values_num),
                'mean': mean(values_num)
            }
        
    return stats

file_csv = "data.csv"
file_json = "data.json"
file_xml = "data.xml"
file_yaml = "data.yaml"

data_csv = load_csv(file_csv)
data_json = load_json(file_json)
data_xml = load_xml(file_xml)
data_yaml = load_yaml(file_yaml)
stats = stats(data_json)
print("données CSV chargées :", data_csv)
print("données JSON chargées :", data_json)
print("données XML chargées :", data_xml)
print("données YAML chargées :", data_yaml)
print("Statistiques des données :", stats)
