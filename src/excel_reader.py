#!/usr/bin/env python3
"""
Module de lecture Excel sans pandas pour éviter les conflits de dépendances
"""
import openpyxl
from io import BytesIO

def read_excel_file(file_content):
    """
    Lit un fichier Excel et retourne les données sous forme de dictionnaire
    
    Args:
        file_content: Contenu du fichier Excel en bytes
        
    Returns:
        dict: Données avec colonnes et lignes
    """
    try:
        # Charger le workbook depuis les bytes
        workbook = openpyxl.load_workbook(BytesIO(file_content))
        
        # Prendre la première feuille
        worksheet = workbook.active
        
        # Lire les en-têtes (première ligne)
        headers = []
        for cell in worksheet[1]:
            headers.append(cell.value if cell.value is not None else "")
        
        # Lire les données
        data = []
        for row in worksheet.iter_rows(min_row=2, values_only=True):
            row_data = {}
            for i, value in enumerate(row):
                if i < len(headers):
                    # Convertir None en chaîne vide
                    row_data[headers[i]] = value if value is not None else ""
            data.append(row_data)
        
        return {
            'columns': headers,
            'data': data,
            'total_rows': len(data)
        }
        
    except Exception as e:
        raise Exception(f"Erreur lors de la lecture du fichier Excel: {str(e)}")

def is_empty_value(value):
    """Vérifie si une valeur est vide ou nulle"""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if str(value).lower() in ['nan', 'none', 'null']:
        return True
    return False

def convert_boolean_field(value):
    """Convertit une valeur O/N en boolean"""
    if is_empty_value(value):
        return None
    
    value_str = str(value).strip().upper()
    if value_str.startswith('O'):
        return True
    elif value_str.startswith('N'):
        return False
    else:
        return None

def clean_string_field(value):
    """Nettoie une valeur string"""
    if is_empty_value(value):
        return None
    return str(value).strip()
