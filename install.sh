#!/bin/bash

# Script d'installation pour l'application de gestion de l'obsolescence IT

# --- Configuration ---
BACKEND_DIR="$(pwd)"
FRONTEND_REPO="https://github.com/Samuel-PL1/Obsolescence-IT-management-frontend.git"
FRONTEND_DIR="/tmp/it-obsolescence-frontend-temp"

# --- Fonctions utilitaires ---
log_info() { echo -e "\e[32mINFO: $1\e[0m"; }
log_warn() { echo -e "\e[33mWARN: $1\e[0m"; }
log_error() { echo -e "\e[31mERROR: $1\e[0m"; exit 1; }

check_command() {
    command -v "$1" >/dev/null 2>&1 || log_error "Le programme '$1' n'est pas installé. Veuillez l'installer et réessayer."
}

# --- Vérification des prérequis ---
log_info "Vérification des prérequis..."
check_command "git"
check_command "python3"
check_command "pip"
check_command "npm" # Pour le frontend
check_command "pnpm" # Pour le frontend

# --- Installation du Backend ---
log_info "Installation du backend Flask..."
cd "$BACKEND_DIR" || log_error "Impossible de naviguer vers le répertoire du backend."

# Création et activation de l'environnement virtuel
if [ ! -d "venv" ]; then
    log_info "Création de l'environnement virtuel..."
    python3 -m venv venv || log_error "Échec de la création de l'environnement virtuel."
fi
source venv/bin/activate || log_error "Échec de l'activation de l'environnement virtuel."

# Installation des dépendances Python
log_info "Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt || log_error "Échec de l'installation des dépendances Python."

# Initialisation de la base de données
log_info "Initialisation de la base de données..."
python3 src/init_db.py || log_error "Échec de l'initialisation de la base de données."

# --- Installation du Frontend ---
log_info "Installation du frontend React..."

# Cloner le dépôt frontend dans un répertoire temporaire
if [ -d "$FRONTEND_DIR" ]; then
    log_warn "Le répertoire temporaire du frontend existe déjà. Suppression..."
    rm -rf "$FRONTEND_DIR"
fi
git clone "$FRONTEND_REPO" "$FRONTEND_DIR" || log_error "Échec du clonage du dépôt frontend."
cd "$FRONTEND_DIR" || log_error "Impossible de naviguer vers le répertoire temporaire du frontend."

# Installation des dépendances Node.js et build
log_info "Installation des dépendances Node.js (pnpm install)..."
pnpm install || log_error "Échec de l'installation des dépendances Node.js."

log_info "Construction du frontend (pnpm build)..."
pnpm run build || log_error "Échec de la construction du frontend."

# --- Copie du Frontend vers le Backend ---
log_info "Copie des fichiers du frontend vers le répertoire static du backend..."
rm -rf "$BACKEND_DIR/src/static/*" # Nettoyer le répertoire static existant
cp -r "$FRONTEND_DIR/dist/"* "$BACKEND_DIR/src/static/" || log_error "Échec de la copie des fichiers du frontend."

# --- Nettoyage ---
log_info "Nettoyage des fichiers temporaires du frontend..."
rm -rf "$FRONTEND_DIR"

# --- Finalisation ---
log_info "Installation terminée avec succès !"
log_info "Pour démarrer l'application, naviguez vers le répertoire du backend et exécutez :"
log_info "  cd $BACKEND_DIR"
log_info "  source venv/bin/activate"
log_info "  python3 src/main.py"
log_info "L'application sera accessible sur http://127.0.0.1:5000 (ou le port configuré)."
log_info "N'oubliez pas de configurer un serveur web comme Nginx ou Apache pour servir l'application en production."


