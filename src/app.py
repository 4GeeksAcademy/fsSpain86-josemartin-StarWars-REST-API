"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Characters, Vehicles, Planets
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


@app.route('/user', methods=['POST'])
def create_user():
    request_body= request.get_json()
    print(request_body)
    exist = User.query.filter_by(email = request_body["email"]).first()
    if exist: 
        return jsonify({
            "msg":"el usuario ya existe"
        }), 400
    new_user = User(email = request_body["email"], password = request_body["password"], is_active = request_body["is_active"])
    db.session.add(new_user)
    db.session.commit()
    response_body = {
        "msg": "usuario creado"
    }
    return jsonify(response_body), 200


@app.route('/user', methods=['GET'])
def get_user():
    users = User.query.all()
    
    serialized_users = list([user.serialize() for user in users])
    print(serialized_users)
    if not users:
        raise APIException("No users found", status_code=404)
    else:
        return jsonify(serialized_users), 200
    


@app.route('/characters', methods=['GET'])
def get_characters():
    characters = Characters.query.all()

    serialized_characters = list([character.serialize() for character in characters])
    print(serialized_characters)
    if not characters:
        raise APIException("No characters found", status_code=404)
    else:
        return jsonify(serialized_characters), 200
    

@app.route('/characters/<int:id>', methods=['GET'])
def get_one_person(id):
    person = Characters.query.get(id)
    if person is None: 
        return jsonify({"msg": "no character found"})
    return jsonify(person.serialize()), 200
    

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planets.query.all()
    serialized_planets = list([planet.serialize() for planet in planets])
    print(serialized_planets)
    if not planets:
        raise APIException("No planets found", status_code=404)
    else:
        return jsonify(serialized_planets), 200
    

@app.route('/planets/<int:id>', methods=['GET'])
def get_one_planet(id):
    planet = Planets.query.get(id)
    if planet is None: 
        return jsonify({"msg": "no planet found"})
    return jsonify(planet.serialize()), 200
    

@app.route('/vehicles', methods=['GET'])
def get_vehicles():
    vehicles = Vehicles.query.all()
    serialized_vehicles = list([vehicle.serialize() for vehicle in vehicles])
    print(serialized_vehicles)
    if not vehicles:
        raise APIException("No vehicles found", status_code=404)
    else:
        return jsonify(serialized_vehicles), 200


@app.route('/vehicles/<int:id>', methods=['GET'])
def get_one_vehicle(id):
    vehicle = Vehicles.query.get(id)
    if vehicle is None: 
        return jsonify({"msg": "no vehicle found"})
    return jsonify(vehicle.serialize()), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
