import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.equipment import equipment_bp
from src.routes.obsolescence import obsolescence_bp
from src.routes.reset import reset_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(equipment_bp, url_prefix='/api')
app.register_blueprint(obsolescence_bp, url_prefix='/api')
app.register_blueprint(reset_bp, url_prefix='/api')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    # Créer les tables seulement si elles n'existent pas déjà
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
    if not os.path.exists(db_path):
        # Créer le répertoire database s'il n'existe pas
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        db.create_all()
        print("Base de données créée")
    else:
        print("Base de données existante trouvée")

    # Import automatique des données d'inventaire si la base est vide
    try:
        from src.models.equipment import Equipment, Application
        from src.excel_reader import read_excel_file, clean_string_field, convert_boolean_field

        print(f"Nombre d'équipements au démarrage: {Equipment.query.count()}")
        if Equipment.query.count() == 0:
            excel_candidates = [
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'inventaireIT.xlsx'),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_import.xlsx')
            ]
            excel_path = next((p for p in excel_candidates if os.path.exists(p)), None)

            if excel_path:
                with open(excel_path, 'rb') as f:
                    excel_data = read_excel_file(f.read())
                data_rows = excel_data['data']

                imported = 0
                for row in data_rows:
                    name = clean_string_field(row.get('Nom PC')) or clean_string_field(row.get('Nom Pc')) or clean_string_field(row.get('Nom pc')) or clean_string_field(row.get('Nom ordinateur')) or clean_string_field(row.get('Nom machine'))
                    location = clean_string_field(row.get('Salle')) or clean_string_field(row.get('Localisation')) or clean_string_field(row.get('Emplacement')) or clean_string_field(row.get('Lieu'))
                    if not name or not location:
                        continue

                    # Déterminer le type d'équipement
                    equipment_type = 'PC'
                    lower = name.lower()
                    if 'srv' in lower or 'server' in lower:
                        equipment_type = 'Serveur'
                    elif 'imp' in lower or 'print' in lower:
                        equipment_type = 'Imprimante'
                    elif 'sw' in lower or 'switch' in lower:
                        equipment_type = 'Switch'
                    elif 'lab' in lower or 'machine' in lower:
                        equipment_type = 'Machine laboratoire'

                    eq = Equipment(
                        name=name,
                        equipment_type=equipment_type,
                        location=location,
                        status='Active'
                    )

                    # Champs optionnels
                    eq.description_alias = clean_string_field(row.get('Description  (Alias)')) or clean_string_field(row.get('Description (Alias)')) or clean_string_field(row.get('Alias')) or clean_string_field(row.get('Description'))
                    eq.brand = clean_string_field(row.get('Marque')) or clean_string_field(row.get('Fabricant'))
                    eq.model_number = clean_string_field(row.get('N° modèle')) or clean_string_field(row.get('No modèle')) or clean_string_field(row.get('N° modele')) or clean_string_field(row.get('No modele')) or clean_string_field(row.get('Modèle')) or clean_string_field(row.get('Modele')) or clean_string_field(row.get('Référence modèle')) or clean_string_field(row.get('Reference modele'))
                    eq.os_name = clean_string_field(row.get("Système d'exploitation PC")) or clean_string_field(row.get('Système d’exploitation PC')) or clean_string_field(row.get('Systeme dexploitation PC')) or clean_string_field(row.get('OS')) or clean_string_field(row.get('Système')) or clean_string_field(row.get('Systeme'))
                    eq.ip_address = clean_string_field(row.get('Adresse IP')) or clean_string_field(row.get('Adresse Ip')) or clean_string_field(row.get('IP')) or clean_string_field(row.get('Ip'))
                    eq.network_connected = convert_boolean_field(row.get('Connecté au réseau O/N')) or convert_boolean_field(row.get('Connecte au reseau O/N')) or convert_boolean_field(row.get('Connecte au réseau O/N')) or convert_boolean_field(row.get('Connecté au reseau O/N'))
                    eq.rls_network_saved = convert_boolean_field(row.get('Sauvegardé sur réseau RLS O/N')) or convert_boolean_field(row.get('Sauvegarde sur reseau RLS O/N')) or convert_boolean_field(row.get('Sauvegarde RLS O/N'))
                    eq.to_be_backed_up = convert_boolean_field(row.get('A sauvegarder O/N')) or convert_boolean_field(row.get('À sauvegarder O/N')) or convert_boolean_field(row.get('ASauvegarder O/N'))
                    eq.supplier = clean_string_field(row.get('Fournisseur matériel')) or clean_string_field(row.get('Fournisseur materiel')) or clean_string_field(row.get('Fournisseur'))

                    db.session.add(eq)
                    db.session.flush()

                    app_name = clean_string_field(row.get('Application')) or clean_string_field(row.get('Logiciel'))
                    app_version = clean_string_field(row.get('Version'))
                    if app_name:
                        db.session.add(Application(name=app_name, version=app_version if app_version else 'Non spécifiée', equipment_id=eq.id))

                    imported += 1

                db.session.commit()
                print(f"Import automatique effectué depuis {os.path.basename(excel_path)}: {imported} équipements importés")
            else:
                print("Aucun fichier d'inventaire trouvé pour l'import automatique")
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de l'import automatique: {e}")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
