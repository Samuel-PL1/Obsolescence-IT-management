#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.models.user import db, User
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(os.path.dirname(__file__), "src", "database", "app.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Supprimer l'utilisateur existant s'il existe
    existing_user = User.query.filter_by(username='admin').first()
    if existing_user:
        db.session.delete(existing_user)
        print('Utilisateur admin existant supprimé')
    
    # Créer un nouvel utilisateur admin
    admin = User(username='admin', email='admin@example.com')
    admin.set_password('admin')
    db.session.add(admin)
    db.session.commit()
    print('Utilisateur admin créé avec succès')
    print('Username: admin')
    print('Password: admin')
