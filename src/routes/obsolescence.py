from flask import Blueprint, request, jsonify
import requests
from src.models.user import db
from src.models.equipment import Equipment, Application, ObsolescenceInfo
from datetime import datetime, date
import json

obsolescence_bp = Blueprint('obsolescence', __name__)

@obsolescence_bp.route('/obsolescence/check', methods=['POST'])
def check_obsolescence():
    """Vérifie l'obsolescence pour un produit spécifique"""
    try:
        data = request.get_json()
        product_name = data.get('product_name')
        product_type = data.get('product_type', 'os')  # 'os' ou 'application'
        
        if not product_name:
            return jsonify({'error': 'Le nom du produit est requis'}), 400
        
        # Recherche dans l'API endoflife.date
        obsolescence_data = fetch_obsolescence_data(product_name)
        
        if obsolescence_data:
            # Sauvegarde ou mise à jour des informations d'obsolescence
            save_obsolescence_info(product_name, product_type, obsolescence_data)
            return jsonify(obsolescence_data), 200
        else:
            return jsonify({'message': 'Aucune information d\'obsolescence trouvée'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@obsolescence_bp.route('/obsolescence/update-all', methods=['POST'])
def update_all_obsolescence():
    """Met à jour les informations d'obsolescence pour tous les équipements"""
    try:
        updated_count = 0
        errors = []
        
        # Récupérer tous les OS uniques
        os_list = db.session.query(Equipment.os_name).filter(Equipment.os_name.isnot(None)).distinct().all()
        
        for (os_name,) in os_list:
            try:
                obsolescence_data = fetch_obsolescence_data(os_name.lower())
                if obsolescence_data:
                    save_obsolescence_info(os_name, 'os', obsolescence_data)
                    updated_count += 1
            except Exception as e:
                errors.append(f"Erreur pour {os_name}: {str(e)}")
        
        # Récupérer toutes les applications uniques
        app_list = db.session.query(Application.name).distinct().all()
        
        for (app_name,) in app_list:
            try:
                obsolescence_data = fetch_obsolescence_data(app_name.lower())
                if obsolescence_data:
                    save_obsolescence_info(app_name, 'application', obsolescence_data)
                    updated_count += 1
            except Exception as e:
                errors.append(f"Erreur pour {app_name}: {str(e)}")
        
        return jsonify({
            'message': f'{updated_count} produits mis à jour',
            'errors': errors
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@obsolescence_bp.route('/obsolescence/info', methods=['GET'])
def get_obsolescence_info():
    """Récupère toutes les informations d'obsolescence"""
    try:
        obsolescence_list = ObsolescenceInfo.query.all()
        return jsonify([info.to_dict() for info in obsolescence_list]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@obsolescence_bp.route('/obsolescence/stats', methods=['GET'])
def get_obsolescence_stats():
    """Récupère les statistiques d'obsolescence"""
    try:
        # Nombre total de produits obsolètes
        obsolete_count = ObsolescenceInfo.query.filter_by(is_obsolete=True).count()
        
        # Nombre total de produits suivis
        total_tracked = ObsolescenceInfo.query.count()
        
        # Équipements avec OS obsolète
        obsolete_os = db.session.query(Equipment).join(
            ObsolescenceInfo,
            db.and_(
                Equipment.os_name == ObsolescenceInfo.product_name,
                ObsolescenceInfo.product_type == 'os',
                ObsolescenceInfo.is_obsolete == True
            )
        ).count()
        
        # Équipements avec applications obsolètes
        obsolete_apps = db.session.query(Equipment).join(
            Application,
            Equipment.id == Application.equipment_id
        ).join(
            ObsolescenceInfo,
            db.and_(
                Application.name == ObsolescenceInfo.product_name,
                ObsolescenceInfo.product_type == 'application',
                ObsolescenceInfo.is_obsolete == True
            )
        ).distinct().count()
        
        return jsonify({
            'total_tracked_products': total_tracked,
            'obsolete_products': obsolete_count,
            'equipment_with_obsolete_os': obsolete_os,
            'equipment_with_obsolete_apps': obsolete_apps,
            'obsolescence_rate': round((obsolete_count / total_tracked * 100) if total_tracked > 0 else 0, 2)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def fetch_obsolescence_data(product_name):
    """Récupère les données d'obsolescence depuis l'API endoflife.date"""
    try:
        # Normaliser le nom du produit pour l'API
        normalized_name = normalize_product_name(product_name)
        
        # Appel à l'API endoflife.date
        url = f"https://endoflife.date/api/v1/products/{normalized_name}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Traiter les données pour extraire les informations pertinentes
            if isinstance(data, list) and len(data) > 0:
                latest_release = data[0]  # Prendre la dernière version
                
                eol_date = None
                support_end_date = None
                is_obsolete = False
                
                # Extraire les dates EOL
                if 'eol' in latest_release:
                    eol_value = latest_release['eol']
                    if isinstance(eol_value, str) and eol_value not in ['false', 'true']:
                        try:
                            eol_date = datetime.strptime(eol_value, '%Y-%m-%d').date()
                            is_obsolete = eol_date < date.today()
                        except ValueError:
                            pass
                    elif eol_value is True:
                        is_obsolete = True
                
                # Extraire les dates de fin de support
                if 'support' in latest_release:
                    support_value = latest_release['support']
                    if isinstance(support_value, str) and support_value not in ['false', 'true']:
                        try:
                            support_end_date = datetime.strptime(support_value, '%Y-%m-%d').date()
                        except ValueError:
                            pass
                
                return {
                    'product_name': product_name,
                    'version': latest_release.get('cycle', 'Unknown'),
                    'eol_date': eol_date.isoformat() if eol_date else None,
                    'support_end_date': support_end_date.isoformat() if support_end_date else None,
                    'is_obsolete': is_obsolete,
                    'raw_data': latest_release
                }
        
        return None
    
    except requests.RequestException as e:
        print(f"Erreur lors de l'appel à l'API: {e}")
        return None
    except Exception as e:
        print(f"Erreur lors du traitement des données: {e}")
        return None

def normalize_product_name(product_name):
    """Normalise le nom du produit pour l'API endoflife.date"""
    # Mapping des noms de produits courants
    name_mapping = {
        'windows': 'windows',
        'windows 10': 'windows',
        'windows 11': 'windows',
        'ubuntu': 'ubuntu',
        'debian': 'debian',
        'centos': 'centos',
        'rhel': 'rhel',
        'red hat enterprise linux': 'rhel',
        'macos': 'macos',
        'mac os': 'macos',
        'java': 'java',
        'python': 'python',
        'node.js': 'nodejs',
        'nodejs': 'nodejs',
        'php': 'php',
        'mysql': 'mysql',
        'postgresql': 'postgresql',
        'apache': 'apache',
        'nginx': 'nginx',
        'docker': 'docker',
        'kubernetes': 'kubernetes'
    }
    
    normalized = product_name.lower().strip()
    return name_mapping.get(normalized, normalized)

def save_obsolescence_info(product_name, product_type, obsolescence_data):
    """Sauvegarde les informations d'obsolescence en base de données"""
    try:
        # Rechercher si l'information existe déjà
        existing_info = ObsolescenceInfo.query.filter_by(
            product_name=product_name,
            product_type=product_type
        ).first()
        
        eol_date = None
        support_end_date = None
        
        if obsolescence_data.get('eol_date'):
            eol_date = datetime.strptime(obsolescence_data['eol_date'], '%Y-%m-%d').date()
        
        if obsolescence_data.get('support_end_date'):
            support_end_date = datetime.strptime(obsolescence_data['support_end_date'], '%Y-%m-%d').date()
        
        if existing_info:
            # Mettre à jour l'information existante
            existing_info.version = obsolescence_data.get('version', 'Unknown')
            existing_info.eol_date = eol_date
            existing_info.support_end_date = support_end_date
            existing_info.is_obsolete = obsolescence_data.get('is_obsolete', False)
            existing_info.last_updated = datetime.utcnow()
        else:
            # Créer une nouvelle information
            new_info = ObsolescenceInfo(
                product_name=product_name,
                product_type=product_type,
                version=obsolescence_data.get('version', 'Unknown'),
                eol_date=eol_date,
                support_end_date=support_end_date,
                is_obsolete=obsolescence_data.get('is_obsolete', False)
            )
            db.session.add(new_info)
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de la sauvegarde: {e}")
        raise e

