"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity #instalar dependencias pipenv install flask_jwt_extended ()
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Persons, Planets, Role, Favorites
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Actualizaciones de las bases de datos

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


###### -------user------------######

@app.route('/User', methods=['GET'])
def handle_hello():
    response_body = { "msg": "Hello, this is your GET /user response "}
    return jsonify(response_body), 200

#--------JWT---- encriptar la configuracion 

app.config['JWT_SECRET_KEY']='unstringseguro'
jwt = JWTManager(app)  

#--------- Registro de usuario ------  
@app.route('/User', methods=['POST'])
def register():
    body = request.json 
    email = body.get('email', None)
    password = body.get('password', None)
    is_active = True
    role = body.get ("role", None) 
    if email is None or password is None:
        return {"error": "Campos requeridos"}, 400  
    if role not in Role.__members__:
        return{"error": f"{role} no existe"}    
# encriptar la password
    user_hash = generate_password_hash(password)
# nuevo Usuario
    new_user = User(email=email, password=user_hash, is_active=is_active, role=role)    
    db.session.add(new_user)
    try:
       db.session.commit()
       return jsonify({"mesage":"Usuario Creado"}), 201
    except Exception as error:    
       db.session.rollback()    
       return {"error", error}, 500   

#------- login ---------
@app.route('/User/login', methods=["POST"])
def login():
    body = request.json
    email = body.get('email', None)
    password = body.get ("password", None)
    if email is None or password is None:
        return {"error": "Todos los campos son requeridos "}

    login_user = User.query.filter_by(email=email).first()
    # verifiacion del email
    if not login_user:
        return {"error":"Usuario no encontrado"}, 404 
    # usando check para validar la contrase;a
    if check_password_hash(login_user.password, password):
        token = create_access_token({"id": login_user.id})
        print(token)
        return jsonify ({"access_token":token})
    else:     
        return "contrase;a incorrecta", 401


#-----Modificacion de la contrase;a------
@app.route('/change-password', methods=["PUT"])
def change_password():
    body= request.json
    email = body.get('email', None)
    new_email = body.get('new_email', None)
    password = body.get('password', None)
    if not email or not password:
        return{"error":"Todos los campos son necesarios"}
    update_user = User.query.filter_by(email=email).first()
    if not update_user:
        return {"error":"usuario no entocontrado"}, 404
    
    hash_password= generate_password_hash(password)
    update_user.password = hash_password
    update_user.email = new_email
    try:
        db.session.commit()
        return jsonify({"msg":"cambiando contrase;a o correo" }) 
    except Exception as error:    
        db.session.rollback()    
        return {"error": error}, 500  


######### --------------Character EndPoint---------------###########

# End point Characters

@app.route('/Persons', methods=['GET'])
def get_persons():
    persons = Persons.query.all()
    serialized_persons = [person.serialize() for person in persons]
    return jsonify({"Person": serialized_persons})

# End point 1 Character

@app.route('/Person/<int:id>', methods=['GET'])
def get_person(id):    
    person = Persons.query.filter_by(id=id).first()
    if not person:
        return{"error":"id no valida"}
    return jsonify({"personaje":person.serialize()})


# add 1 Character

@app.route('/Person', methods=['POST'])
def add_person():
    body = request.json  # busco el json del body
    body_name = body.get('name', None)
    body_birth_year = body.get('birth_year', None)
    body_skin_color = body.get('skin_color', None)
    body_height = body.get('height', None)
    body_eye_color = body.get('eye_color', None)
    if body_name is None or body_birth_year is None or body_skin_color is None or body_height is None or body_eye_color is None:
        return {"error": "Campos requeridos"}, 400
    person_exists = Persons.query.filter_by(name=body_name).first()
    if person_exists:
        return {"error": f"Personaje ya registrado {body_name}"}, 400
    new_person = Persons(name=body_name, birth_year=body_birth_year, skin_color=body_skin_color, height=body_height, eye_color=body_eye_color)                          
    db.session.add(new_person)
    try:
        db.session.commit()
        return jsonify({"data": f"Personaje {body_name} creado"}), 201
    except Exception as error:
        db.session.rollback()
        return {"error": error}, 500

    #delet 1 Character

    @app.route('/Person/<int:id>', methods=['DELETE'])
    def delet_person(id):
      person = Persons.query.filter_by(id=id).first()
      if not person:
        return{"error":"personaje no encontrado"},404
      db.session.delete(person)  
      try:        
        db.session.commit()
        return{"msg":"personaje borrado"}, 400
      except Exception as error:
        db.session.rollback()
        return {"error": error}, 500

        
####### ---------------- Planets EndPoint-------------------#######

# End point Planets


@app.route('/Planets', methods=['GET'])
def get_planets():
    planets = Planets.query.all()
    serialized_planets = [planet.serialize() for planet in planets]
    return jsonify({"data": serialized_planets})

# End point 1 Planet

@app.route('/Planet/<int:id>', methods=['GET'])
def get_planet(id): 
    planet = Planets.query.filter_by(id=id).first()
    if not planet:
        return{"error":"id no valida"}
    return jsonify({"planeta":planet.serialize()})


# add Planet

@app.route('/Planet', methods=['POST'])
def add_planet():
    body = request.json  
    body_name = body.get('name', None)
    body_climate = body.get('climate', None)
    body_population = body.get('population', None)
    body_orbital_period = body.get('orbital_period', None)
    body_rotate_period = body.get('rotate_period', None)

    if body_name is None or body_climate is None or body_population is None or body_orbital_period is None or body_rotate_period is None:
        return {"error": "Campos requeridos"}, 400

    planet_exists = Planets.query.filter_by(name=body_name).first()
    if planet_exists:
        return {"error": f"Planeta ya registrado {body_name}"}, 400

    new_planet = Planets(name=body_name, climate=body_climate, population=body_population, orbital_period=body_orbital_period, rotate_period=body_rotate_period)                         
    db.session.add(new_planet)
    try:
        db.session.commit()
        return jsonify({"data": f"planeta {body_name} creado"}), 201
    except Exception as error:
        db.session.rollback()
        return {"error": error}, 500

#delet 1 Planet

@app.route('/Planet/<int:id>', methods=['DELETE'])
def delete_planet(id):
      planet = Planets.query.filter_by(id=id).first()
      if not planet:
        return{"error":"planeta no encontrado"},404
      db.session.delete(planet)  
      try:        
        db.session.commit()
        return{"msg":"planeta borrado"}, 400
      except Exception as error:
        db.session.rollback()
        return {"error": error}, 500

####### ---------------- Favorites EndPoint (-------------------#######



@app.route('/Favorites', methods=['GET'] )
@jwt_required()
def get_favorite_by_user():
    user = get_jwt_identity()
    current_user_id = user["id"]
    user_favorites = Favorites.query.filter_by(user_id=current_user_id).all()
    return jsonify({"data": [favorite.serialize() for favorite in favorites]})
    
@app.route('/Favorites', methods=['GET'] )
def get_favorites():
    favorites= Favorites.query.all()
    return jsonify({"favorites": [favorite.serialize() for favorite in favorites]})

@app.route('/Favorites', methods=['POST'] )
@jwt_required()
def add_favorite():
    body = request.json
    person_id = body.get("person_id", None)
    planet_id = body.get("planet_id", None)
    user = get_jwt_identity()   
    if not person_id and not planet_id:
        return {"error": " el id del personaje o el planeta es requerido"}
    if person_id:
        new_favorite = Favorites (person_id=person_id, user_id=user["id"])
        db.session.add(new_favorite)
    else:
        new_favorite = Favorites(planet_id=planet_id, user_id=user["id"])    
        db.session.add(new_favorite)
    try:        
        db.session.commit()
        return{"msg":"Favorito creado con exito"}, 400
    except Exception as error:
        db.session.rollback()
        return jsonify({"error": error}), 500

    

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
