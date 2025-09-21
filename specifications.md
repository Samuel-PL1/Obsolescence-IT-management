# Spécifications de l'application de gestion de l'obsolescence

## 1. Objectif
Développer une application web pour gérer l'obsolescence d'un parc informatique, en permettant le suivi des matériels, des systèmes d'exploitation et des applications, ainsi que la visualisation des données via un tableau de bord.

## 2. Fonctionnalités clés

### 2.1. Gestion des accès et Authentification
*   **Authentification locale:** Permettre la création et la gestion de comptes utilisateurs directement dans l'application.
*   **Authentification Active Directory (AD):** Intégration avec un annuaire AD pour l'authentification des utilisateurs existants.
*   **Gestion des rôles:** Définir des rôles (ex: Administrateur, Utilisateur) avec des permissions différentes.

### 2.2. Interface d'Administration
*   **Gestion des comptes:**
    *   Création, modification, suppression de comptes utilisateurs (locaux).
    *   Attribution de rôles.
    *   Réinitialisation de mots de passe.
*   **Gestion des entrées matériels:**
    *   Ajout, modification, suppression de matériels (PC, serveurs, machines spécifiques).
    *   Champs pour chaque matériel:
        *   Nom/Identifiant unique
        *   Type de matériel (PC, Serveur, Imprimante, etc.)
        *   Localisation (Site, Bâtiment, Salle)
        *   Adresse IP
        *   Système d'exploitation (OS) et sa version
        *   Liste des applications installées et leurs versions
        *   Date d'acquisition
        *   Date de fin de garantie/support
        *   Statut (Actif, Obsolète, En stock, etc.)
    *   Possibilité d'attacher des documents (factures, licences).

### 2.3. Gestion de l'Obsolescence
*   **Recherche automatique:** L'application doit pouvoir rechercher et mettre à jour les informations d'obsolescence pour les OS et les applications listées.
    *   Sources potentielles: Sites officiels des éditeurs, bases de données publiques (CVE, EOL dates).
    *   Fréquence de mise à jour configurable.
*   **Notification:** Alerte en cas d'obsolescence proche ou avérée.

### 2.4. Tableau de Bord (Page d'accueil)
*   **Visualisation graphique:** Affichage de graphiques récapitulatifs.
    *   Nombre de matériels par type.
    *   Répartition des OS par version.
    *   Statut d'obsolescence des OS et applications (ex: nombre d'OS obsolètes, applications critiques obsolètes).
    *   Matériels par localisation/site.
*   **Filtres:** Possibilité de filtrer les données affichées par:
    *   Type de matériel
    *   Localisation/Site
    *   Statut d'obsolescence (OS, applications)
    *   Date d'acquisition/fin de support

## 3. Architecture Technique Proposée
*   **Backend:** Flask (Python) pour la logique métier, les APIs RESTful et l'intégration AD.
*   **Base de données:** PostgreSQL (ou SQLite pour un démarrage rapide, puis migration).
*   **Frontend:** React (JavaScript) pour une interface utilisateur dynamique et réactive.
*   **Authentification AD:** Utilisation de bibliothèques Python pour l'intégration LDAP/AD.
*   **Recherche d'obsolescence:** Modules Python pour le web scraping ou l'interrogation d'APIs externes.
*   **Graphiques:** Libraries JavaScript comme Chart.js ou D3.js.

## 4. Suggestions et Automatisations
*   **Import/Export:** Fonctionnalité d'importation/exportation des données matériels (CSV, Excel).
*   **Inventaire automatique:** Possibilité d'intégrer des outils d'inventaire réseau existants (si applicable).
*   **Rapports:** Génération de rapports personnalisables sur l'état du parc.
*   **Historique:** Suivi des modifications apportées aux entrées matériels.

## 5. Étapes Suivantes (Réalisées)
1.  Recherche d'APIs et sources de données pour l'obsolescence.
2.  Mise en place de l'environnement de développement backend.
3.  Développement du module d'authentification.
4.  Développement du frontend React.
5.  Intégration des graphiques et tableau de bord.
6.  Implémentation du filtre de localisation pour le tableau de bord.
7.  Développement de la fonctionnalité d'import Excel.
8.  Tests et déploiement de l'application.
9.  Création du script d'installation Linux.

## 6. Déploiement Actuel

L'application est déployée et accessible à l'adresse : https://3dhkilc8wjl6.manus.space

Un script d'installation `install.sh` est disponible à la racine du dépôt backend pour faciliter le déploiement sur un serveur Linux.

