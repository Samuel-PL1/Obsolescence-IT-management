"""
Modèle de base de données pour les informations d'obsolescence
"""
from src.database import db
from datetime import datetime

class ObsolescenceInfo(db.Model):
    __tablename__ = 'obsolescence_info'
    
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    version = db.Column(db.String(100), nullable=True)
    product_type = db.Column(db.String(50), nullable=False)  # 'OS' ou 'Application'
    
    # Dates d'obsolescence
    eol_date = db.Column(db.Date, nullable=True)  # End of Life
    support_end_date = db.Column(db.Date, nullable=True)  # Fin de support
    
    # Statut et criticité
    status = db.Column(db.String(20), nullable=False, default='Unknown')  # Low, Medium, High, Critical, Unknown
    
    # Équipements affectés
    equipment_names = db.Column(db.Text, nullable=True)  # Liste des noms d'équipements séparés par virgules
    
    # Métadonnées
    source = db.Column(db.String(100), nullable=True)  # endoflife.date, AI Estimation, Manual
    confidence = db.Column(db.String(20), nullable=True, default='Medium')  # Low, Medium, High
    recommendation = db.Column(db.Text, nullable=True)
    
    # Timestamps
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ObsolescenceInfo {self.product_name} {self.version}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'version': self.version,
            'product_type': self.product_type,
            'eol_date': self.eol_date.isoformat() if self.eol_date else None,
            'support_end_date': self.support_end_date.isoformat() if self.support_end_date else None,
            'status': self.status,
            'equipment_names': self.equipment_names.split(',') if self.equipment_names else [],
            'source': self.source,
            'confidence': self.confidence,
            'recommendation': self.recommendation,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @property
    def equipment_count(self):
        """Retourne le nombre d'équipements affectés"""
        if not self.equipment_names:
            return 0
        return len(self.equipment_names.split(','))
    
    @property
    def is_critical(self):
        """Retourne True si le produit est critique"""
        return self.status in ['Critical', 'High']
    
    @property
    def days_until_eol(self):
        """Retourne le nombre de jours jusqu'à la fin de vie"""
        if not self.eol_date:
            return None
        
        today = datetime.now().date()
        delta = self.eol_date - today
        return delta.days
    
    @classmethod
    def get_critical_products(cls):
        """Retourne tous les produits critiques"""
        return cls.query.filter(cls.status.in_(['Critical', 'High'])).all()
    
    @classmethod
    def get_by_type(cls, product_type):
        """Retourne tous les produits d'un type donné"""
        return cls.query.filter_by(product_type=product_type).all()
    
    @classmethod
    def get_obsolete_count(cls):
        """Retourne le nombre de produits obsolètes"""
        return cls.query.filter_by(status='Critical').count()
    
    @classmethod
    def get_stats(cls):
        """Retourne les statistiques d'obsolescence"""
        total = cls.query.count()
        critical = cls.query.filter_by(status='Critical').count()
        high = cls.query.filter_by(status='High').count()
        medium = cls.query.filter_by(status='Medium').count()
        low = cls.query.filter_by(status='Low').count()
        
        return {
            'total': total,
            'critical': critical,
            'high': high,
            'medium': medium,
            'low': low,
            'obsolescence_rate': round((critical / total * 100), 1) if total > 0 else 0
        }
