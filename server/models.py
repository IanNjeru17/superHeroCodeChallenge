from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    super_name = db.Column(db.String, nullable=False)

    # Relationship with HeroPower
    hero_powers = db.relationship('HeroPower', backref='hero', cascade='all, delete-orphan')
    powers = association_proxy('hero_powers', 'power')

    serialize_rules = ('-hero_powers.hero',)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "super_name": self.super_name,
            "hero_powers": [hero_power.to_dict() for hero_power in self.hero_powers],
            "powers": [power.to_dict() for power in self.powers]
        }

    def __repr__(self):
        return f'<Hero {self.id}: {self.name}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

    # Relationship with HeroPower
    hero_powers = db.relationship('HeroPower', backref='power', cascade='all, delete-orphan')

    # Validation for description length
    @validates('description')
    def validate_description(self, key, value):
        if len(value) < 20:
            raise ValueError("Description must be at least 20 characters long.")
        return value

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }

    def __repr__(self):
        return f'<Power {self.id}: {self.name}>'

# HeroPower Model (Join Table)
class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'))
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'))

    
    serialize_only = ('id', 'strength', 'hero_id', 'power_id')

    @validates('strength')
    def validate_strength(self, key, value):
        if value not in ['Strong', 'Weak', 'Average']:
            raise ValueError("validation errors")
        return value

    def to_dict(self):
        return {
            "id": self.id,
            "strength": self.strength,
            "hero_id": self.hero_id,
            "power": self.power.to_dict() 
        }

    def __repr__(self):
        return f'<HeroPower {self.id}: Hero {self.hero_id}, Power {self.power_id} - {self.strength}>'
