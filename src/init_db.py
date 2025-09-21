from models.equipment import db
from main import app

with app.app_context():
    db.create_all()
    print("Database initialized!")

