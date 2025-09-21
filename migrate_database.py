#!/usr/bin/env python3
"""
Script de migration pour ajouter les nouveaux champs du template Excel
à la table equipment existante.
"""

from src.models.user import db
from src.main import app
from sqlalchemy import text

def migrate_database():
    """Ajoute les nouveaux champs à la table equipment"""
    
    with app.app_context():
        try:
            # Vérifier si les colonnes existent déjà
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('equipment')]
            
            # Liste des nouvelles colonnes à ajouter
            new_columns = [
                ('description_alias', 'VARCHAR(200)'),
                ('brand', 'VARCHAR(100)'),
                ('model_number', 'VARCHAR(100)'),
                ('network_connected', 'BOOLEAN'),
                ('rls_network_saved', 'BOOLEAN'),
                ('to_be_backed_up', 'BOOLEAN'),
                ('supplier', 'VARCHAR(100)')
            ]
            
            print("Migration de la base de données...")
            print(f"Colonnes existantes: {existing_columns}")
            
            # Ajouter chaque nouvelle colonne si elle n'existe pas
            for column_name, column_type in new_columns:
                if column_name not in existing_columns:
                    print(f"Ajout de la colonne: {column_name}")
                    sql = f"ALTER TABLE equipment ADD COLUMN {column_name} {column_type}"
                    db.session.execute(text(sql))
                else:
                    print(f"Colonne {column_name} existe déjà")
            
            # Valider les changements
            db.session.commit()
            
            # Vérifier les nouvelles colonnes
            inspector = inspect(db.engine)
            updated_columns = [col['name'] for col in inspector.get_columns('equipment')]
            print(f"\nColonnes après migration: {updated_columns}")
            
            print("\nMigration terminée avec succès!")
            
        except Exception as e:
            print(f"Erreur lors de la migration: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    migrate_database()
