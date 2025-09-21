#!/usr/bin/env python3
"""
Script pour créer un utilisateur admin
"""
from src.main import app
from src.models.user import User, db

def create_admin_user():
    """Crée un utilisateur admin s'il n'existe pas"""
    with app.app_context():
        # Vérifier si l'utilisateur admin existe déjà
        if User.query.filter_by(username='admin').first():
            print("Utilisateur admin existe déjà")
            return
        
        # Créer l'utilisateur admin
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        print("Utilisateur admin créé avec succès")

if __name__ == "__main__":
    create_admin_user()

