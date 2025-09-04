from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.equipment import Equipment, Application, ObsolescenceInfo
from datetime import datetime

equipment_bp = Blueprint('equipment', __name__)

@equipment_bp.route('/equipment', methods=['GET'])
def get_all_equipment():
    """Récupère tous les équipements"""
    try:
        equipment_list = Equipment.query.all()
        return jsonify([eq.to_dict() for eq in equipment_list]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/equipment/<int:equipment_id>', methods=['GET'])
def get_equipment(equipment_id):
    """Récupère un équipement spécifique"""
    try:
        equipment = Equipment.query.get_or_404(equipment_id)
        return jsonify(equipment.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/equipment', methods=['POST'])
def create_equipment():
    """Crée un nouvel équipement"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['name', 'equipment_type', 'location']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        # Conversion des dates
        acquisition_date = None
        warranty_end_date = None
        
        if 'acquisition_date' in data and data['acquisition_date']:
            acquisition_date = datetime.strptime(data['acquisition_date'], '%Y-%m-%d').date()
        
        if 'warranty_end_date' in data and data['warranty_end_date']:
            warranty_end_date = datetime.strptime(data['warranty_end_date'], '%Y-%m-%d').date()
        
        # Création de l'équipement
        equipment = Equipment(
            name=data['name'],
            equipment_type=data['equipment_type'],
            location=data['location'],
            ip_address=data.get('ip_address'),
            os_name=data.get('os_name'),
            os_version=data.get('os_version'),
            acquisition_date=acquisition_date,
            warranty_end_date=warranty_end_date,
            status=data.get('status', 'Active')
        )
        
        db.session.add(equipment)
        db.session.commit()
        
        # Ajout des applications si présentes
        if 'applications' in data:
            for app_data in data['applications']:
                application = Application(
                    name=app_data['name'],
                    version=app_data['version'],
                    equipment_id=equipment.id
                )
                db.session.add(application)
        
        db.session.commit()
        
        return jsonify(equipment.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/equipment/<int:equipment_id>', methods=['PUT'])
def update_equipment(equipment_id):
    """Met à jour un équipement"""
    try:
        equipment = Equipment.query.get_or_404(equipment_id)
        data = request.get_json()
        
        # Mise à jour des champs
        if 'name' in data:
            equipment.name = data['name']
        if 'equipment_type' in data:
            equipment.equipment_type = data['equipment_type']
        if 'location' in data:
            equipment.location = data['location']
        if 'ip_address' in data:
            equipment.ip_address = data['ip_address']
        if 'os_name' in data:
            equipment.os_name = data['os_name']
        if 'os_version' in data:
            equipment.os_version = data['os_version']
        if 'status' in data:
            equipment.status = data['status']
        
        # Mise à jour des dates
        if 'acquisition_date' in data and data['acquisition_date']:
            equipment.acquisition_date = datetime.strptime(data['acquisition_date'], '%Y-%m-%d').date()
        
        if 'warranty_end_date' in data and data['warranty_end_date']:
            equipment.warranty_end_date = datetime.strptime(data['warranty_end_date'], '%Y-%m-%d').date()
        
        equipment.updated_at = datetime.utcnow()
        
        # Mise à jour des applications
        if 'applications' in data:
            # Supprimer les anciennes applications
            Application.query.filter_by(equipment_id=equipment.id).delete()
            
            # Ajouter les nouvelles applications
            for app_data in data['applications']:
                application = Application(
                    name=app_data['name'],
                    version=app_data['version'],
                    equipment_id=equipment.id
                )
                db.session.add(application)
        
        db.session.commit()
        
        return jsonify(equipment.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/equipment/<int:equipment_id>', methods=['DELETE'])
def delete_equipment(equipment_id):
    """Supprime un équipement"""
    try:
        equipment = Equipment.query.get_or_404(equipment_id)
        db.session.delete(equipment)
        db.session.commit()
        
        return jsonify({'message': 'Équipement supprimé avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/equipment/stats', methods=['GET'])
def get_equipment_stats():
    """Récupère les statistiques des équipements"""
    try:
        # Statistiques par type
        type_stats = db.session.query(
            Equipment.equipment_type,
            db.func.count(Equipment.id).label('count')
        ).group_by(Equipment.equipment_type).all()
        
        # Statistiques par localisation
        location_stats = db.session.query(
            Equipment.location,
            db.func.count(Equipment.id).label('count')
        ).group_by(Equipment.location).all()
        
        # Statistiques par statut
        status_stats = db.session.query(
            Equipment.status,
            db.func.count(Equipment.id).label('count')
        ).group_by(Equipment.status).all()
        
        # Total des équipements
        total_equipment = Equipment.query.count()
        
        return jsonify({
            'total_equipment': total_equipment,
            'by_type': [{'type': stat[0], 'count': stat[1]} for stat in type_stats],
            'by_location': [{'location': stat[0], 'count': stat[1]} for stat in location_stats],
            'by_status': [{'status': stat[0], 'count': stat[1]} for stat in status_stats]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

