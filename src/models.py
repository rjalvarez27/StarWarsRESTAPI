from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()

class Role(enum.Enum):
    admin = "admin"    
    user = "user"

#db.Model = base 

class User(db.Model):   
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(300), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    role = db.Column(db.Enum(Role), nullable=False , default="user")
    favorites = db.Relationship("Favorites")

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
 
# modelos para crear las star wars APi

class Persons(db.Model):       
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    birth_year = db.Column(db.String(20), nullable=True, default='N/A')
    skin_color =db.Column(db.String(80), nullable=True, default='N/A')
    height = db.Column(db.String(50), nullable=True, default='N/A')
    eye_color = db.Column(db.String(50), nullable=True, default='N/A')
    
    
    def __repr__(self):
        return '<Persons %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "birth_Year": self.birth_year,
            "skin_color": self.skin_color,
            "height": self.height,
            "eye_color": self.eye_color
        }


class Planets(db.Model):      
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    climate = db.Column(db.String(20), nullable=True, default='N/A')
    population = db.Column(db.String(50), nullable=True, default='N/A')
    orbital_period = db.Column(db.String(30), nullable=True, default='N/A')
    rotate_period = db.Column(db.String(30), nullable=True, default='N/A')
    

    def __repr__(self):
        return '<Planets %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "population": self.population,
            "orbital_period": self.orbital_period,
            "rotate_period": self.rotate_period
        }   

class Favorites (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id= db.Column(db.Integer, nullable=True)
    planet_id= db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)
    user = db.Relationship("User")

    def __repr__(self):
        return '<Favorites %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "person_id": self.person_id,
            "planet_id": self.planet_id,
            "user_id": self.user_id,       
            
        }   


