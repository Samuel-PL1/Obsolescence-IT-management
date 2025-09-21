import os
import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv
from flask import Flask, send_from_directory
from flask_cors import CORS

# Ensure the project root is available on the Python path when executed directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models.user import db  # noqa: E402  (import after path adjustment)
from src.routes.equipment import equipment_bp  # noqa: E402
from src.routes.obsolescence import obsolescence_bp  # noqa: E402
from src.routes.user import user_bp  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_STATIC_FOLDER = BASE_DIR / "static"
DEFAULT_DATABASE_PATH = BASE_DIR / "database" / "app.db"


def _load_environment(env_file: Optional[str]) -> None:
    """Load environment variables from .env if available."""
    if env_file:
        load_dotenv(env_file)
        return

    default_env = PROJECT_ROOT / ".env"
    if default_env.exists():
        load_dotenv(default_env)


def create_app() -> Flask:
    """Application factory used by both the CLI and WSGI servers."""
    _load_environment(os.environ.get("APP_ENV_FILE"))

    app = Flask(__name__, static_folder=str(DEFAULT_STATIC_FOLDER))

    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        # Fallback to a deterministic key to avoid crashes but warn loudly.
        secret_key = "change-me"
        app.logger.warning(
            "SECRET_KEY is not defined. Generate one and store it in the .env file."
        )
    app.config["SECRET_KEY"] = secret_key

    database_path = os.environ.get("DATABASE_PATH", os.fspath(DEFAULT_DATABASE_PATH))
    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Default to production settings when not explicitly defined.
    os.environ.setdefault("FLASK_ENV", "production")

    CORS(app)

    app.register_blueprint(user_bp, url_prefix="/api")
    app.register_blueprint(equipment_bp, url_prefix="/api")
    app.register_blueprint(obsolescence_bp, url_prefix="/api")

    db.init_app(app)

    _register_routes(app)
    _register_cli_commands(app)

    return app


def _register_routes(app: Flask) -> None:
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve(path: str):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        candidate = Path(static_folder_path) / path
        if path and candidate.exists():
            return send_from_directory(static_folder_path, path)

        index_path = Path(static_folder_path) / "index.html"
        if index_path.exists():
            return send_from_directory(static_folder_path, "index.html")

        return "index.html not found", 404


def _register_cli_commands(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db_command() -> None:
        """Initialise la base de données SQLite si elle n'existe pas."""
        with app.app_context():
            db.create_all()
        click.echo("Base de données initialisée.")

    @app.cli.command("upgrade-db")
    def upgrade_db_command() -> None:
        """Applique les mises à jour du schéma (create_all sur les nouveaux modèles)."""
        with app.app_context():
            db.create_all()
        click.echo("Schéma de base de données mis à jour.")


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
