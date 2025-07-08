"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, Blueprint
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Character, Planet, User, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

api = Blueprint('api', __name__)

#People
@api.route('/people', methods=['GET'])
def get_all_people():
    characters = Character.query.all()
    return jsonify([character.serialize() for character in characters]), 200

@api.route('/people/<int:character_id>', methods=['GET'])
def get_single_person(character_id):
    character = Character.query.get(character_id)
    if character:
        return jsonify(character.serialize()), 200
    return jsonify({"error": "Character not found"}), 404

#Planets
@api.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@api.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        return jsonify(planet.serialize()), 200
    return jsonify({"error": "Planet not found"}), 404

#Users
@api.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@api.route('/users/favorites', methods=['GET'])
def get_all_favorites_from_user():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    favorites = Favorite.query.filter_by(user_id=user_id).all()
    if favorites:
        return jsonify([favorite.serialize() for favorite in favorites]), 200
    return jsonify({"error": "There are no favorites for this user"}), 404

#Posts
@api.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_planet_to_favorites(planet_id):
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    existing_fav = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if existing_fav:
        return jsonify({"error": "Planet already in favorites"}), 400

    new_fav = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(new_fav)
    db.session.commit()

    return jsonify({"message": "Planet added to favorites"}), 201

@api.route('/favorite/people/<int:character_id>', methods=['POST'])
def add_character_to_favorites(character_id):
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    character = Character.query.get(character_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404

    existing_fav = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()
    if existing_fav:
        return jsonify({"error": "Character already in favorites"}), 400

    new_fav = Favorite(user_id=user_id, character_id=character_id)
    db.session.add(new_fav)
    db.session.commit()

    return jsonify({"message": "Character added to favorites"}), 201

#Deletes
@api.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet_from_favorites(planet_id):
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"error": "Planet not found in favorites"}), 404
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({"message": "Planet deleted from favorites"}), 200

@api.route('/favorite/people/<int:character_id>', methods=['DELETE'])
def delete_character_from_favorites(character_id):
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    favorite = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()
    if not favorite:
        return jsonify({"error": "Character not found in favorites"}), 404
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({"message": "Character deleted from favorites"}), 200


app.register_blueprint(api)


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
