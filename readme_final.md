# Gestionnaire d'Obsolescence IT - Version 2.0

Application web complète de gestion de l'obsolescence d'un parc informatique avec authentification locale, interface d'administration, tableau de bord interactif, recherche automatique d'informations d'obsolescence, **filtrage par localisation** et **importation d'équipements via Excel**.

## 🚀 Fonctionnalités Principales

### Tableau de Bord Interactif
- **Statistiques en temps réel** : Total équipements, actifs, obsolètes, alertes critiques
- **Graphiques dynamiques** : Répartition par type, état d'obsolescence, localisation
- **🆕 Filtrage par localisation** : Vue globale ou par site spécifique
- **Alertes récentes** : Notifications d'obsolescence avec niveaux de priorité

### Gestion Complète des Équipements
- **CRUD complet** : Création, lecture, mise à jour, suppression
- **🆕 Import Excel en masse** : Importation depuis fichiers .xlsx/.xls avec modèle fourni
- **Filtres avancés** : Par type, statut, localisation, recherche textuelle
- **Types supportés** : PC, Serveurs, Imprimantes, Switch, Machines laboratoire
- **Gestion des applications** : Applications installées par équipement

### Suivi Automatique d'Obsolescence
- **Intégration API endoflife.date** : Recherche automatique des dates de fin de vie
- **Support multi-produits** : OS (Windows, Ubuntu, etc.) et applications
- **Calcul intelligent** : Temps restant avant EOL avec niveaux de criticité
- **Mise à jour périodique** : Actualisation automatique des informations

### Administration des Utilisateurs
- **Gestion des comptes** : Interface d'administration complète
- **Système de rôles** : Admin, Manager, Technicien, Utilisateur
- **Authentification locale** : Extensible vers Active Directory
- **Statistiques utilisateurs** : Suivi des connexions et activités

## 🎯 Nouvelles Fonctionnalités Version 2.0

### 📍 Filtrage par Localisation
- **Dropdown intelligent** : Sélection parmi toutes les localisations disponibles
- **Filtrage en temps réel** : Mise à jour automatique de tous les graphiques
- **Indicateur visuel** : Badge affiché quand un filtre est actif
- **Vue adaptative** : Interface qui s'adapte selon le filtre sélectionné

### 📊 Import Excel Avancé
- **Interface intuitive** : Modal dédiée avec instructions claires
- **Modèle pré-formaté** : Téléchargement d'un fichier Excel exemple
- **Glisser-déposer** : Zone d'upload moderne et intuitive
- **Validation robuste** : Vérification des colonnes et données obligatoires
- **Rapport détaillé** : Statistiques d'import avec gestion d'erreurs
- **Détection automatique** : Type d'équipement déterminé selon le nom

#### Format Excel Supporté
Basé sur vos spécifications, les colonnes supportées sont :

**Colonnes Obligatoires :**
- `Salle` : Localisation de l'équipement
- `Nom PC` : Nom unique de l'équipement

**Colonnes Optionnelles :**
- `Description  (Alias)` : Description ou alias de l'équipement
- `Marque` : Marque du fabricant
- `N° modèle` : Numéro de modèle
- `Système d'exploitation PC` : OS installé
- `Application` : Application principale installée
- `Version` : Version de l'application
- `Connecté au réseau O/N` : Connexion réseau (O/N)
- `Sauvegardé sur réseau RLS O/N` : Sauvegarde RLS (O/N)
- `Adresse IP` : Adresse IP de l'équipement
- `A sauvegarder O/N` : Nécessite sauvegarde (O/N)
- `Fournisseur matériel` : Nom du fournisseur

## 🔧 Architecture Technique

### Backend (Flask)
- **Framework** : Python 3.11 + Flask
- **Base de données** : SQLite avec SQLAlchemy ORM
- **APIs REST** : Endpoints complets et documentés
- **Intégrations** : API endoflife.date pour données d'obsolescence
- **🆕 Import Excel** : pandas + openpyxl pour traitement des fichiers
- **CORS** : Configuration pour interaction frontend-backend

### Frontend (React)
- **Framework** : React 18 + Vite
- **Design** : Tailwind CSS + shadcn/ui components
- **Graphiques** : Recharts pour visualisations interactives
- **Icons** : Lucide React pour interface moderne
- **Responsive** : Adaptation automatique mobile/desktop

### Déploiement
- **Plateforme** : Manus Cloud Platform
- **🆕 URL Production** : https://nghki1cj0llm.manus.space
- **CI/CD** : Déploiement automatique via Git

## 📦 Installation et Configuration

### Prérequis
- Python 3.11+
- Node.js 18+
- Git
- pnpm (pour le frontend)

### Installation sur un Serveur Linux (Recommandé)

Un script d\'installation `install.sh` est fourni à la racine du dépôt backend pour automatiser le déploiement.

1.  **Cloner le dépôt backend** sur votre serveur Linux :
    ```bash
    git clone https://github.com/Samuel-PL1/Obsolescence-IT-management.git
    cd Obsolescence-IT-management
    ```
2.  **Rendre le script exécutable** :
    ```bash
    chmod +x install.sh
    ```
3.  **Exécuter le script** :
    ```bash
    ./install.sh
    ```

Le script va :
- Vérifier les prérequis (Git, Python3, pip, npm, pnpm).
- Installer le backend (environnement virtuel, dépendances Python, initialisation DB).
- Cloner le dépôt frontend, installer ses dépendances, le builder et copier les fichiers statiques dans le backend.
- Nettoyer les fichiers temporaires.

Après l\'exécution, l\'application sera prête à être démarrée. Le script vous indiquera les commandes pour lancer le serveur Flask. Pour une mise en production, il est recommandé de configurer un serveur web comme Nginx ou Apache en tant que proxy inverse.

### Installation Manuelle (pour information)

#### Backend
```bash
# Cloner le projet
git clone https://github.com/Samuel-PL1/Obsolescence-IT-management.git
cd Obsolescence-IT-management

# Créer l\'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données
python src/init_db.py

# Lancer le serveur
python src/main.py
```

#### Frontend
```bash
# Cloner le projet
git clone https://github.com/Samuel-PL1/Obsolescence-IT-management-frontend.git
cd Obsolescence-IT-management-frontend

# Installer les dépendances
pnpm install

# Build production
pnpm run build

# Copier les fichiers build vers le répertoire static du backend
cp -r dist/* ../Obsolescence-IT-management/src/static/
```

## 📊 APIs Disponibles

### Équipements
- `GET /api/equipment` : Liste tous les équipements
- `POST /api/equipment` : Crée un nouvel équipement
- `GET /api/equipment/{id}` : Détails d'un équipement
- `PUT /api/equipment/{id}` : Met à jour un équipement
- `DELETE /api/equipment/{id}` : Supprime un équipement
- `GET /api/equipment/stats` : Statistiques générales
- `🆕 GET /api/equipment/stats?location={location}` : Statistiques filtrées
- `🆕 GET /api/equipment/locations` : Liste des localisations
- `🆕 POST /api/equipment/import` : Import Excel
- `🆕 GET /api/equipment/export-template` : Modèle Excel

### Obsolescence
- `GET /api/obsolescence/check/{product}` : Vérification d'obsolescence
- `POST /api/obsolescence/update-all` : Mise à jour globale
- `GET /api/obsolescence/stats` : Statistiques d'obsolescence

### Utilisateurs
- `GET /api/users` : Liste des utilisateurs
- `POST /api/users` : Crée un utilisateur
- `GET /api/users/{id}` : Détails d'un utilisateur
- `PUT /api/users/{id}` : Met à jour un utilisateur
- `DELETE /api/users/{id}` : Supprime un utilisateur

## 🧪 Tests et Validation

### Tests Fonctionnels Version 2.0
- ✅ **Filtrage par localisation** : Opérationnel sur le tableau de bord
- ✅ **Import Excel** : Validation des colonnes et données
- ✅ **Téléchargement modèle** : Fichier Excel pré-formaté
- ✅ **Gestion des erreurs** : Rapport détaillé d'import
- ✅ **Interface responsive** : Adaptation mobile/desktop
- ✅ **APIs backend** : Tous les endpoints fonctionnels

### Tests d'Intégration
- ✅ Communication frontend-backend
- ✅ Persistance des données importées
- ✅ Mise à jour des statistiques en temps réel
- ✅ Intégration endoflife.date

## 📚 Documentation Complète

- **📋 Documentation Technique** : `documentation_technique.md`
- **👤 Guide Utilisateur** : `guide_utilisateur.md`
- **📝 Changelog** : `changelog.md`
- **🔧 Spécifications** : `specifications.md`
- **🌐 API endoflife.date** : `endoflife_api_doc.md`

## 🎯 Guide d'Utilisation Rapide

### Import Excel
1. Aller dans **Équipements**
2. Cliquer sur **"Import Excel"**
3. Télécharger le modèle Excel
4. Remplir avec vos données
5. Glisser-déposer le fichier
6. Cliquer sur **"Importer"**

### Filtrage par Localisation
1. Aller sur le **Tableau de bord**
2. Sélectionner une localisation dans le dropdown
3. Observer la mise à jour des graphiques
4. Cliquer sur "Supprimer le filtre" pour revenir à la vue globale

## 🔮 Évolutions Futures

### Authentification
- **Active Directory** : Intégration LDAP/AD
- **SSO** : Single Sign-On
- **Permissions granulaires** : Contrôle d'accès par fonctionnalité

### Fonctionnalités Avancées
- **Notifications automatiques** : Alertes par email/SMS
- **Planification de maintenance** : Calendrier des mises à jour
- **Rapports avancés** : Génération PDF, planification
- **API publique** : Intégration avec systèmes tiers
- **Audit trail** : Historique des modifications

### Performance et Scalabilité
- **Base de données** : Migration vers PostgreSQL
- **Cache** : Redis pour performances
- **Monitoring** : Métriques et alertes système

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème :
- **Documentation** : Consulter les guides fournis
- **Issues** : Créer un ticket sur le repository
- **Contact** : [À définir selon l'organisation]

---

**🎉 Version actuelle** : 2.0 avec filtrage par localisation et import Excel  
**📅 Dernière mise à jour** : 19 Septembre 2025  
**🌐 URL de production** : https://nghki1cj0llm.manus.space  
**✨ Nouvelles fonctionnalités** : Filtrage par localisation + Import Excel complet

