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
    """Récupère les statistiques des équipements avec filtrage optionnel par localisation"""
    try:
        # Récupérer le paramètre de filtre de localisation
        location_filter = request.args.get('location')
        
        # Base query
        base_query = Equipment.query
        if location_filter and location_filter != 'all':
            base_query = base_query.filter(Equipment.location == location_filter)
        
        # Statistiques par type
        type_stats = db.session.query(
            Equipment.equipment_type,
            db.func.count(Equipment.id).label('count')
        )
        if location_filter and location_filter != 'all':
            type_stats = type_stats.filter(Equipment.location == location_filter)
        type_stats = type_stats.group_by(Equipment.equipment_type).all()
        
        # Statistiques par statut
        status_stats = db.session.query(
            Equipment.status,
            db.func.count(Equipment.id).label('count')
        )
        if location_filter and location_filter != 'all':
            status_stats = status_stats.filter(Equipment.location == location_filter)
        status_stats = status_stats.group_by(Equipment.status).all()
        
        # Statistiques par localisation (toujours toutes les localisations)
        location_stats = db.session.query(
            Equipment.location,
            db.func.count(Equipment.id).label('count')
        ).group_by(Equipment.location).all()
        
        # Total des équipements (avec filtre)
        total_equipment = base_query.count()
        active_equipment = base_query.filter_by(status='Active').count()
        obsolete_equipment = base_query.filter_by(status='Obsolete').count()
        
        return jsonify({
            'total_equipment': total_equipment,
            'active_equipment': active_equipment,
            'obsolete_equipment': obsolete_equipment,
            'by_type': [{'type': stat[0], 'count': stat[1]} for stat in type_stats],
            'by_status': [{'status': stat[0], 'count': stat[1]} for stat in status_stats],
            'by_location': [{'location': stat[0], 'count': stat[1]} for stat in location_stats],
            'applied_filter': location_filter
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/equipment/locations', methods=['GET'])
def get_locations():
    """Récupère toutes les localisations uniques"""
    try:
        locations = db.session.query(Equipment.location).distinct().filter(
            Equipment.location.isnot(None),
            Equipment.location != ''
        ).all()
        
        location_list = [loc[0] for loc in locations]
        return jsonify({'locations': sorted(location_list)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@equipment_bp.route('/equipment/import', methods=['POST'])
def import_equipment():
    """Importe des équipements depuis un fichier Excel"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'Format de fichier non supporté. Utilisez .xlsx ou .xls'}), 400
        
        # Lire le fichier Excel
        import pandas as pd
        import io
        
        try:
            # Lire le fichier Excel en mémoire
            df = pd.read_excel(io.BytesIO(file.read()))
        except Exception as e:
            return jsonify({'error': f'Erreur lors de la lecture du fichier Excel: {str(e)}'}), 400
        
        # Mapping des colonnes selon l'image fournie
        column_mapping = {
            'Salle': 'location',
            'Description (Alias)': 'name', 
            'Nom PC': 'name',
            'Système d\'exploitation PC': 'os_name',
            'Application': 'application_name',
            'Version': 'application_version',
            'Fournisseur matériel': 'manufacturer'
        }
        
        # Normaliser les noms de colonnes
        df.columns = df.columns.str.strip()
        
        # Vérifier les colonnes requises
        required_columns = ['Salle', 'Nom PC']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({
                'error': f'Colonnes manquantes: {", ".join(missing_columns)}',
                'available_columns': list(df.columns)
            }), 400
        
        imported_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Extraire les données de base
                equipment_name = str(row.get('Nom PC', '')).strip()
                location = str(row.get('Salle', '')).strip()
                
                if not equipment_name or equipment_name.lower() in ['nan', 'none', '']:
                    errors.append(f'Ligne {index + 2}: Nom PC manquant')
                    continue
                
                if not location or location.lower() in ['nan', 'none', '']:
                    errors.append(f'Ligne {index + 2}: Salle manquante')
                    continue
                
                # Déterminer le type d'équipement basé sur le nom
                equipment_type = 'PC'  # Par défaut
                name_lower = equipment_name.lower()
                if 'srv' in name_lower or 'server' in name_lower:
                    equipment_type = 'Serveur'
                elif 'imp' in name_lower or 'print' in name_lower:
                    equipment_type = 'Imprimante'
                elif 'sw' in name_lower or 'switch' in name_lower:
                    equipment_type = 'Switch'
                elif 'lab' in name_lower or 'machine' in name_lower:
                    equipment_type = 'Machine laboratoire'
                
                # Vérifier si l'équipement existe déjà
                existing_equipment = Equipment.query.filter_by(name=equipment_name).first()
                if existing_equipment:
                    errors.append(f'Ligne {index + 2}: Équipement {equipment_name} existe déjà')
                    continue
                
                # Créer l'équipement
                equipment = Equipment(
                    name=equipment_name,
                    equipment_type=equipment_type,
                    location=location,
                    os_name=str(row.get('Système d\'exploitation PC', '')).strip() or None,
                    status='Active'
                )
                
                db.session.add(equipment)
                db.session.flush()  # Pour obtenir l'ID
                
                # Ajouter l'application si présente
                app_name = str(row.get('Application', '')).strip()
                app_version = str(row.get('Version', '')).strip()
                
                if app_name and app_name.lower() not in ['nan', 'none', '']:
                    application = Application(
                        name=app_name,
                        version=app_version if app_version.lower() not in ['nan', 'none', ''] else 'Non spécifiée',
                        equipment_id=equipment.id
                    )
                    db.session.add(application)
                
                imported_count += 1
                
            except Exception as e:
                errors.append(f'Ligne {index + 2}: {str(e)}')
                continue
        
        # Sauvegarder les changements
        if imported_count > 0:
            db.session.commit()
        else:
            db.session.rollback()
        
        return jsonify({
            'message': f'{imported_count} équipements importés avec succès',
            'imported_count': imported_count,
            'total_rows': len(df),
            'errors': errors[:10],  # Limiter à 10 erreurs pour l'affichage
            'error_count': len(errors)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de l\'import: {str(e)}'}), 500

@equipment_bp.route('/equipment/export-template', methods=['GET'])
def export_template():
    """Exporte un modèle Excel pour l'import"""
    try:
        import pandas as pd
        import io
        from flask import send_file
        
        # Créer un DataFrame avec les colonnes attendues
        template_data = {
            'Salle': ['Siège Paris - Bureau 101', 'Agence Lyon - Salle 205'],
            'Description (Alias)': ['Poste de travail principal', 'Serveur de base de données'],
            'Nom PC': ['PC-001', 'SRV-001'],
            'Système d\'exploitation PC': ['Windows 10 Pro', 'Ubuntu 20.04 LTS'],
            'Application': ['Microsoft Office', 'MySQL'],
            'Version': ['2019', '8.0'],
            'Fournisseur matériel': ['Dell', 'HP']
        }
        
        df = pd.DataFrame(template_data)
        
        # Créer un fichier Excel en mémoire
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Équipements', index=False)
            
            # Ajouter une feuille d'instructions
            instructions = pd.DataFrame({
                'Instructions d\'import': [
                    '1. Remplissez les colonnes selon vos données',
                    '2. Salle et Nom PC sont obligatoires',
                    '3. Le type d\'équipement est déterminé automatiquement',
                    '4. Les noms doivent être uniques',
                    '5. Formats supportés: .xlsx, .xls'
                ]
            })
            instructions.to_excel(writer, sheet_name='Instructions', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='modele_import_equipements.xlsx'
        )
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la génération du modèle: {str(e)}'}), 500

