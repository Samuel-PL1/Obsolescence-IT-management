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
- `GUNICORN_BIND` : adresse d'écoute de Gunicorn (`unix:/run/obsolescence/app.sock` par défaut). Sur Plesk, utilisez plutôt une socket TCP interne (`127.0.0.1:8050` par exemple) pour la mettre derrière le proxy web natif.

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

## 8. Intégration à Odin/Plesk

Plesk (anciennement Odin) fournit un proxy Apache/Nginx devant vos applications. Pour intégrer l'API :

1. **Choisissez le bon utilisateur** : chaque abonnement Plesk possède un utilisateur système (ex. `example`). Passez son nom au
   script d'installation pour éviter de créer un compte supplémentaire :

   ```bash
   sudo APP_USER=example APP_GROUP=psacln APP_HOME=/var/www/vhosts/example.com/obsolescence \
        ./scripts/install_server.sh
   ```

   Cela installe l'application dans l'espace du domaine tout en conservant les permissions attendues par Plesk. Pensez à
   ajuster `WorkingDirectory`, `EnvironmentFile` et `ExecStart` dans l'unité `systemd` pour refléter ce chemin personnalisé.

2. **Exposez Gunicorn en TCP** : modifiez le fichier `.env` pour définir `GUNICORN_BIND=127.0.0.1:8050`, puis rechargez le service
   (`sudo systemctl restart obsolescence.service`). Le port reste privé car seul Apache/Nginx y accède.

3. **Ajoutez les directives proxy** : dans Plesk, ouvrez **Sites web & Domaines → Paramètres Apache & nginx** du domaine concerné
   puis ajoutez :

   - *Directives Apache supplémentaires* :

     ```apache
     ProxyPreserveHost On
     ProxyPass / http://127.0.0.1:8050/
     ProxyPassReverse / http://127.0.0.1:8050/
     ```

   - *Directives nginx supplémentaires* (mode proxy activé) :

     ```nginx
     location / {
         proxy_pass http://127.0.0.1:8050/;
         proxy_set_header Host $host;
         proxy_set_header X-Real-IP $remote_addr;
         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
         proxy_set_header X-Forwarded-Proto $scheme;
     }
     ```

   Validez puis redémarrez le domaine. Plesk se charge de recharger Apache/Nginx.

4. **Sécurité & supervision** : Plesk autorise également la création d'une tâche planifiée pour redémarrer le service ou exécuter
   `flask --app src.main upgrade-db`. Utilisez `journalctl -u obsolescence.service` ou l'onglet **Journaux** de Plesk pour
   consulter l'activité.

5. **Certificat TLS** : gérez le certificat Let’s Encrypt depuis Plesk ; Apache/Nginx terminent le TLS avant de proxyfier vers
   Gunicorn.

Ces étapes permettent d'exploiter l'application au sein d'un environnement Plesk standard tout en conservant la gestion via
`systemd` et le script d'installation fourni.
