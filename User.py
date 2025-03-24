from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()  

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)  
    fullname = db.Column(db.String(200), nullable=False)

    def __init__(self, id, username, password, fullname=""):
        self.id = id
        self.username = username
        self.password = password
        self.fullname = fullname

    @classmethod
    def check_password(cls, hashed_password, password):
        return check_password_hash(hashed_password, password)

    def __repr__(self):  
        return f'<User {self.username}>'

#para el usuario 1
print(generate_password_hash("pizzas1004"))
#para el usuario 2
print(generate_password_hash("10ventas"))
     