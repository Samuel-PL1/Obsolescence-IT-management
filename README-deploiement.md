# Guide de déploiement

Ce document décrit une procédure d'installation et d'exploitation de l'API **Obsolescence IT Management** sur un serveur Linux en production.

## 1. Pré-requis

- Accès administrateur (root ou sudo) sur le serveur cible.
- Distribution Linux compatible `systemd` (Debian/Ubuntu, Rocky/Alma, etc.).
- Un serveur web ou un reverse-proxy (ex. Nginx) configuré pour exposer le socket Unix `/run/obsolescence/app.sock` si nécessaire.

## 2. Installation automatisée

1. Copiez ou clonez le dépôt dans le répertoire cible (par défaut `/opt/obsolescence`).
2. Exécutez le script d'installation :

   ```bash
   cd /opt/obsolescence
   sudo ./scripts/install_server.sh
   ```

   Variables optionnelles :

   | Variable | Valeur par défaut | Description |
   |----------|-------------------|-------------|
   | `APP_USER` | `obsolescence` | Utilisateur système exécutant l'application. |
   | `APP_GROUP` | `obsolescence` | Groupe associé. |
   | `APP_HOME` | `pwd` | Répertoire de déploiement (doit contenir le code). |
   | `VENV_DIR` | `$APP_HOME/venv` | Dossier du virtualenv. |
   | `ENV_FILE` | `$APP_HOME/.env` | Fichier d'environnement utilisé par l'app. |
   | `LOG_DIR` | `/var/log/obsolescence` | Emplacement des journaux applicatifs. |

   Le script :

   - crée l'utilisateur/groupe système si nécessaire ;
   - installe Python 3, `venv`, `pip` et SQLite (via `apt` ou `dnf`) ;
   - crée un environnement virtuel et installe les dépendances depuis `requirements.txt` ;
   - génère un fichier `.env` avec les variables essentielles (`SECRET_KEY`, `FLASK_ENV`, `DATABASE_PATH`) ;
   - prépare les dossiers de logs (`/var/log/obsolescence`).

## 3. Configuration de l'environnement

Le fichier `.env` généré peut être ajusté selon vos besoins. Variables principales :

- `SECRET_KEY` : clé secrète Flask (générée automatiquement, à conserver secrète) ;
- `FLASK_ENV` : laisser `production` en environnement serveur ;
- `DATABASE_PATH` : chemin du fichier SQLite. Exemple par défaut : `/opt/obsolescence/src/database/app.db`.

Ajoutez vos propres variables si nécessaire (ex. paramètres SMTP, URL externes…).

## 4. Initialisation et mise à jour de la base de données

Avant le premier démarrage (et après chaque modification du schéma), exécutez :

```bash
sudo -u obsolescence /opt/obsolescence/venv/bin/flask --app src.main init-db
```

Pour réappliquer les définitions de modèles après une mise à jour de code :

```bash
sudo -u obsolescence /opt/obsolescence/venv/bin/flask --app src.main upgrade-db
```

Les deux commandes s'appuient sur les blueprints de l'application et garantissent la création des tables nécessaires.

## 5. Service systemd

Un exemple d'unité est fourni dans `deploy/systemd/obsolescence.service`. Adaptez les chemins si votre installation diffère, puis copiez le fichier :

```bash
sudo cp deploy/systemd/obsolescence.service /etc/systemd/system/obsolescence.service
sudo systemctl daemon-reload
sudo systemctl enable obsolescence.service
```

### Démarrage / arrêt / statut

```bash
sudo systemctl start obsolescence.service
sudo systemctl status obsolescence.service
sudo systemctl restart obsolescence.service  # pour redéployer
sudo systemctl stop obsolescence.service
```

### Journaux et rotation

- Journaux applicatifs : `/var/log/obsolescence/access.log` et `/var/log/obsolescence/error.log` (écrits par Gunicorn).
- Journaux système : `journalctl -u obsolescence.service -f`.
- Une configuration `logrotate` est fournie (`deploy/logrotate/obsolescence`). Pour l'activer :

  ```bash
  sudo cp deploy/logrotate/obsolescence /etc/logrotate.d/obsolescence
  sudo logrotate -f /etc/logrotate.d/obsolescence  # test manuel
  ```

Cette configuration effectue une rotation hebdomadaire, conserve 12 archives et envoie `SIGHUP` au service pour rouvrir les fichiers.

## 6. Mise à jour de l'application

1. Positionnez-vous dans le répertoire de déploiement et récupérez les dernières modifications (`git pull` ou copie du nouveau paquet).
2. Réexécutez le script `install_server.sh` si de nouvelles dépendances ont été ajoutées (idempotent pour la plupart des opérations).
3. Mettez à jour la base si besoin (`upgrade-db`).
4. Redémarrez le service : `sudo systemctl restart obsolescence.service`.

## 7. Vérification du service

- Vérifier que le socket Unix est présent : `ls -l /run/obsolescence/app.sock`.
- Tester l'API via `curl --unix-socket /run/obsolescence/app.sock http://localhost/api/health` (adapter au point de terminaison disponible).

Pour toute personnalisation (nombre de workers Gunicorn, logs JSON, base externe…), modifiez l'unité `systemd` et/ou le fichier `.env` en conséquence.
