# Documentation Technique - Gestionnaire d'Obsolescence IT

## Vue d'ensemble

Le Gestionnaire d'Obsolescence IT est une application web complète développée pour gérer l'obsolescence d'un parc informatique. Elle permet le suivi des équipements, des systèmes d'exploitation et des applications, avec une visualisation des données via un tableau de bord interactif.

**URL de l'application déployée** : https://lnh8imcwwzew.manus.space

## Architecture Technique

### Stack Technologique

**Backend :**
- **Framework** : Flask (Python 3.11)
- **Base de données** : SQLite (extensible vers PostgreSQL)
- **ORM** : SQLAlchemy
- **API** : RESTful avec CORS activé
- **Authentification** : Locale (extensible Active Directory)

**Frontend :**
- **Framework** : React 18 avec Vite
- **UI Library** : shadcn/ui + Tailwind CSS
- **Graphiques** : Recharts
- **Icônes** : Lucide React
- **Routing** : React Router DOM

**Intégrations externes :**
- **API endoflife.date** : Données d'obsolescence automatisées
- **Déploiement** : Manus Cloud Platform

### Architecture des Données

#### Modèles de Base de Données

**Equipment (Équipements)**
```python
- id: Integer (Primary Key)
- name: String(100) - Nom de l'équipement
- equipment_type: String(50) - Type (PC, Serveur, Imprimante, etc.)
- location: String(200) - Localisation
- ip_address: String(15) - Adresse IP
- os_name: String(100) - Nom du système d'exploitation
- os_version: String(50) - Version du système
- acquisition_date: Date - Date d'acquisition
- warranty_end_date: Date - Fin de garantie
- status: String(20) - Statut (Active, Obsolete, In Stock)
- description_alias: String(200) - Description (Alias)
- brand: String(100) - Marque
- model_number: String(100) - N° modèle
- network_connected: Boolean - Connecté au réseau O/N
- rls_network_saved: Boolean - Sauvegardé sur réseau RLS O/N
- to_be_backed_up: Boolean - A sauvegarder O/N
- supplier: String(100) - Fournisseur matériel
- created_at: DateTime - Date de création
- updated_at: DateTime - Dernière modification
```

**Application (Applications installées)**
```python
- id: Integer (Primary Key)
- name: String(100) - Nom de l'application
- version: String(50) - Version
- equipment_id: Integer (Foreign Key) - Référence équipement
- created_at: DateTime - Date d'ajout
```

**ObsolescenceInfo (Informations d'obsolescence)**
```python
- id: Integer (Primary Key)
- product_name: String(100) - Nom du produit
- product_type: String(20) - Type (os/application)
- version: String(50) - Version
- eol_date: Date - Date de fin de vie
- support_end_date: Date - Fin de support
- is_obsolete: Boolean - Statut d'obsolescence
- last_updated: DateTime - Dernière mise à jour
```

**User (Utilisateurs)**
```python
- id: Integer (Primary Key)
- username: String(80) - Nom d'utilisateur
- email: String(120) - Adresse email
```

## APIs REST

### Endpoints Équipements

**GET /api/equipment**
- Description : Récupère tous les équipements
- Réponse : Liste des équipements avec leurs applications

**POST /api/equipment**
- Description : Crée un nouvel équipement
- Body : Données de l'équipement (JSON)
- Réponse : Équipement créé avec ID

**GET /api/equipment/{id}**
- Description : Récupère un équipement spécifique
- Réponse : Détails complets de l'équipement

**PUT /api/equipment/{id}**
- Description : Met à jour un équipement
- Body : Données modifiées (JSON)
- Réponse : Équipement mis à jour

**DELETE /api/equipment/{id}**
- Description : Supprime un équipement
- Réponse : Message de confirmation

**GET /api/equipment/stats**
- Description : Statistiques des équipements
- Réponse : Répartition par type, localisation, statut

### Endpoints Obsolescence

**POST /api/obsolescence/check**
- Description : Vérifie l'obsolescence d'un produit
- Body : `{"product_name": "Windows", "product_type": "os"}`
- Réponse : Informations d'obsolescence

**POST /api/obsolescence/update-all**
- Description : Met à jour toutes les informations d'obsolescence
- Réponse : Nombre de produits mis à jour et erreurs

**GET /api/obsolescence/info**
- Description : Récupère toutes les informations d'obsolescence
- Réponse : Liste complète des données d'obsolescence

**GET /api/obsolescence/stats**
- Description : Statistiques d'obsolescence
- Réponse : Compteurs et taux d'obsolescence

### Endpoints Utilisateurs

**GET /api/users**
- Description : Récupère tous les utilisateurs
- Réponse : Liste des utilisateurs

**POST /api/users**
- Description : Crée un nouvel utilisateur
- Body : Données utilisateur (JSON)
- Réponse : Utilisateur créé

## Intégration API endoflife.date

L'application utilise l'API publique endoflife.date pour récupérer automatiquement les informations d'obsolescence.

### Fonctionnement

1. **Normalisation des noms** : Les noms de produits sont normalisés selon le mapping de l'API
2. **Appels automatiques** : Requêtes HTTP vers `https://endoflife.date/api/v1/products/{product}`
3. **Traitement des données** : Extraction des dates EOL et de fin de support
4. **Sauvegarde locale** : Stockage en base pour consultation rapide

### Produits supportés

- Systèmes d'exploitation : Windows, Ubuntu, Debian, CentOS, RHEL, macOS
- Applications : Java, Python, Node.js, PHP, MySQL, PostgreSQL, Apache, Nginx
- Outils : Docker, Kubernetes

## Interface Utilisateur

### Composants Principaux

**Sidebar (Navigation)**
- Navigation collapsible
- Icônes Lucide
- Indicateur de page active
- Profil utilisateur

**Dashboard (Tableau de bord)**
- Cartes de statistiques
- Graphiques Recharts (barres, camembert)
- Alertes récentes
- Actualisation en temps réel

**EquipmentList (Liste des équipements)**
- Grille de cartes responsive
- Filtres par type, statut, recherche
- Badges de statut colorés
- Actions CRUD

**EquipmentForm (Formulaire équipement)**
- Validation côté client
- Gestion des applications
- Sélecteurs de dates
- Messages d'erreur

**ObsolescenceView (Vue obsolescence)**
- Liste détaillée des produits
- Calcul du temps restant
- Export CSV
- Filtres avancés

**UserManagement (Gestion utilisateurs)**
- Administration des comptes
- Gestion des rôles
- Statistiques utilisateurs
- Formulaire d'ajout

### Responsive Design

- **Mobile First** : Interface adaptée aux écrans mobiles
- **Breakpoints** : sm (640px), md (768px), lg (1024px), xl (1280px)
- **Grilles flexibles** : CSS Grid et Flexbox
- **Navigation adaptative** : Sidebar collapsible sur mobile

## Sécurité

### Authentification

- **Locale** : Comptes stockés en base de données
- **Extensible AD** : Architecture prête pour l'intégration Active Directory
- **Sessions** : Gestion des sessions utilisateur
- **Rôles** : Système de permissions (Admin, Manager, Technicien, Utilisateur)

### Protection des APIs

- **CORS** : Configuration pour les requêtes cross-origin
- **Validation** : Validation des données d'entrée
- **Sanitisation** : Protection contre les injections
- **Rate Limiting** : Prêt pour l'implémentation

## Déploiement

### Environnement de Production

**URL** : https://3dhkilc8wjl6.manus.space

**Configuration** :
- Serveur : Manus Cloud Platform
- Base de données : SQLite (production-ready)
- Assets : Fichiers statiques optimisés
- HTTPS : Certificat SSL automatique

### Variables d'Environnement

```bash
FLASK_ENV=production
SECRET_KEY=asdf#FGSgvasgf$5$WGT
SQLALCHEMY_DATABASE_URI=sqlite:///app.db
```

### Installation sur un Serveur Linux

Pour faciliter le déploiement sur un serveur Linux, un script d'installation `install.sh` est fourni à la racine du projet backend. Ce script automatise les étapes suivantes :

1.  **Vérification des prérequis** : Git, Python3, pip, npm, pnpm.
2.  **Installation du Backend** :
    - Création et activation d'un environnement virtuel Python.
    - Installation des dépendances Python (`requirements.txt`).
    - Initialisation de la base de données SQLite.
3.  **Installation du Frontend** :
    - Clonage du dépôt frontend temporairement.
    - Installation des dépendances Node.js avec `pnpm`.
    - Construction du projet frontend (`pnpm build`).
    - Copie des fichiers statiques du frontend vers le répertoire `src/static` du backend.
4.  **Nettoyage** : Suppression des fichiers temporaires du frontend.

#### Utilisation du Script d'Installation

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

Après l'exécution du script, l'application sera prête à être démarrée. Le script vous indiquera les commandes pour lancer le serveur Flask. Pour une mise en production, il est recommandé de configurer un serveur web comme Nginx ou Apache en tant que proxy inverse.

### Build et Déploiement Manuel (pour information)

1.  **Build Frontend** :
    ```bash
    cd it-obsolescence-frontend
    npm run build
    ```

2.  **Copie des assets** :
    ```bash
    cp -r dist/* ../it-obsolescence-manager/src/static/
    ```

3.  **Déploiement** :
    ```bash
    # Automatique via Manus Platform ou manuel
    ```

## Maintenance et Monitoring

### Logs

- **Flask** : Logs d'application et d'erreurs
- **Accès** : Logs des requêtes HTTP
- **Base de données** : Logs SQLAlchemy

### Monitoring

- **Santé de l'application** : Endpoint `/health` (à implémenter)
- **Métriques** : Nombre d'équipements, taux d'obsolescence
- **Alertes** : Notifications d'obsolescence critique

### Sauvegarde

- **Base de données** : Sauvegarde automatique SQLite
- **Configuration** : Versioning Git
- **Assets** : Stockage redondant

## Extensions Futures

### Authentification Active Directory

```python
# Configuration LDAP
LDAP_SERVER = 'ldap://domain.company.com'
LDAP_BASE_DN = 'DC=company,DC=com'
LDAP_USER_DN = 'OU=Users,DC=company,DC=com'
```

### Notifications

- **Email** : Alertes d'obsolescence par email
- **Slack/Teams** : Intégrations de messagerie
- **Dashboard** : Notifications en temps réel

### Rapports Avancés

- **PDF** : Génération de rapports PDF
- **Planification** : Rapports automatiques
- **Graphiques** : Visualisations avancées

### API Extensions

- **GraphQL** : API GraphQL pour requêtes complexes
- **Webhooks** : Notifications externes
- **Bulk Operations** : Opérations en lot

## Troubleshooting

### Problèmes Courants

**Erreur de connexion à l'API endoflife.date**
```python
# Vérifier la connectivité réseau
curl -I https://endoflife.date/api/v1/products/windows
```

**Base de données verrouillée**
```bash
# Redémarrer l'application
systemctl restart flask-app
```

**Assets non chargés**
```bash
# Vérifier les fichiers statiques
ls -la src/static/
```

### Support

Pour toute question technique ou problème, consulter :
- Documentation API : https://endoflife.date/docs/api/
- Issues GitHub : (à créer)
- Contact support : (à définir)


## Nouvelles Fonctionnalités (Version 2.0)

### Filtrage par Localisation sur le Tableau de Bord

#### Description
Le tableau de bord permet maintenant de filtrer tous les graphiques et statistiques par localisation spécifique.

#### Fonctionnalités
- **Dropdown de sélection** : Liste déroulante avec toutes les localisations disponibles
- **Filtrage en temps réel** : Les graphiques se mettent à jour automatiquement
- **Indicateur visuel** : Badge affiché quand un filtre est actif
- **Option "Toutes les localisations"** : Permet de revenir à la vue globale

#### Endpoints API
```
GET /api/equipment/locations
- Retourne la liste des localisations uniques

GET /api/equipment/stats?location={location}
- Retourne les statistiques filtrées par localisation
- Paramètre optionnel : location (string)
```

### Import Excel des Équipements

#### Description
Fonctionnalité complète d'import en masse des équipements depuis des fichiers Excel (.xlsx, .xls).

#### Format de Fichier Supporté
Basé sur les spécifications fournies, les colonnes supportées sont :

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

#### Détection Automatique du Type
Le type d'équipement est déterminé automatiquement selon le nom :
- **PC** : Par défaut
- **Serveur** : Si le nom contient "srv", "server"
- **Imprimante** : Si le nom contient "imp", "print"
- **Switch** : Si le nom contient "sw", "switch"
- **Machine laboratoire** : Si le nom contient "lab", "machine"

#### Endpoints API
```
POST /api/equipment/import
- Import des équipements depuis un fichier Excel
- Content-Type: multipart/form-data
- Paramètre: file (fichier Excel)
- Retourne: statistiques d'import et erreurs

GET /api/equipment/export-template
- Télécharge un modèle Excel avec exemples
- Retourne: fichier modele_import_equipements.xlsx
```

#### Dépendances Ajoutées
```bash
pip install pandas openpyxl
```

### Tests et Validation Version 2.0

#### Tests Fonctionnels
- ✅ Filtrage par localisation opérationnel
- ✅ Import Excel avec validation des colonnes
- ✅ Téléchargement du modèle Excel
- ✅ Gestion des erreurs d'import
- ✅ Interface utilisateur responsive

#### URL de Déploiement Mise à Jour
- **Production** : https://nghki1cj0llm.manus.space
- **Version** : 2.0 avec filtrage et import Excel


