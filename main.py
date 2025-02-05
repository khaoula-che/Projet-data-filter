import csv
from os import write
import json
import yaml
import xml.etree.ElementTree as ET

# charger des donnees depuis un csv et retoune une liste de dict
def load_csv(file):
    data = []
    with open(file, 'r') as f :
        reader = csv.DictReader(f)
        for row in reader : 
            data.append(row)
    return data

def save_csv(file,data):
    if not data : 
        print("Aucune donnees à sauvegarder")
        return
    keys = data[0].keys()
    with open(file, 'w') as f:
        writer = csv.DictWriter(f, file=keys)
        writer.writeheader()
        writer.writerows(data)

def load_json(file):
    with open(file,"r") as f :
        return json.load(f)
    
def save_json(file, data) :
    with open(file,"w") as f :
         json.dump(data,file, indent=4)

file_csv = "data.csv"
file_json = "data.json"

data_csv = load_csv(file_csv)
data_json = load_json(file_json)

print("données CSV chargées ", data_csv)
print("données JSON chargées ", data_json)

