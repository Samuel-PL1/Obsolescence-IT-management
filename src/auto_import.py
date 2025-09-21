#!/usr/bin/env python3
"""
Script d'importation automatique des données Excel au démarrage
"""
import os
from models.equipment import Equipment, Application, db
from src.excel_reader import read_excel_file, is_empty_value, convert_boolean_field, clean_string_field

def auto_import_excel_data():
    """Importe automatiquement les données Excel en remplaçant les données existantes"""
    
    # Supprimer toutes les données existantes pour forcer l'import des vraies données
    try:
        # Supprimer les applications d'abord (clé étrangère)
        Application.query.delete()
        # Supprimer les équipements
        Equipment.query.delete()
        db.session.commit()
        print("Données existantes supprimées")
    except Exception as e:
        print(f"Erreur lors de la suppression: {e}")
        db.session.rollback()
    
    # Chemin vers le fichier Excel
    excel_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'inventaireITLabPDB.xlsx')
    
    if not os.path.exists(excel_file):
        print(f"Fichier Excel non trouvé: {excel_file}")
        return
    
    try:
        # Lire le fichier Excel avec notre module personnalisé
        with open(excel_file, 'rb') as f:
            excel_data = read_excel_file(f.read())
        
        data_rows = excel_data['data']
        print(f"Lecture du fichier Excel: {len(data_rows)} lignes trouvées")
        
        # Mapping des colonnes
        column_mapping = {
            'Salle': 'location',
            'Nom PC': 'name',
            'Description  (Alias)': 'description_alias',
            'Marque': 'brand',
            'N° modèle': 'model_number',
            "Système d'exploitation PC": 'os_name',
            'Application': 'application_name',
            'Version': 'application_version',
            'Connecté au réseau O/N': 'network_connected',
            'Sauvegardé sur réseau RLS O/N': 'rls_network_saved',
            'Adresse IP': 'ip_address',
            'A sauvegarder O/N': 'to_be_backed_up',
            'Fournisseur matériel': 'supplier'
        }
        
        imported_count = 0
        
        for index, row in enumerate(data_rows):
            try:
                # Vérifier les champs obligatoires
                name = clean_string_field(row.get('Nom PC'))
                location = clean_string_field(row.get('Salle'))
                
                if not name or not location:
                    continue
                
                # Vérifier si l'équipement existe déjà
                if Equipment.query.filter_by(name=name).first():
                    continue
                
                # Déterminer le type d'équipement
                equipment_type = "PC"  # Par défaut
                name_lower = name.lower()
                if any(keyword in name_lower for keyword in ['srv', 'server']):
                    equipment_type = "Serveur"
                elif any(keyword in name_lower for keyword in ['imp', 'print']):
                    equipment_type = "Imprimante"
                elif any(keyword in name_lower for keyword in ['sw', 'switch']):
                    equipment_type = "Switch"
                elif any(keyword in name_lower for keyword in ['lab', 'machine']):
                    equipment_type = "Machine laboratoire"
                
                # Créer l'équipement
                equipment = Equipment(
                    name=name,
                    equipment_type=equipment_type,
                    location=location,
                    status="Active"
                )
                
                # Ajouter les champs optionnels
                equipment.description_alias = clean_string_field(row.get('Description  (Alias)'))
                equipment.brand = clean_string_field(row.get('Marque'))
                equipment.model_number = clean_string_field(row.get('N° modèle'))
                equipment.os_name = clean_string_field(row.get('Système d\'exploitation PC'))
                equipment.ip_address = clean_string_field(row.get('Adresse IP'))
                equipment.network_connected = convert_boolean_field(row.get('Connecté au réseau O/N'))
                equipment.rls_network_saved = convert_boolean_field(row.get('Sauvegardé sur réseau RLS O/N'))
                equipment.to_be_backed_up = convert_boolean_field(row.get('A sauvegarder O/N'))
                equipment.supplier = clean_string_field(row.get('Fournisseur matériel'))
                
                db.session.add(equipment)
                db.session.flush()  # Pour obtenir l'ID
                
                # Ajouter l'application si présente
                app_name = clean_string_field(row.get('Application'))
                app_version = clean_string_field(row.get('Version'))
                if app_name:
                    application = Application(
                        name=app_name,
                        version=app_version if app_version else 'Non spécifiée',
                        equipment_id=equipment.id
                    )
                    db.session.add(application)
                
                imported_count += 1
                
            except Exception as e:
                print(f"Erreur ligne {index + 2}: {e}")
                continue
        
        db.session.commit()
        print(f"Import automatique terminé: {imported_count} équipements importés")
        
    except Exception as e:
        print(f"Erreur lors de l'import automatique: {e}")
        db.session.rollback()

if __name__ == "__main__":
    auto_import_excel_data()
