from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.equipment import Equipment, Application, ObsolescenceInfo
from datetime import datetime

equipment_bp = Blueprint('equipment', __name__)

@equipment_bp.route('/equipment', methods=['GET'])
@equipment_bp.route('/equipments', methods=['GET'])
@equipment_bp.route('/equipment/list', methods=['GET'])
@equipment_bp.route('/equipments/list', methods=['GET'])
def get_all_equipment():
    """Récupère les équipements avec recherche, filtres et pagination facultatifs"""
    try:
        # Paramètres
        search = request.args.get('search') or request.args.get('q') or ''
        type_filter = request.args.get('type') or request.args.get('equipment_type') or ''
        status_filter = request.args.get('status') or ''
        location_filter = request.args.get('location') or ''
        paginated = request.args.get('paginated', '').lower() in ['1', 'true', 'yes']
        page = request.args.get('page', type=int)
        page_size = request.args.get('pageSize', type=int) or request.args.get('limit', type=int)

        # Normalisation des valeurs front -> base
        status_map = {
            'actif': 'Active',
            'active': 'Active',
            'obsolète': 'Obsolete',
            'obsolete': 'Obsolete',
            'en stock': 'In Stock',
            'en_stock': 'In Stock',
            'stock': 'In Stock'
        }
        if status_filter:
            key = status_filter.strip().lower()
            if key in status_map:
                status_filter = status_map[key]
            if key in ['tous', 'toutes', 'tous les statuts', 'toutes les statuts', 'all']:
                status_filter = ''

        query = Equipment.query

        # Filtres
        if location_filter and location_filter not in ['all', 'toutes', 'toutes les localisations']:
            query = query.filter(Equipment.location == location_filter)
        if type_filter and type_filter not in ['all', 'tous', 'tous les types']:
            query = query.filter(Equipment.equipment_type == type_filter)
        if status_filter and status_filter.lower() != 'all':
            query = query.filter(Equipment.status == status_filter)
        if search:
            like = f"%{search}%"
            query = query.filter(
                db.or_(
                    Equipment.name.ilike(like),
                    Equipment.location.ilike(like),
                    Equipment.ip_address.ilike(like),
                    Equipment.os_name.ilike(like),
                    Equipment.brand.ilike(like),
                    Equipment.model_number.ilike(like)
                )
            )

        # Tri (récents d'abord)
        query = query.order_by(Equipment.created_at.desc())

        total = query.count()
        print(f"[API] GET /equipment -> total={total} search='{search}' type='{type_filter}' status='{status_filter}' location='{location_filter}'")

        # Pagination
        if paginated or (page is not None and page_size):
            page = page or 1
            page_size = page_size or 20
            items = query.offset((page - 1) * page_size).limit(page_size).all()
            payload = {
                'items': [eq.to_dict() for eq in items],
                'total': total,
                'page': page,
                'pageSize': page_size
            }
            # Alias pour compatibilité
            payload['data'] = payload['items']
            payload['results'] = payload['items']
            payload['count'] = payload['total']
            payload['totalCount'] = payload['total']
            return jsonify(payload), 200

        # Sans pagination: renvoyer la liste brute
        equipment_list = query.all()
        return jsonify([eq.to_dict() for eq in equipment_list]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/equipment/<int:equipment_id>', methods=['GET'])
@equipment_bp.route('/equipments/<int:equipment_id>', methods=['GET'])
def get_equipment(equipment_id):
    """Récupère un équipement spécifique"""
    try:
        equipment = Equipment.query.get_or_404(equipment_id)
        return jsonify(equipment.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/equipment', methods=['POST'])
@equipment_bp.route('/equipments', methods=['POST'])
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
@equipment_bp.route('/equipments/<int:equipment_id>', methods=['PUT'])
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
@equipment_bp.route('/equipments/<int:equipment_id>', methods=['DELETE'])
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
@equipment_bp.route('/equipment/summary', methods=['GET'])
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
@equipment_bp.route('/equipment-filters/locations', methods=['GET'])
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
@equipment_bp.route('/equipments/import', methods=['POST'])
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
        
        # Lire le fichier Excel avec notre module personnalisé
        from src.excel_reader import read_excel_file
        
        try:
            # Lire le fichier Excel en mémoire
            excel_data = read_excel_file(file.read())
            columns = excel_data['columns']
            data_rows = excel_data['data']
        except Exception as e:
            return jsonify({'error': f'Erreur lors de la lecture du fichier Excel: {str(e)}'}), 400
        
        # Normaliser les noms de colonnes
        columns = [str(col).strip() if col is not None else '' for col in columns]

        # Importer les fonctions utilitaires
        from src.excel_reader import is_empty_value, convert_boolean_field, clean_string_field

        # Variantes d'en-têtes possibles (accents, apostrophes, espaces)
        header_map = {
            'name': ['Nom PC', 'Nom Pc', 'Nom pc', 'Nom ordinateur', 'Nom machine'],
            'location': ['Salle', 'Localisation', 'Emplacement', 'Lieu'],
            'description_alias': ['Description  (Alias)', 'Description (Alias)', 'Alias', 'Description'],
            'brand': ['Marque', 'Fabricant'],
            'model_number': ['N° modèle', 'No modèle', 'N° modele', 'No modele', 'Modèle', 'Modele', 'Référence modèle', 'Reference modele'],
            'os_name': ["Système d'exploitation PC", 'Système d’exploitation PC', 'Systeme dexploitation PC', 'OS', 'Système', 'Systeme'],
            'ip_address': ['Adresse IP', 'Adresse Ip', 'IP', 'Ip'],
            'network_connected': ['Connecté au réseau O/N', 'Connecte au reseau O/N', 'Connecte au réseau O/N', 'Connecté au reseau O/N'],
            'rls_network_saved': ['Sauvegardé sur réseau RLS O/N', 'Sauvegarde sur reseau RLS O/N', 'Sauvegarde RLS O/N'],
            'to_be_backed_up': ['A sauvegarder O/N', 'À sauvegarder O/N', 'ASauvegarder O/N'],
            'supplier': ['Fournisseur matériel', 'Fournisseur materiel', 'Fournisseur']
        }

        # Vérifier la présence des colonnes obligatoires via synonymes
        def has_any(keys, cols):
            ks = set(keys)
            return any(c in ks for c in cols)
        has_name = has_any(columns, header_map['name'])
        has_location = has_any(columns, header_map['location'])
        if not (has_name and has_location):
            return jsonify({
                'error': "Colonnes d'en-têtes introuvables. Assurez-vous que le fichier contient les colonnes pour 'Nom PC' et 'Salle' (variantes acceptées).",
                'available_columns': columns
            }), 400

        imported_count = 0
        errors = []

        # Préparer un utilitaire pour récupérer des valeurs avec variantes d'en-têtes
        def first_value(row_obj, keys):
            for k in keys:
                v = row_obj.get(k, '')
                v = clean_string_field(v)
                if v is not None and v != '':
                    return v
            return None

        for index, row in enumerate(data_rows):
            try:
                equipment_name = first_value(row, header_map['name'])
                location = first_value(row, header_map['location'])

                if not equipment_name:
                    errors.append(f'Ligne {index + 2}: Nom PC manquant')
                    continue
                if not location:
                    errors.append(f'Ligne {index + 2}: Salle manquante')
                    continue

                # Déterminer le type d'équipement basé sur le nom
                equipment_type = 'PC'
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

                equipment = Equipment(
                    name=equipment_name,
                    equipment_type=equipment_type,
                    location=location,
                    description_alias=first_value(row, header_map['description_alias']),
                    brand=first_value(row, header_map['brand']),
                    model_number=first_value(row, header_map['model_number']),
                    os_name=first_value(row, header_map['os_name']),
                    ip_address=first_value(row, header_map['ip_address']),
                    network_connected=convert_boolean_field(first_value(row, header_map['network_connected'])),
                    rls_network_saved=convert_boolean_field(first_value(row, header_map['rls_network_saved'])),
                    to_be_backed_up=convert_boolean_field(first_value(row, header_map['to_be_backed_up'])),
                    supplier=first_value(row, header_map['supplier']),
                    status='Active'
                )

                db.session.add(equipment)
                db.session.flush()

                app_name = clean_string_field(row.get('Application', '')) or clean_string_field(row.get('Logiciel', ''))
                app_version = clean_string_field(row.get('Version', ''))
                if app_name:
                    application = Application(
                        name=app_name,
                        version=app_version if app_version else 'Non spécifiée',
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
            'total_rows': len(data_rows),
            'errors': errors[:10],  # Limiter à 10 erreurs pour l'affichage
            'error_count': len(errors)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de l\'import: {str(e)}'}), 500

@equipment_bp.route('/equipment/export-template', methods=['GET'])
@equipment_bp.route('/equipments/export-template', methods=['GET'])
def export_template():
    """Exporte un modèle Excel pour l'import"""
    try:
        import pandas as pd
        import io
        from flask import send_file
        
        # Créer un DataFrame avec les colonnes attendues selon le fichier Excel fourni
        template_data = {
            'Salle': ['PDB-Chromato', 'PDB-GAZ', 'PDB-Spectro'],
            'Description  (Alias)': ['Poste de travail principal', 'Serveur de base de données', 'Machine d\'analyse'],
            'Marque': ['Dell', 'HP', 'Agilent'],
            'Nom PC': ['PC-CHROMATO-01', 'SRV-GAZ-01', 'LAB-SPECTRO-01'],
            'N° modèle': ['OptiPlex 7090', 'ProLiant DL380', 'Model 1260'],
            'Système d\'exploitation PC': ['Windows 10 Pro', 'Ubuntu 20.04 LTS', 'Windows 7 Pro'],
            'Application': ['ChemStation', 'MySQL', 'OpenLAB CDS'],
            'Version': ['C.01.10', '8.0', '2.7'],
            'Connecté au réseau O/N': ['O', 'O', 'N'],
            'Sauvegardé sur réseau RLS O/N': ['O', 'O', 'N'],
            'Adresse IP': ['192.168.1.10', '192.168.1.20', ''],
            'A sauvegarder O/N': ['O', 'O', 'N'],
            'Fournisseur matériel': ['Dell Technologies', 'HP Inc.', 'Agilent Technologies']
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
                    '2. Colonnes obligatoires: Salle, Nom PC',
                    '3. Le type d\'équipement est déterminé automatiquement selon le nom',
                    '4. Les noms d\'équipements doivent être uniques',
                    '5. Pour les colonnes O/N: utilisez O (Oui) ou N (Non)',
                    '6. Formats supportés: .xlsx, .xls',
                    '7. Colonnes disponibles:',
                    '   - Salle (obligatoire): Localisation de l\'équipement',
                    '   - Description (Alias): Description ou alias de l\'équipement',
                    '   - Marque: Marque du fabricant',
                    '   - Nom PC (obligatoire): Nom unique de l\'équipement',
                    '   - N° modèle: Numéro de modèle',
                    '   - Système d\'exploitation PC: OS installé',
                    '   - Application: Application principale installée',
                    '   - Version: Version de l\'application',
                    '   - Connecté au réseau O/N: Connexion réseau (O/N)',
                    '   - Sauvegardé sur réseau RLS O/N: Sauvegarde RLS (O/N)',
                    '   - Adresse IP: Adresse IP de l\'équipement',
                    '   - A sauvegarder O/N: Nécessite sauvegarde (O/N)',
                    '   - Fournisseur matériel: Nom du fournisseur'
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
