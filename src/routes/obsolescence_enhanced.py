"""
Routes d'obsolescence améliorées avec analyse complète des OS et applications
"""
from flask import Blueprint, jsonify, request
from src.models.equipment import Equipment
from src.models.obsolescence import ObsolescenceInfo
from src.database import db
from src.services.obsolescence_analyzer import ObsolescenceAnalyzer
from collections import defaultdict
import json
from datetime import datetime

obsolescence_bp = Blueprint('obsolescence_enhanced', __name__)

@obsolescence_bp.route('/api/obsolescence/analyze-all', methods=['POST'])
def analyze_all_obsolescence():
    """Analyse complète de l'obsolescence de tous les OS et applications"""
    try:
        analyzer = ObsolescenceAnalyzer()
        
        # Récupérer tous les équipements
        equipments = Equipment.query.all()
        
        # Analyser les OS
        os_data = extract_os_from_equipments(equipments)
        os_results = analyzer.analyze_os_obsolescence(os_data)
        
        # Analyser les applications
        apps_data = extract_applications_from_equipments(equipments)
        app_results = analyzer.analyze_applications_obsolescence(apps_data)
        
        # Sauvegarder les résultats en base
        save_obsolescence_results(os_results + app_results)
        
        return jsonify({
            "message": f"Analyse terminée: {len(os_results)} OS et {len(app_results)} applications analysés",
            "os_analyzed": len(os_results),
            "applications_analyzed": len(app_results),
            "total_products": len(os_results) + len(app_results)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@obsolescence_bp.route('/api/obsolescence/products', methods=['GET'])
def get_all_obsolescence_products():
    """Récupère tous les produits avec leurs informations d'obsolescence"""
    try:
        products = ObsolescenceInfo.query.all()
        
        result = []
        for product in products:
            result.append({
                "id": product.id,
                "name": product.product_name,
                "version": product.version,
                "type": product.product_type,
                "eol_date": product.eol_date.isoformat() if product.eol_date else None,
                "support_end_date": product.support_end_date.isoformat() if product.support_end_date else None,
                "status": product.status,
                "equipment_count": len(product.equipment_names.split(',')) if product.equipment_names else 0,
                "equipment_names": product.equipment_names.split(',') if product.equipment_names else [],
                "source": product.source,
                "confidence": product.confidence,
                "recommendation": product.recommendation,
                "last_updated": product.last_updated.isoformat() if product.last_updated else None
            })
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@obsolescence_bp.route('/api/obsolescence/stats-enhanced', methods=['GET'])
def get_enhanced_obsolescence_stats():
    """Statistiques d'obsolescence améliorées"""
    try:
        products = ObsolescenceInfo.query.all()
        
        stats = {
            "total_tracked_products": len(products),
            "by_status": defaultdict(int),
            "by_type": defaultdict(int),
            "critical_products": [],
            "obsolete_products": 0,
            "equipment_with_obsolete_os": 0,
            "equipment_with_obsolete_apps": 0,
            "obsolescence_rate": 0.0
        }
        
        critical_count = 0
        obsolete_count = 0
        
        for product in products:
            stats["by_status"][product.status] += 1
            stats["by_type"][product.product_type] += 1
            
            if product.status in ["Critical", "High"]:
                critical_count += 1
                if product.status == "Critical":
                    obsolete_count += 1
                    
                stats["critical_products"].append({
                    "name": product.product_name,
                    "version": product.version,
                    "type": product.product_type,
                    "status": product.status,
                    "eol_date": product.eol_date.isoformat() if product.eol_date else None,
                    "equipment_count": len(product.equipment_names.split(',')) if product.equipment_names else 0
                })
        
        stats["obsolete_products"] = obsolete_count
        
        # Calculer le taux d'obsolescence
        if len(products) > 0:
            stats["obsolescence_rate"] = round((critical_count / len(products)) * 100, 1)
        
        # Compter les équipements avec OS/apps obsolètes
        os_obsolete = ObsolescenceInfo.query.filter_by(product_type="OS", status="Critical").all()
        apps_obsolete = ObsolescenceInfo.query.filter_by(product_type="Application", status="Critical").all()
        
        stats["equipment_with_obsolete_os"] = sum(len(p.equipment_names.split(',')) for p in os_obsolete if p.equipment_names)
        stats["equipment_with_obsolete_apps"] = sum(len(p.equipment_names.split(',')) for p in apps_obsolete if p.equipment_names)
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_os_from_equipments(equipments):
    """Extrait tous les OS uniques des équipements"""
    os_dict = defaultdict(lambda: {"count": 0, "equipment_names": []})
    
    for equipment in equipments:
        if equipment.os_name and equipment.os_name.strip() and equipment.os_name != '?':
            os_full = f"{equipment.os_name} {equipment.os_version or ''}".strip()
            os_dict[os_full]["count"] += 1
            os_dict[os_full]["equipment_names"].append(equipment.name)
    
    return [{"name": os_name, **data} for os_name, data in os_dict.items()]

def extract_applications_from_equipments(equipments):
    """Extrait toutes les applications uniques des équipements"""
    apps_dict = defaultdict(lambda: {"count": 0, "equipment_names": [], "version": ""})
    
    for equipment in equipments:
        if equipment.applications:
            try:
                apps_data = json.loads(equipment.applications) if isinstance(equipment.applications, str) else equipment.applications
                for app in apps_data:
                    app_name = app.get('name', '').strip()
                    app_version = app.get('version', '').strip()
                    
                    if app_name and app_name != '?':
                        app_key = f"{app_name}_{app_version}"
                        apps_dict[app_key]["count"] += 1
                        apps_dict[app_key]["equipment_names"].append(equipment.name)
                        apps_dict[app_key]["name"] = app_name
                        apps_dict[app_key]["version"] = app_version
            except (json.JSONDecodeError, TypeError):
                continue
    
    return [{"name": data["name"], "version": data["version"], "count": data["count"], "equipment_names": data["equipment_names"]} 
            for data in apps_dict.values()]

def save_obsolescence_results(results):
    """Sauvegarde les résultats d'analyse en base de données"""
    try:
        # Supprimer les anciennes données
        ObsolescenceInfo.query.delete()
        
        for result in results:
            # Convertir les dates string en datetime
            eol_date = None
            support_date = None
            
            if result.get('eol_date'):
                try:
                    eol_date = datetime.strptime(result['eol_date'], '%Y-%m-%d')
                except ValueError:
                    pass
                    
            if result.get('support_end_date'):
                try:
                    support_date = datetime.strptime(result['support_end_date'], '%Y-%m-%d')
                except ValueError:
                    pass
            
            obsolescence_info = ObsolescenceInfo(
                product_name=result['name'],
                version=result.get('version', ''),
                product_type=result['type'],
                eol_date=eol_date,
                support_end_date=support_date,
                status=result.get('status', 'Unknown'),
                equipment_names=','.join(result.get('equipment_names', [])),
                source=result.get('source', 'Unknown'),
                confidence=result.get('confidence', 'Medium'),
                recommendation=result.get('recommendation', ''),
                last_updated=datetime.now()
            )
            
            db.session.add(obsolescence_info)
        
        db.session.commit()
        print(f"Sauvegardé {len(results)} produits d'obsolescence")
        
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de la sauvegarde: {e}")
        raise e

@obsolescence_bp.route('/api/obsolescence/product/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    """Récupère les détails d'un produit spécifique"""
    try:
        product = ObsolescenceInfo.query.get_or_404(product_id)
        
        return jsonify({
            "id": product.id,
            "name": product.product_name,
            "version": product.version,
            "type": product.product_type,
            "eol_date": product.eol_date.isoformat() if product.eol_date else None,
            "support_end_date": product.support_end_date.isoformat() if product.support_end_date else None,
            "status": product.status,
            "equipment_names": product.equipment_names.split(',') if product.equipment_names else [],
            "source": product.source,
            "confidence": product.confidence,
            "recommendation": product.recommendation,
            "last_updated": product.last_updated.isoformat() if product.last_updated else None
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
