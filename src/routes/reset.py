from flask import Blueprint, jsonify
from src.models.equipment import Equipment, Application, db

reset_bp = Blueprint('reset', __name__)

@reset_bp.route('/reset-data', methods=['POST'])
def reset_data():
    """
    Supprime toutes les données d'équipements et d'applications
    """
    try:
        # Supprimer toutes les applications
        Application.query.delete()
        
        # Supprimer tous les équipements
        Equipment.query.delete()
        
        # Valider les changements
        db.session.commit()
        
        return jsonify({
            'message': 'Toutes les données ont été supprimées avec succès',
            'status': 'success'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': f'Erreur lors de la suppression des données: {str(e)}',
            'status': 'error'
        }), 500
