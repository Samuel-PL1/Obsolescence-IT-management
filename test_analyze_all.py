#!/usr/bin/env python3
"""Script de test pour l'analyse complète d'obsolescence"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
from src.database import db
from src.models.equipment import Equipment
from src.models.obsolescence import ObsolescenceInfo
from src.services.obsolescence_analyzer import ObsolescenceAnalyzer
from src.routes.obsolescence_enhanced import extract_os_from_equipments, extract_applications_from_equipments, save_obsolescence_results

# Configuration Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    print("=== ANALYSE COMPLÈTE D'OBSOLESCENCE ===\n")
    
    # Récupérer tous les équipements
    equipments = Equipment.query.all()
    print(f"✅ {len(equipments)} équipements trouvés\n")
    
    # Analyser les OS
    print("📊 Analyse des systèmes d'exploitation...")
    os_data = extract_os_from_equipments(equipments)
    print(f"   {len(os_data)} OS uniques détectés")
    
    analyzer = ObsolescenceAnalyzer()
    os_results = analyzer.analyze_os_obsolescence(os_data)
    print(f"   {len(os_results)} OS analysés avec succès\n")
    
    # Analyser les applications
    print("📊 Analyse des applications...")
    apps_data = extract_applications_from_equipments(equipments)
    print(f"   {len(apps_data)} applications uniques détectées")
    
    # Pour le test, on n'analyse que les 5 premières applications pour éviter les coûts IA
    apps_data_sample = apps_data[:5]
    app_results = analyzer.analyze_applications_obsolescence(apps_data_sample)
    print(f"   {len(app_results)} applications analysées (échantillon)\n")
    
    # Sauvegarder les résultats
    print("💾 Sauvegarde des résultats...")
    all_results = os_results + app_results
    save_obsolescence_results(all_results)
    print(f"   {len(all_results)} produits sauvegardés\n")
    
    # Afficher un résumé
    print("=== RÉSUMÉ ===")
    for result in all_results[:10]:  # Afficher les 10 premiers
        status_emoji = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(result['status'], "⚪")
        print(f"{status_emoji} {result['name']} - {result['status']} - EOL: {result.get('eol_date', 'N/A')}")
    
    if len(all_results) > 10:
        print(f"... et {len(all_results) - 10} autres produits")
    
    print("\n✅ Analyse terminée avec succès!")
