import os
import json

# Directory containing JSON files
directory = r'directory'

# Definiere die Zielwerte ("Werte"), die gesucht werden sollen

target_values = {
    "dd A", "alter", "crpn2", "schwanger", "sswtr", 
    "quickA", "pttp A", "fibc A", "at A", "fps A", 
    "ggt", "hb", "wbc", "f13 A"
}



def search_values_in_json(json_data, targets):
    found_values = {}
    
    def search_recursive(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key in targets:
                    found_values[key] = value
                if key == "TestLISCode" and value in targets:
                    found_values[value] = value
                search_recursive(value)
        elif isinstance(data, list):
            for element in data:
                search_recursive(element)
                
    search_recursive(json_data)
    return found_values

# Function to safely convert values for comparison
def safe_convert(value):
    try:
        return float(value)
    except ValueError:
        return value

# Process rules function to show found and missing values per rule
def process_regeln(data, regeln):
    for i, regel in enumerate(regeln, start=1):
        found_values = []
        missing_values = []
        
        # Check for each condition if the parameter is in data
        for condition in regel["bedingungen"]:
            param = condition["parameter"]
            if param in data:
                found_values.append(param)
            else:
                missing_values.append(param)
        
        # Print the results for the current rule
        print(f"Regel {i}:")
        print("  Werte drin:", ", ".join(found_values) if found_values else "Keine")
        print("  Werte nicht drin:", ", ".join(missing_values) if missing_values else "Keine")
        print()  # Empty line for b
# Definieren Sie die Regeln für jede ID in einem strukturierten Format
regeln = [
    {
        "id": "ddimer_60",
        "abschnitt": "Diagnosen",
        "logik": "UND",
        "textbaustein": "D-Dimer-Erhöhung, {{dd A}} ng/ml (altersentsprechende Norm: <600), kontrollbedürftig",
        "bedingungen": [
            {"nr": 1, "typ": "messung", "parameter": "dd A", "operator": ">", "wert": 600},
            {"nr": 2, "typ": "kontext", "parameter": "alter", "operator": ">", "wert": 59},
            {"nr": 3, "typ": "kontext", "parameter": "alter", "operator": "<", "wert": 70}
        ]
    },
    {
        "id": "ddimer_70",
        "abschnitt": "Diagnosen",
        "logik": "UND",
        "textbaustein": "D-Dimer-Erhöhung, {{dd A}} ng/ml (altersentsprechende Norm: <700), kontrollbedürftig",
        "bedingungen": [
            {"nr": 1, "typ": "messung", "parameter": "dd A", "operator": ">", "wert": 700},
            {"nr": 2, "typ": "kontext", "parameter": "alter", "operator": ">", "wert": 69},
            {"nr": 3, "typ": "kontext", "parameter": "alter", "operator": "<", "wert": 80}
        ]
    },
    {
        "id": "ddimer_ohne_CRP",
        "abschnitt": "Diagnosen",
        "logik": "UND",
        "textbaustein": "D-Dimer-Erhöhung, {{dd A}} ng/ml, kontrollbedürftig",
        "bedingungen": [
            {"nr": 1, "typ": "messung", "parameter": "dd A", "operator": ">", "wert": 520},
            {"nr": 2, "typ": "messung", "parameter": "crpn2", "operator": "<", "wert": 6},
            {"nr": 3, "typ": "kontext", "parameter": "alter", "operator": "<", "wert": 60},
            {"nr": 4, "typ": "kontext", "parameter": "schwanger", "operator": "=", "wert": "nein"}
        ]
    },
    {
        "id": "ddimer_mit_CRP",
        "abschnitt": "Diagnosen",
        "logik": "UND",
        "textbaustein": "D-Dimer-Erhöhung, {{dd A}} ng/ml a. e. bei CRP ↑ {{crpn2}} mg/l, kontrollbedürftig",
        "bedingungen": [
            {"nr": 1, "typ": "messung", "parameter": "dd A", "operator": ">", "wert": 520},
            {"nr": 2, "typ": "messung", "parameter": "crpn2", "operator": ">", "wert": 5},
            {"nr": 3, "typ": "kontext", "parameter": "alter", "operator": "<", "wert": 60},
            {"nr": 4, "typ": "kontext", "parameter": "schwanger", "operator": "=", "wert": "nein"}
        ]
    },
    {
        "id": "ddimer_ssw_leicht",
        "abschnitt": "Diagnosen",
        "logik": "Kombination",
        "textbaustein": "leicht überproportionale D-Dimer-Erhöhung, {{dd A}} ng/ml DD: Ausdruck eines gesteigerten Thromboserisikos",
        "bedingungen": [
            {"nr": 1, "typ": "messung", "parameter": "crpn2", "operator": "<", "wert": 15},
            {"nr": 2, "typ": "messung", "parameter": "dd A", "operator": ">", "wert": 1382},
            {"nr": 3, "typ": "messung", "parameter": "dd A", "operator": "<", "wert": 1755},
            {"nr": 4, "typ": "messung", "parameter": "sswtr", "operator": ">", "wert": 2},
            {"nr": 5, "typ": "messung", "parameter": "sswtr", "operator": "<", "wert": 8},
            # Weitere Bedingungssets können hier hinzugefügt werden, um die komplexe Regel zu vervollständigen
        ]
    },
    {
        "id": "d_Schwangerschaftskontrolle_unauffällig",
        "abschnitt": "Diagnosen",
        "logik": "Kombination",
        "textbaustein": "keine überproportionale Hämostaseaktivierung in der Schwangerschaft",
        "bedingungen": [
            {"nr": 1, "typ": "messung", "parameter": "crpn2", "operator": "<", "wert": 15},
            {"nr": 2, "typ": "messung", "parameter": "quickA", "operator": ">", "wert": 80},
            {"nr": 3, "typ": "messung", "parameter": "pttp A", "operator": "<", "wert": 38},
            {"nr": 4, "typ": "messung", "parameter": "fibc A", "operator": ">", "wert": 2},
            {"nr": 5, "typ": "messung", "parameter": "at A", "operator": ">", "wert": 80},
            {"nr": 6, "typ": "messung", "parameter": "fps A", "operator": ">", "wert": 30},
            {"nr": 7, "typ": "messung", "parameter": "ggt", "operator": "<", "wert": 40},
            {"nr": 8, "typ": "messung", "parameter": "hb", "operator": ">", "wert": 10},
            {"nr": 9, "typ": "messung", "parameter": "wbc", "operator": "<", "wert": 13.6}
        ]
    },
    {
        "id": "ddimer_ssw_leicht_CRP",
        "abschnitt": "Diagnosen",
        "logik": "Kombination",
        "textbaustein": "leicht überproportionale D-Dimer-Erhöhung, {{dd A}} ng/ml a. e. bei CRP ↑ {{crpn2}} mg/l",
        "bedingungen": [
            {"nr": 1, "typ": "messung", "parameter": "crpn2", "operator": ">", "wert": 15},
            {"nr": 2, "typ": "messung", "parameter": "sswtr", "operator": ">", "wert": 3},
            {"nr": 3, "typ": "messung", "parameter": "sswtr", "operator": "<", "wert": 8},
            {"nr": 4, "typ": "messung", "parameter": "dd A", "operator": ">", "wert": 1382},
            {"nr": 5, "typ": "messung", "parameter": "dd A", "operator": "<", "wert": 1755}
            # Weiteres für komplexe Konditionen hinzufügen
        ]
    },
    {
        "id": "d_schwanger",
        "abschnitt": "Diagnosen",
        "logik": "UND",
        "textbaustein": "aktuelle Schwangerschaft in der {{sswtr}}. SSW",
        "bedingungen": [
            {"nr": 1, "typ": "messung", "parameter": "sswtr", "operator": ">", "wert": 2}
        ]
    },
    {
        "id": "df13_ss",
        "abschnitt": "Diagnosen",
        "logik": "UND",
        "textbaustein": "V. a. milder Faktor-XIII-Mangel, {{f13 A}} % DD: erworben (überproportional für die Gravidität, kontrollbedürftig)",
        "bedingungen": [
            {"nr": 1, "typ": "messung", "parameter": "f13 A", "operator": "<", "wert": 60},
            {"nr": 2, "typ": "messung", "parameter": "sswtr", "operator": ">", "wert": 2}
        ]
    },
    {
        "id": "df13",
        "abschnitt": "Diagnosen",
        "logik": "UND",
        "textbaustein": "V. a. milder Faktor-XIII-Mangel, {{f13 A}} % DD: erworben, kontrollbedürftig",
        "bedingungen": [
            {"nr": 1, "typ": "messung", "parameter": "f13 A", "operator": "<", "wert": 70},
            {"nr": 2, "typ": "kontext", "parameter": "schwanger", "operator": "=", "wert": "nein"}
        ]
    }
]


# Scan each JSON file in the directory
# Scan each JSON file in the directory
for filename in os.listdir(directory):
    if filename.endswith(".json"):
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                found = search_values_in_json(data, target_values)
                
                if found:
                    print(f"JSON {filename}:")
                    print("\nÜberprüfung der Regeln:")
                    process_regeln(found, regeln)
                    print("\n" + "-"*40 + "\n")
                else:
                    print(f"JSON {filename} - Keine Zielwerte gefunden.\n")
                    
            except json.JSONDecodeError:
                print(f"{filename} konnte nicht gelesen werden: Ungültiges JSON-Format.")