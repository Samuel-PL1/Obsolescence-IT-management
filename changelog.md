# Changelog - Gestionnaire d'Obsolescence IT

## Version 2.0 - 19 Septembre 2025

### 🎯 Nouvelles Fonctionnalités

#### Filtrage par Localisation sur le Tableau de Bord
- **Dropdown de sélection** : Filtre tous les graphiques par localisation
- **Filtrage en temps réel** : Mise à jour automatique des statistiques
- **Indicateur visuel** : Badge affiché quand un filtre est actif
- **Vue adaptative** : Graphique par localisation masqué lors du filtrage

#### Import Excel des Équipements
- **Interface d'import** : Modal dédiée avec instructions claires
- **Modèle Excel** : Téléchargement d'un fichier exemple pré-formaté
- **Glisser-déposer** : Zone intuitive pour l'upload de fichiers
- **Validation robuste** : Vérification des colonnes et données
- **Rapport détaillé** : Statistiques d'import avec gestion d'erreurs
- **Détection automatique** : Type d'équipement selon le nom

### 🔧 Améliorations Techniques

#### Backend
- **Nouveaux endpoints** :
  - `GET /api/equipment/locations` : Liste des localisations
  - `GET /api/equipment/stats?location=` : Statistiques filtrées
  - `POST /api/equipment/import` : Import Excel
  - `GET /api/equipment/export-template` : Modèle Excel
- **Dépendances ajoutées** : pandas, openpyxl
- **Validation des données** : Gestion des erreurs d'import

#### Frontend
- **Nouveau composant** : `ImportExcel.jsx`
- **Interface améliorée** : Filtres et boutons d'action
- **Gestion d'état** : Synchronisation des données
- **Feedback utilisateur** : Messages d'erreur et de succès

### 📊 Format d'Import Excel Supporté

#### Colonnes Obligatoires
- `Salle` : Localisation de l'équipement
- `Nom PC` : Nom unique de l'équipement

#### Colonnes Optionnelles
- `Description (Alias)` : Description de l'équipement
- `Système d'exploitation PC` : OS installé
- `Application` : Application principale
- `Version` : Version de l'application
- `Fournisseur matériel` : Fabricant

### 🚀 Déploiement
- **URL de production** : https://nghki1cj0llm.manus.space
- **Tests validés** : Toutes les fonctionnalités opérationnelles

---

## Version 1.0 - 19 Septembre 2025

### 🎯 Fonctionnalités Initiales

#### Tableau de Bord
- **Statistiques en temps réel** : Total équipements, actifs, obsolètes, alertes
- **Graphiques interactifs** : 
  - Équipements par type (barres)
  - État d'obsolescence (camembert)
  - Équipements par localisation (barres horizontales)
- **Alertes récentes** : Notifications d'obsolescence avec niveaux de priorité

#### Gestion des Équipements
- **CRUD complet** : Création, lecture, mise à jour, suppression
- **Filtres avancés** : Par type, statut, recherche textuelle
- **Cartes visuelles** : Affichage détaillé avec badges de statut
- **Gestion des applications** : Applications installées par équipement

#### Suivi d'Obsolescence
- **Intégration API endoflife.date** : Recherche automatique des dates EOL
- **Calcul intelligent** : Temps restant avant fin de support
- **Niveaux de criticité** : Critique, Obsolète, Faible
- **Export de rapports** : Génération de rapports CSV

#### Administration des Utilisateurs
- **Gestion des comptes** : CRUD utilisateurs
- **Système de rôles** : Admin, Manager, Technicien, Utilisateur
- **Statistiques utilisateurs** : Actifs/inactifs, historique connexions

### 🔧 Architecture Technique

#### Backend (Flask)
- **APIs REST** : Endpoints complets pour toutes les fonctionnalités
- **Base de données** : SQLite avec modèles SQLAlchemy
- **Authentification** : Système local (extensible AD)
- **CORS configuré** : Support frontend-backend

#### Frontend (React)
- **Interface moderne** : Design Material avec Tailwind CSS
- **Composants réutilisables** : Architecture modulaire
- **Graphiques interactifs** : Recharts pour visualisations
- **Responsive design** : Adaptation mobile et desktop

#### Intégrations
- **API endoflife.date** : Données d'obsolescence automatiques
- **Export CSV** : Génération de rapports
- **Recherche en temps réel** : Filtrage et recherche instantanés

### 🚀 Déploiement Initial
- **URL de production** : https://lnh8imcwwzew.manus.space (version 1.0)
- **Documentation complète** : Technique et utilisateur
- **Tests validés** : Toutes les fonctionnalités opérationnelles

### 📋 Spécifications Techniques
- **Backend** : Python 3.11, Flask, SQLAlchemy, SQLite
- **Frontend** : React 18, Vite, Tailwind CSS, Recharts
- **Déploiement** : Manus Cloud Platform
- **APIs externes** : endoflife.date pour données d'obsolescence



## Version 2.1 - 19 Septembre 2025

### 🎯 Nouvelles Fonctionnalités

#### Script d'Installation Linux
- **Automatisation** : Script `install.sh` pour un déploiement simplifié sur les serveurs Linux.
- **Prérequis** : Vérification automatique des dépendances (Git, Python3, pip, npm, pnpm).
- **Installation complète** : Gère l'installation du backend (venv, dépendances Python, DB) et du frontend (clonage, dépendances Node.js, build, copie des assets).
- **Nettoyage** : Suppression des fichiers temporaires après l'installation.

### 🚀 Déploiement
- **URL de production mise à jour** : https://3dhkilc8wjl6.manus.space
- **Tests validés** : Toutes les fonctionnalités opérationnelles, y compris le filtrage par localisation et l'import Excel.


