from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    equipment_type = db.Column(db.String(50), nullable=False)  # PC, Server, Printer, etc.
    location = db.Column(db.String(200), nullable=False)  # Site, Building, Room
    ip_address = db.Column(db.String(15), nullable=True)
    os_name = db.Column(db.String(100), nullable=True)
    os_version = db.Column(db.String(50), nullable=True)
    acquisition_date = db.Column(db.Date, nullable=True)
    warranty_end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='Active')  # Active, Obsolete, In Stock, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relation avec les applications installées
    applications = db.relationship('Application', backref='equipment', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Equipment {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'equipment_type': self.equipment_type,
            'location': self.location,
            'ip_address': self.ip_address,
            'os_name': self.os_name,
            'os_version': self.os_version,
            'acquisition_date': self.acquisition_date.isoformat() if self.acquisition_date else None,
            'warranty_end_date': self.warranty_end_date.isoformat() if self.warranty_end_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'applications': [app.to_dict() for app in self.applications]
        }

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Application {self.name} {self.version}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'equipment_id': self.equipment_id,
            'created_at': self.created_at.isoformat()
        }

class ObsolescenceInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    product_type = db.Column(db.String(20), nullable=False)  # 'os' or 'application'
    version = db.Column(db.String(50), nullable=False)
    eol_date = db.Column(db.Date, nullable=True)
    support_end_date = db.Column(db.Date, nullable=True)
    is_obsolete = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ObsolescenceInfo {self.product_name} {self.version}>'

    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'product_type': self.product_type,
            'version': self.version,
            'eol_date': self.eol_date.isoformat() if self.eol_date else None,
            'support_end_date': self.support_end_date.isoformat() if self.support_end_date else None,
            'is_obsolete': self.is_obsolete,
            'last_updated': self.last_updated.isoformat()
        }

