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

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(equipment_bp, url_prefix='/api')
app.register_blueprint(obsolescence_bp, url_prefix='/api')

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
        
        # Import automatique des données Excel
        try:
            from auto_import import auto_import_excel_data
            auto_import_excel_data()
        except Exception as e:
            print(f"Erreur lors de l'import automatique: {e}")
    else:
        print("Base de données existante trouvée")
        # Forcer l'import des vraies données même si la base existe
        try:
            from auto_import import auto_import_excel_data
            auto_import_excel_data()
        except Exception as e:
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
    app.run(host='0.0.0.0', port=5000, debug=True)
