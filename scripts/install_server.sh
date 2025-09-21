#!/usr/bin/env bash
set -euo pipefail

APP_USER=${APP_USER:-obsolescence}
APP_GROUP=${APP_GROUP:-$APP_USER}
APP_HOME=${APP_HOME:-$(pwd)}
VENV_DIR=${VENV_DIR:-$APP_HOME/venv}
ENV_FILE=${ENV_FILE:-$APP_HOME/.env}
REQUIREMENTS_FILE=${REQUIREMENTS_FILE:-$APP_HOME/requirements.txt}
PYTHON_BIN=${PYTHON_BIN:-python3}
LOG_DIR=${LOG_DIR:-/var/log/obsolescence}

umask 027

ensure_root() {
    if [[ "${EUID}" -ne 0 ]]; then
        echo "Ce script doit être exécuté avec les privilèges administrateur (root)." >&2
        exit 1
    fi
}

install_system_packages() {
    if command -v apt-get >/dev/null 2>&1; then
        apt-get update -y
        apt-get install -y python3 python3-venv python3-pip sqlite3
    elif command -v dnf >/dev/null 2>&1; then
        dnf install -y python3 python3-venv python3-pip sqlite
    else
        echo "Gestionnaire de paquets inconnu. Installez Python 3, pip, venv et SQLite manuellement." >&2
    fi
}

ensure_group() {
    if ! getent group "${APP_GROUP}" >/dev/null 2>&1; then
        groupadd --system "${APP_GROUP}"
    fi
}

ensure_user() {
    if ! id "${APP_USER}" >/dev/null 2>&1; then
        useradd --system --gid "${APP_GROUP}" --shell /usr/sbin/nologin --create-home "${APP_USER}"
    fi
}

create_directories() {
    mkdir -p "${APP_HOME}"
    chown -R "${APP_USER}:${APP_GROUP}" "${APP_HOME}"

    mkdir -p "${LOG_DIR}"
    touch "${LOG_DIR}/access.log" "${LOG_DIR}/error.log"
    chown -R "${APP_USER}:${APP_GROUP}" "${LOG_DIR}"
    chmod 750 "${LOG_DIR}"
}

create_virtualenv() {
    local python_path
    python_path=$(command -v "${PYTHON_BIN}" || true)
    if [[ -z "${python_path}" ]]; then
        echo "Python binaire introuvable : ${PYTHON_BIN}." >&2
        exit 1
    fi

    if [[ ! -d "${VENV_DIR}" ]]; then
        "${python_path}" -m venv "${VENV_DIR}"
    fi

    "${VENV_DIR}/bin/pip" install --upgrade pip setuptools wheel
    if [[ -f "${REQUIREMENTS_FILE}" ]]; then
        "${VENV_DIR}/bin/pip" install -r "${REQUIREMENTS_FILE}"
    else
        echo "Fichier requirements introuvable : ${REQUIREMENTS_FILE}." >&2
        exit 1
    fi

    chown -R "${APP_USER}:${APP_GROUP}" "${VENV_DIR}"
}

append_env_value() {
    local key="$1"
    local value="$2"
    if ! grep -q "^${key}=" "${ENV_FILE}" 2>/dev/null; then
        echo "${key}=${value}" >>"${ENV_FILE}"
    fi
}

write_env_file() {
    if [[ ! -f "${ENV_FILE}" ]]; then
        touch "${ENV_FILE}"
        chmod 640 "${ENV_FILE}"
    fi

    local secret_key
    if ! grep -q '^SECRET_KEY=' "${ENV_FILE}" 2>/dev/null; then
        secret_key="$("${PYTHON_BIN}" - <<'PY'
import secrets
print(secrets.token_urlsafe(64))
PY
)"
        append_env_value "SECRET_KEY" "${secret_key}"
    fi

    append_env_value "FLASK_ENV" "production"
    append_env_value "DATABASE_PATH" "${APP_HOME}/src/database/app.db"

    chown "${APP_USER}:${APP_GROUP}" "${ENV_FILE}"
}

print_summary() {
    cat <<SUMMARY
Installation terminée.

Utilisateur système : ${APP_USER}
Répertoire de l'application : ${APP_HOME}
Environnement virtuel : ${VENV_DIR}
Fichier d'environnement : ${ENV_FILE}
Logs applicatifs : ${LOG_DIR}/(access.log|error.log)

Pensez à :
  - Déployer le service systemd (voir README-deploiement.md).
  - Exécuter "sudo -u ${APP_USER} ${VENV_DIR}/bin/flask --app src.main init-db" avant le premier démarrage.
SUMMARY
}

main() {
    ensure_root
    install_system_packages
    ensure_group
    ensure_user
    create_directories
    create_virtualenv
    write_env_file
    print_summary
}

main "$@"
