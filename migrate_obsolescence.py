#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.database import db
from src.models.obsolescence import ObsolescenceInfo
from src.models.user import User
from src.models.equipment import Equipment
from flask import Flask

# Configuration Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # Créer la nouvelle table obsolescence_info
    db.create_all()
    print("Table obsolescence_info créée avec succès")
