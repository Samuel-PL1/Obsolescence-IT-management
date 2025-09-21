"""WSGI entrypoint used by production servers such as Gunicorn."""

from src.main import create_app

app = create_app()
