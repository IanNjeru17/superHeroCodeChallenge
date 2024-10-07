#!/usr/bin/env python3

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize the Flask app and its configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize database and migrations
migrate = Migrate(app, db)

db.init_app(app)

# Root route
@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    hero_data = [{
        'id': hero.id,
        'name': hero.name,
        'super_name': hero.super_name
    } for hero in heroes]
    return jsonify(hero_data)

# Get hero by ID
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    try:
        hero = Hero.query.get(id)
        if hero:
            return jsonify(hero.to_dict(include_hero_powers=True)), 200
        else:
            return jsonify({"error": "Hero not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get all powers
@app.route('/powers', methods=['GET'])
def get_powers():
    try:
        powers = Power.query.all()
        return jsonify([power.to_dict() for power in powers]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get by ID
@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    try:
        power = Power.query.get(id)
        if power:
            return jsonify(power.to_dict()), 200
        else:
            return jsonify({"error": "Power not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# new power
@app.route('/powers', methods=['POST'])
def create_power():
    data = request.get_json()
    if 'description' not in data:
        return jsonify({"error": "Description is required"}), 400
    if not isinstance(data['description'], str) or len(data['description']) < 20:
        return jsonify({"error": "Description must be a string of at least 20 characters long"}), 400

    power = Power(description=data['description'])
    db.session.add(power)
    db.session.commit()
    return jsonify(power.to_dict()), 201
# update power
@app.route('/powers/<int:power_id>', methods=['PATCH'])
def update_power(power_id):
    power = Power.query.get(power_id)
    if power:
        try:
            data = request.get_json()
            power.description = data.get('description')
            db.session.commit()
            return jsonify({
                'id': power.id,
                'name': power.name,
                'description': power.description
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'errors': ['Validation errors']}), 400
    else:
        return jsonify({'error': 'Power not found'}), 404

# Create new hero-power
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()

    if 'strength' not in data or 'hero_id' not in data or 'power_id' not in data:
        return jsonify({"errors": ["validation errors"]}), 400
    
    if data['strength'] not in ['Strong', 'Weak', 'Average']:
        return jsonify({"error": "validation errors"}), 400

    try:
        hero_power = HeroPower(
            strength=data['strength'],
            hero_id=data['hero_id'],
            power_id=data['power_id']
        )
        db.session.add(hero_power)
        db.session.commit()
        return jsonify(hero_power.to_dict()), 201
    except Exception as e:
        return jsonify({"errors": [str(e)]}), 400


if __name__ == '__main__':
    app.run(port=5555, debug=True)
