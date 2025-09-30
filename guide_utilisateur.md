# Guide Utilisateur - Gestionnaire d'Obsolescence IT

## Introduction

Le Gestionnaire d'Obsolescence IT est une application web qui vous permet de gérer efficacement votre parc informatique et de suivre l'obsolescence de vos équipements, systèmes d'exploitation et applications.

**Accès à l'application** : https://g8h3ilc36nxo.manus.space

## Première Connexion

### Accès à l'Application

1. Ouvrez votre navigateur web
2. Accédez à l'URL : https://g8h3ilc36nxo.manus.space
3. L'application se charge automatiquement avec un compte de démonstration

### Interface Principale

L'interface se compose de :
- **Sidebar gauche** : Navigation principale entre les sections
- **Zone principale** : Contenu de la page active
- **Header** : Titre de la section et actions rapides

## Navigation

### Menu Principal

La sidebar contient 4 sections principales :

🏠 **Tableau de bord** : Vue d'ensemble et statistiques
💻 **Équipements** : Gestion du parc informatique
⚠️ **Obsolescence** : Suivi des dates de fin de vie
👥 **Utilisateurs** : Administration des comptes

### Navigation Mobile

Sur mobile, cliquez sur l'icône menu (☰) pour ouvrir/fermer la sidebar.

## Tableau de Bord

### Vue d'Ensemble

Le tableau de bord affiche :

**Statistiques Clés** :
- Total des équipements
- Équipements actifs
- Équipements obsolètes
- Alertes critiques

**Graphiques** :
- Répartition par type d'équipement (PC, Serveur, Imprimante, Switch)
- État d'obsolescence (À jour, Bientôt obsolète, Obsolète)
- Répartition par localisation

**Alertes Récentes** :
- Notifications d'obsolescence
- Niveaux de priorité (Critique, Attention, Info)
- Équipements concernés

### Actualisation

Cliquez sur le bouton **"Actualiser"** pour mettre à jour les données en temps réel.

## Gestion des Équipements

### Liste des Équipements

#### Affichage

Les équipements sont présentés sous forme de cartes contenant :
- **Nom** et **type** de l'équipement
- **Localisation** précise
- **Adresse IP** (si disponible)
- **Système d'exploitation** et version
- **Date d'acquisition**
- **Applications installées** (badges)
- **Statut** avec badge coloré :
  - 🟢 **Actif** : En fonctionnement
  - 🔴 **Obsolète** : Nécessite une mise à jour
  - ⚪ **En stock** : Non déployé

#### Filtres et Recherche

**Barre de recherche** :
- Recherche par nom d'équipement
- Recherche par localisation
- Recherche par adresse IP
- Recherche par système d'exploitation

**Filtres** :
- **Type** : PC, Serveur, Imprimante, Switch
- **Statut** : Actif, Obsolète, En stock

#### Actions sur les Équipements

**Modifier** (icône crayon) :
- Ouvre le formulaire de modification
- Permet de mettre à jour toutes les informations

**Supprimer** (icône poubelle) :
- Supprime définitivement l'équipement
- Demande une confirmation

### Ajouter un Équipement

#### Accès

Cliquez sur le bouton **"Nouvel équipement"** en haut à droite de la liste.

#### Formulaire d'Ajout

**Informations Générales** (obligatoires) :
- **Nom** : Identifiant unique (ex: PC-001, SRV-001)
- **Type** : Sélection dans la liste (PC, Serveur, Imprimante, Switch, Routeur, Autre)
- **Localisation** : Emplacement précis (ex: Siège Paris - Bureau 101)

**Informations Optionnelles** :
- **Adresse IP** : Format xxx.xxx.xxx.xxx
- **Statut** : Actif (par défaut), Obsolète, En stock, En maintenance

**Système d'Exploitation** :
- **Nom** : Windows, Ubuntu, macOS, etc.
- **Version** : 10 Pro, 20.04 LTS, etc.

**Dates** :
- **Date d'acquisition** : Sélecteur de date
- **Fin de garantie** : Sélecteur de date

**Applications Installées** :
1. Saisissez le nom de l'application
2. Saisissez la version
3. Cliquez sur le bouton **"+"**
4. L'application apparaît dans la liste
5. Cliquez sur **"×"** pour supprimer une application

#### Validation et Sauvegarde

- Les champs obligatoires sont marqués d'un astérisque (*)
- Les erreurs de validation s'affichent en rouge
- Cliquez sur **"Créer"** pour sauvegarder
- Cliquez sur **"Annuler"** pour revenir à la liste

### Modifier un Équipement

1. Dans la liste, cliquez sur l'icône **"Modifier"** (crayon)
2. Le formulaire se pré-remplit avec les données existantes
3. Modifiez les champs souhaités
4. Cliquez sur **"Mettre à jour"** pour sauvegarder

## Suivi de l'Obsolescence

### Vue d'Ensemble

La section Obsolescence présente :

**Statistiques** :
- **Total Produits** : Nombre de produits suivis
- **Obsolètes** : Produits en fin de vie
- **Critiques** : Nécessitent une action immédiate
- **À jour** : Produits supportés

### Liste des Produits

#### Informations Affichées

Pour chaque produit :
- **Nom et version** (ex: Windows 7, Ubuntu 18.04 LTS)
- **Type** : Système d'exploitation ou Application
- **Badge de criticité** :
  - 🔴 **Critique** : Support terminé
  - 🟠 **Obsolète** : Fin de vie atteinte
  - 🟡 **Moyen** : Fin de vie proche
  - 🟢 **Faible** : Support à long terme

#### Détails d'Obsolescence

**Dates importantes** :
- **Date de fin de vie** : Arrêt des mises à jour
- **Fin de support** : Arrêt du support technique
- **Temps restant** : Calcul automatique

**Équipements affectés** :
- Liste des équipements utilisant ce produit
- Nombre total d'équipements concernés

#### Filtres

**Recherche** :
- Par nom de produit
- Par version
- Par équipement affecté

**Statut** :
- Tous les statuts
- Obsolètes uniquement
- Critiques uniquement
- Actifs uniquement

### Actions

**Actualiser** :
- Met à jour toutes les informations d'obsolescence
- Interroge l'API endoflife.date
- Peut prendre quelques minutes

**Exporter** :
- Génère un rapport CSV
- Contient tous les produits filtrés
- Téléchargement automatique

**Voir détails** :
- Affiche les informations complètes
- Historique des mises à jour
- Recommandations de migration

## Gestion des Utilisateurs

### Liste des Utilisateurs

#### Informations Affichées

Pour chaque utilisateur :
- **Photo de profil** (initiale)
- **Nom d'utilisateur**
- **Adresse email**
- **Rôle** avec badge :
  - 🛡️ **Administrateur** : Tous les droits
  - ⚙️ **Manager** : Gestion des équipements
  - 🔧 **Technicien** : Maintenance
  - 👤 **Utilisateur** : Consultation

**Statistiques** :
- **Dernière connexion** : Date et heure
- **Date de création** : Ancienneté du compte
- **Statut** : Actif ou Inactif

#### Actions

**Modifier** (icône crayon) :
- Modification des informations
- Changement de rôle
- Réinitialisation du mot de passe

**Supprimer** (icône poubelle) :
- Suppression du compte
- Impossible pour les administrateurs
- Demande une confirmation

### Ajouter un Utilisateur

#### Formulaire

1. Cliquez sur **"Nouvel utilisateur"**
2. Remplissez les champs :
   - **Nom d'utilisateur** : Identifiant unique
   - **Email** : Adresse email valide
   - **Rôle** : Sélection dans la liste
   - **Mot de passe** : Mot de passe temporaire
3. Cliquez sur **"Créer l'utilisateur"**

#### Rôles et Permissions

**Administrateur** :
- Gestion complète des utilisateurs
- Accès à toutes les fonctionnalités
- Configuration système

**Manager** :
- Gestion des équipements
- Consultation des rapports
- Gestion des utilisateurs standards

**Technicien** :
- Gestion des équipements
- Mise à jour des informations techniques
- Consultation de l'obsolescence

**Utilisateur** :
- Consultation uniquement
- Accès au tableau de bord
- Visualisation des équipements

## Conseils d'Utilisation

### Bonnes Pratiques

**Gestion des Équipements** :
- Utilisez une nomenclature cohérente (PC-001, SRV-001)
- Mettez à jour régulièrement les informations
- Documentez les applications installées

**Suivi de l'Obsolescence** :
- Consultez régulièrement les alertes
- Planifiez les migrations avant les dates critiques
- Exportez les rapports pour la planification

**Administration** :
- Attribuez les rôles appropriés
- Surveillez les connexions utilisateurs
- Maintenez les comptes à jour

### Automatisation

**Mise à jour automatique** :
- L'application vérifie automatiquement l'obsolescence
- Les données sont mises à jour quotidiennement
- Les alertes critiques sont prioritaires

**Notifications** :
- Les alertes apparaissent sur le tableau de bord
- Les équipements obsolètes sont mis en évidence
- Les rapports peuvent être exportés régulièrement

## Dépannage

### Problèmes Courants

**L'application ne se charge pas** :
- Vérifiez votre connexion internet
- Actualisez la page (F5)
- Videz le cache du navigateur

**Les données ne s'affichent pas** :
- Cliquez sur "Actualiser"
- Vérifiez les filtres appliqués
- Contactez l'administrateur

**Erreur lors de la sauvegarde** :
- Vérifiez les champs obligatoires
- Respectez les formats demandés
- Réessayez après quelques secondes

### Support

Pour toute assistance :
- Consultez cette documentation
- Contactez votre administrateur système
- Vérifiez les messages d'erreur affichés

## Raccourcis Clavier

- **Ctrl + R** : Actualiser la page
- **Échap** : Fermer les modales
- **Tab** : Navigation dans les formulaires
- **Entrée** : Valider les formulaires

## Compatibilité

**Navigateurs supportés** :
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Appareils** :
- Ordinateurs de bureau
- Tablettes
- Smartphones (interface adaptée)

L'application est optimisée pour tous les écrans et s'adapte automatiquement à la taille de votre appareil.


## Nouvelles Fonctionnalités (Version 2.0)

### Filtrage par Localisation

#### Accès à la Fonctionnalité
1. Rendez-vous sur le **Tableau de bord**
2. Localisez le dropdown **"Toutes les localisations"** en haut à droite
3. Sélectionnez une localisation spécifique dans la liste

#### Utilisation
- **Filtrage global** : Tous les graphiques et statistiques se mettent à jour selon la localisation sélectionnée
- **Indicateur visuel** : Un badge bleu indique qu'un filtre est actif
- **Suppression du filtre** : Cliquez sur "Supprimer le filtre" ou sélectionnez "Toutes les localisations"

### Import Excel des Équipements

#### Préparation du Fichier Excel

##### Format Requis
Votre fichier Excel doit contenir les colonnes suivantes :

**Colonnes Obligatoires :**
- **Salle** : Localisation de l'équipement (ex: "Siège Paris - Bureau 101")
- **Nom PC** : Nom unique de l'équipement (ex: "PC-001", "SRV-001")

**Colonnes Optionnelles :**
- **Description  (Alias)** : Description ou alias de l'équipement
- **Marque** : Marque du fabricant
- **N° modèle** : Numéro de modèle
- **Système d'exploitation PC** : OS installé
- **Application** : Application principale installée
- **Version** : Version de l'application
- **Connecté au réseau O/N** : Connexion réseau (O/N)
- **Sauvegardé sur réseau RLS O/N** : Sauvegarde RLS (O/N)
- **Adresse IP** : Adresse IP de l'équipement
- **A sauvegarder O/N** : Nécessite sauvegarde (O/N)
- **Fournisseur matériel** : Nom du fournisseur

#### Processus d'Import

##### Étape 1 : Accès à l'Import
1. Naviguez vers la page **Équipements**
2. Cliquez sur le bouton **"Import Excel"** (icône upload)

##### Étape 2 : Téléchargement du Modèle
1. Dans la modal d'import, cliquez sur **"Télécharger le modèle Excel"**
2. Utilisez ce fichier comme base pour vos données

##### Étape 3 : Sélection du Fichier
- **Glisser-déposer** : Faites glisser votre fichier Excel dans la zone prévue
- **Sélection manuelle** : Cliquez sur "Sélectionner un fichier"
- **Formats acceptés** : .xlsx et .xls uniquement

##### Étape 4 : Import et Validation
1. Cliquez sur **"Importer"**
2. L'application valide automatiquement les données
3. Consultez le rapport d'import avec statistiques et erreurs

#### Règles de Validation

##### Détection Automatique du Type
- **PC** : Par défaut
- **Serveur** : Nom contenant "srv" ou "server"
- **Imprimante** : Nom contenant "imp" ou "print"
- **Switch** : Nom contenant "sw" ou "switch"
- **Machine laboratoire** : Nom contenant "lab" ou "machine"

### Conseils d'Utilisation

#### Pour le Filtrage
- Utilisez le filtre pour analyser des sites spécifiques
- Alternez entre vue globale et locale pour identifier les tendances

#### Pour l'Import Excel
- Utilisez toujours le modèle fourni comme base
- Vérifiez vos données dans Excel avant import
- Assurez-vous que chaque équipement a un nom unique
- Testez avec un petit échantillon d'abord pour de gros volumes

