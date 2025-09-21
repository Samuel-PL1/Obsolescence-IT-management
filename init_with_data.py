#!/usr/bin/env python3
"""
Script pour initialiser la base de données avec les données réelles importées
"""
import os
import shutil
from models.equipment import db
from main import app

def init_database_with_real_data():
    """Initialise la base de données avec les données réelles"""
    
    # Chemin vers la base de données avec les vraies données
    source_db = "/home/ubuntu/it-obsolescence-manager-manager-backend/app_with_real_data.db"
    target_db = "/home/ubuntu/it-obsolescence-manager-manager-backend/src/database/app.db"
    
    # Créer le répertoire database s'il n'existe pas
    os.makedirs(os.path.dirname(target_db), exist_ok=True)
    
    # Copier la base de données avec les vraies données
    if os.path.exists(source_db):
        shutil.copy2(source_db, target_db)
        print(f"Base de données copiée de {source_db} vers {target_db}")
    else:
        print(f"Fichier source {source_db} non trouvé, création d'une nouvelle base")
        with app.app_context():
            db.create_all()
            print("Nouvelle base de données créée")

if __name__ == "__main__":
    init_database_with_real_data()
