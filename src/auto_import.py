#!/usr/bin/env python3
"""
Script d'importation automatique des données Excel au démarrage
"""
import os
import pandas as pd
from models.equipment import Equipment, Application, db

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
        # Lire le fichier Excel
        df = pd.read_excel(excel_file)
        print(f"Lecture du fichier Excel: {len(df)} lignes trouvées")
        
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
        
        for index, row in df.iterrows():
            try:
                # Vérifier les champs obligatoires
                if pd.isna(row.get('Nom PC')) or pd.isna(row.get('Salle')):
                    continue
                
                name = str(row['Nom PC']).strip()
                location = str(row['Salle']).strip()
                
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
                for excel_col, db_field in column_mapping.items():
                    if excel_col in df.columns and not pd.isna(row.get(excel_col)):
                        value = row[excel_col]
                        
                        if db_field in ['network_connected', 'rls_network_saved', 'to_be_backed_up']:
                            # Conversion O/N vers boolean
                            if isinstance(value, str):
                                equipment.__setattr__(db_field, value.upper().startswith('O'))
                        elif db_field not in ['application_name', 'application_version']:
                            equipment.__setattr__(db_field, str(value) if not pd.isna(value) else None)
                
                db.session.add(equipment)
                db.session.flush()  # Pour obtenir l'ID
                
                # Ajouter l'application si présente
                app_name = row.get('Application')
                app_version = row.get('Version')
                if not pd.isna(app_name) and str(app_name).strip():
                    application = Application(
                        name=str(app_name).strip(),
                        version=str(app_version).strip() if not pd.isna(app_version) else None,
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
