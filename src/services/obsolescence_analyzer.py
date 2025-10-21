"""
Service d'analyse d'obsolescence avec IA pour les applications métier
"""
import requests
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from openai import OpenAI
import os

class ObsolescenceAnalyzer:
    def __init__(self):
        self.client = OpenAI() if os.getenv('OPENAI_API_KEY') else None
        self.endoflife_base_url = "https://endoflife.date/api"
        
    def normalize_os_name(self, os_name: str) -> str:
        """Normalise le nom de l'OS pour l'API endoflife.date"""
        if not os_name:
            return None
            
        os_name = os_name.lower().strip()
        
        # Mapping des OS vers les noms endoflife.date
        os_mappings = {
            'windows': 'windows',
            'windows xp': 'windowsxp',
            'windows 7': 'windows-7',
            'windows 10': 'windows-10',
            'windows 11': 'windows-11',
            'ubuntu': 'ubuntu',
            'debian': 'debian',
            'centos': 'centos',
            'rhel': 'rhel',
            'macos': 'macos',
            'mac os': 'macos'
        }
        
        for key, value in os_mappings.items():
            if key in os_name:
                return value
        
        return None
    
    def extract_version_from_os(self, os_full: str) -> Tuple[str, str]:
        """Extrait le nom de l'OS et sa version"""
        if not os_full:
            return None, None
            
        # Patterns pour extraire les versions
        patterns = [
            r'(Windows\s*(?:XP|7|8|10|11))\s*([^,\n]*)',
            r'(Ubuntu)\s*(\d+\.\d+)',
            r'(Debian)\s*(\d+)',
            r'(CentOS)\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, os_full, re.IGNORECASE)
            if match:
                os_name = match.group(1).strip()
                version = match.group(2).strip()
                return os_name, version
                
        return os_full, ""
    
    def get_endoflife_data(self, product: str) -> Optional[Dict]:
        """Récupère les données d'obsolescence depuis endoflife.date"""
        try:
            url = f"{self.endoflife_base_url}/{product}.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Produit {product} non trouvé dans endoflife.date")
                return None
                
        except Exception as e:
            print(f"Erreur lors de la récupération des données pour {product}: {e}")
            return None
    
    def estimate_application_eol_with_ai(self, app_name: str, app_version: str) -> Dict:
        """Estime la fin de vie d'une application avec l'IA"""
        if not self.client:
            return self.get_default_estimation(app_name, app_version)
            
        try:
            prompt = f"""
Analyse l'application suivante et estime sa fin de vie :

Application: {app_name}
Version: {app_version}

Cette application semble être un logiciel métier/laboratoire spécialisé.

Fournis une estimation réaliste de :
1. Date de fin de support (format YYYY-MM-DD)
2. Date de fin de vie (format YYYY-MM-DD) 
3. Niveau de criticité (Low, Medium, High, Critical)
4. Recommandations de migration

Réponds uniquement en JSON avec cette structure :
{{
    "eol_date": "YYYY-MM-DD",
    "support_end_date": "YYYY-MM-DD", 
    "criticality": "Low|Medium|High|Critical",
    "recommendation": "texte de recommandation",
    "confidence": "Low|Medium|High",
    "source": "AI Estimation"
}}

Base ton estimation sur :
- L'âge probable de la version
- Le type d'application (logiciel métier = cycles plus longs)
- Les patterns typiques de support des éditeurs
"""

            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Erreur IA pour {app_name}: {e}")
            return self.get_default_estimation(app_name, app_version)
    
    def get_default_estimation(self, app_name: str, app_version: str) -> Dict:
        """Estimation par défaut basée sur des heuristiques"""
        current_year = datetime.now().year
        
        # Heuristiques basées sur le nom et la version
        if any(word in app_name.lower() for word in ['legacy', 'old', 'deprecated']):
            criticality = "Critical"
            eol_year = current_year + 1
        elif any(word in app_name.lower() for word in ['chromatography', 'spectr', 'lab']):
            # Logiciels de laboratoire : cycles plus longs
            criticality = "Medium"
            eol_year = current_year + 5
        else:
            criticality = "Low"
            eol_year = current_year + 3
            
        eol_date = f"{eol_year}-12-31"
        support_date = f"{eol_year - 1}-12-31"
        
        return {
            "eol_date": eol_date,
            "support_end_date": support_date,
            "criticality": criticality,
            "recommendation": f"Planifier la migration avant {eol_year}",
            "confidence": "Low",
            "source": "Heuristic Estimation"
        }
    
    def analyze_os_obsolescence(self, os_list: List[Dict]) -> List[Dict]:
        """Analyse l'obsolescence de tous les OS"""
        results = []
        
        for os_info in os_list:
            os_name, version = self.extract_version_from_os(os_info['name'])
            normalized_name = self.normalize_os_name(os_name)
            
            if normalized_name:
                eol_data = self.get_endoflife_data(normalized_name)
                
                if eol_data:
                    # Trouve la version correspondante
                    matching_version = self.find_matching_version(eol_data, version)
                    
                    if matching_version:
                        result = {
                            "name": os_info['name'],
                            "type": "OS",
                            "equipment_count": os_info['count'],
                            "equipment_names": os_info['equipment_names'],
                            "eol_date": matching_version.get('eol'),
                            "support_end_date": matching_version.get('support'),
                            "status": self.calculate_status(matching_version.get('eol')),
                            "source": "endoflife.date",
                            "confidence": "High"
                        }
                        results.append(result)
                    
        return results
    
    def analyze_applications_obsolescence(self, apps_list: List[Dict]) -> List[Dict]:
        """Analyse l'obsolescence de toutes les applications"""
        results = []
        
        for app_info in apps_list:
            app_name = app_info['name']
            app_version = app_info.get('version', '')
            
            # Essayer d'abord endoflife.date pour les applications connues
            normalized_app = self.normalize_app_name(app_name)
            eol_data = None
            
            if normalized_app:
                eol_data = self.get_endoflife_data(normalized_app)
            
            if eol_data:
                # Utiliser les données endoflife.date
                matching_version = self.find_matching_version(eol_data, app_version)
                if matching_version:
                    result = {
                        "name": f"{app_name} {app_version}".strip(),
                        "type": "Application",
                        "equipment_count": app_info['count'],
                        "equipment_names": app_info['equipment_names'],
                        "eol_date": matching_version.get('eol'),
                        "support_end_date": matching_version.get('support'),
                        "status": self.calculate_status(matching_version.get('eol')),
                        "source": "endoflife.date",
                        "confidence": "High"
                    }
                    results.append(result)
            else:
                # Utiliser l'IA pour estimer
                estimation = self.estimate_application_eol_with_ai(app_name, app_version)
                
                result = {
                    "name": f"{app_name} {app_version}".strip(),
                    "type": "Application", 
                    "equipment_count": app_info['count'],
                    "equipment_names": app_info['equipment_names'],
                    "eol_date": estimation.get('eol_date'),
                    "support_end_date": estimation.get('support_end_date'),
                    "status": estimation.get('criticality', 'Medium'),
                    "recommendation": estimation.get('recommendation'),
                    "source": estimation.get('source', 'AI Estimation'),
                    "confidence": estimation.get('confidence', 'Medium')
                }
                results.append(result)
                
        return results
    
    def normalize_app_name(self, app_name: str) -> Optional[str]:
        """Normalise le nom d'application pour endoflife.date"""
        if not app_name:
            return None
            
        app_name = app_name.lower().strip()
        
        # Applications connues dans endoflife.date
        app_mappings = {
            'java': 'java',
            'python': 'python',
            'nodejs': 'nodejs',
            'node.js': 'nodejs',
            'php': 'php',
            'mysql': 'mysql',
            'postgresql': 'postgresql',
            'mongodb': 'mongodb',
            'redis': 'redis',
            'nginx': 'nginx',
            'apache': 'apache',
            'docker': 'docker',
            'kubernetes': 'kubernetes'
        }
        
        for key, value in app_mappings.items():
            if key in app_name:
                return value
                
        return None
    
    def find_matching_version(self, eol_data: List[Dict], version: str) -> Optional[Dict]:
        """Trouve la version correspondante dans les données endoflife.date"""
        if not eol_data or not version:
            return eol_data[0] if eol_data else None
            
        # Recherche exacte d'abord
        for item in eol_data:
            if str(item.get('cycle', '')).lower() == version.lower():
                return item
                
        # Recherche partielle
        for item in eol_data:
            cycle = str(item.get('cycle', ''))
            if version.lower() in cycle.lower() or cycle.lower() in version.lower():
                return item
                
        # Retourne la première version si aucune correspondance
        return eol_data[0] if eol_data else None
    
    def calculate_status(self, eol_date: str) -> str:
        """Calcule le statut basé sur la date de fin de vie"""
        if not eol_date:
            return "Unknown"
            
        try:
            eol = datetime.strptime(eol_date, '%Y-%m-%d')
            now = datetime.now()
            days_remaining = (eol - now).days
            
            if days_remaining < 0:
                return "Critical"  # Déjà obsolète
            elif days_remaining < 365:
                return "High"  # Moins d'un an
            elif days_remaining < 730:
                return "Medium"  # Moins de 2 ans
            else:
                return "Low"  # Plus de 2 ans
                
        except ValueError:
            return "Unknown"
