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
            for key,value in row.items() :
                if value.startswith("[") and value.endswith("]") :
                    row[key] = eval(value)
                
                elif value.replace('.', '', 1).isdigit() :
                    if '.' in value :
                        row[key] = float(value)
                    else :
                        row[key] = int(value)
                   
            data.append(row)
    return data

def save_csv(file,data):
    if not data : 
        print("Aucune donnees à sauvegarder")
        return
    keys = data[0].keys()
    with open(file, 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
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
        record = {}
        for child in i :
            if child.text.isdigit() :
                record[child.tag] = int(child.text) 
            elif child.text.replace('.', '',1).isdigit() :
                record[child.tag] = float(child.text)
            elif child.text.startswith("[") and child.text.endswith("]"):
                record[child.tag] = json.loads(child.text.replace("'", "\""))
            else :
                record[child.tag] = child.text
     
        data.append(record)
    return data
        
def save_xml(file,data) :
    root = ET.Element("root")
    for i in data :
        item = ET.SubElement(root,"item")
        for key,value in i.items():
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
    return round(sum(values) / len(values))

def stats(data) :
    stats_result ={}
    for key in data[0].keys():
        values = [item[key] for item in data if key in item]

        values_num = []
        values_bool = []
        values_list = []

        for v in values : 
            if isinstance(v, (int,float)) :
                values_num.append(v)
            elif isinstance(v,str) and v.replace('.', '',1).isdigit() :
                values_num.append(float(v))
            
            if isinstance(v,bool) or str(v).lower() in ['true', 'false']:
                values_bool.append(v)
            if isinstance(v, list) or (isinstance(v, str) and v.startswith('[') and v.endswith(']')) : 
                values_list.append(v)
            
        if values_num :
            stats_result[key] = { 
                'min': min(values_num), 
                'max': max(values_num),
                'mean': mean(values_num)
        }
        if values_bool : 
            count = 0
            for v in values_bool : 
                if str(v).lower() == 'true' :
                    count +=1
            stats_result[key] = {
                'true_parcentage' : round((count / len(values_bool)) * 100),
                'false_parcentage': round(100 - (count / len(values_bool)) * 100)
            }
        if values_list : 
            list_sizes = []
            for v in values_list: 
                if isinstance(v, str):
                    list_sizes.append(len(eval(v)))
                else : 
                    list_sizes.append(len(v))
            stats_result[key] = {
                'min_size': round(min(list_sizes), 2),
                'max_size': round(max(list_sizes),2),
                'mean_size': mean(list_sizes)
            }
    return stats_result

def filter_data(data, key, value, operator) :
    data_filtered = []
    for item in data :
        if key in item : 
            item_value = item[key]
            if isinstance(item_value, str) and item_value.replace('.', '', 1).isdigit():
                item_value = float(item_value) if '.' in item_value else int(item_value)
            
            # Conversion de value en nombre si possible
            if isinstance(value, str) and value.replace('.', '', 1).isdigit():
                value = float(value) if '.' in value else int(value)
            
            if isinstance(item_value, str) and isinstance(value,str):
                if (operator == "==" and item_value == value ) :
                    data_filtered.append(item)
                elif (operator == "<" and item_value < value ) :
                    data_filtered.append(item)
                elif (operator == ">" and item_value > value ): 
                    data_filtered.append(item)

            elif isinstance(item_value, (int,float)) :
                if (operator == "==" and item_value == value ) :
                    data_filtered.append(item)
                elif (operator == "<" and item_value < value ) :
                    data_filtered.append(item)
                elif (operator == ">" and item_value > value ): 
                    data_filtered.append(item)

            elif isinstance(item_value, list)  :
                if (operator =="<" and len(item_value) < value) :
                    data_filtered.append(item)
                elif (operator ==">" and len(item_value) > value):
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

print("Données CSV chargées :", stats(data_csv))
print("Données JSON chargées :", stats(data_json))
print("Données XML chargées :", stats(data_xml))
print("Données YAML chargées :", stats(data_yaml))

print("Données CSV filtrées (firstname < 'Marie'):", filter_data(data_csv, "firstname", "Marie", "<"))
print("Données JSON filtrées (firstname < 'Marie'):", filter_data(data_json, "firstname", "Marie", "<"))
print("Données XML filtrées (firstname < 'Marie'):", filter_data(data_xml, "firstname", "Marie", "<"))
print("Données YAML filtrées (firstname < 'Marie'):", filter_data(data_yaml, "firstname", "Marie", "<"))

print("Données CSV filtrées (nombre de notes > 3):", filter_data(data_csv, "grades", 3, ">"))
print("Données JSON filtrées (nombre de notes > 3):", filter_data(data_json, "grades", 3, ">"))
print("Données XML filtrées (nombre de notes > 3):", filter_data(data_xml, "grades", 3, ">"))
print("Données YAML filtrées (nombre de notes > 3):", filter_data(data_yaml, "grades", 3, ">"))

print("Données CSV filtrées (age > 25):", filter_data(data_csv, "age", 25, ">"))
print("Données JSON filtrées (age > 25):", filter_data(data_json, "age", 25, ">"))
print("Données XML filtrées (age > 25):", filter_data(data_xml, "age", 25, ">"))
print("Données YAML filtrées (age > 25):", filter_data(data_yaml, "age", 25, ">"))