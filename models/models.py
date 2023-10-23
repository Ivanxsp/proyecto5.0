from datetime import date
from config import mysql,login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(UserMixin, mysql.Model):
    __tablename__ = 'usuarios'

    id_usuario = mysql.Column(mysql.Integer, primary_key=True, autoincrement=True)
    usuario = mysql.Column(mysql.String(25), nullable=False)
    email = mysql.Column(mysql.String(50), nullable=False)
    contrasena = mysql.Column(mysql.String(256), nullable=False)
    id_rol = mysql.Column(mysql.Integer, mysql.ForeignKey('roles.id_rol', ondelete='CASCADE', onupdate='CASCADE'))
    usuarios_uk1 = mysql.Index('usuarios_uk1', usuario, email, unique=True)

    def set_password(self, password):
        self.contrasena = generate_password_hash(password)

    def return_password(self, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.contrasena, password)

    def get_id(self):
        return self.id_usuario

    def __repr__(self):
        return '<User {}>'.format(self.usuario)
    
@login_manager.user_loader
def load_user(id_usuario):
    return Usuario.query.get((id_usuario))
    
class Rol(mysql.Model):
    __tablename__ = 'roles'

    id_rol = mysql.Column(mysql.Integer, primary_key=True, autoincrement=True)
    nombre_rol = mysql.Column(mysql.String(50), nullable=False)

class Tema(mysql.Model):
    __tablename__ = 'temas'

    id_tema = mysql.Column(mysql.Integer, primary_key=True, autoincrement=True)
    tema = mysql.Column(mysql.String(50), nullable=False)

class Post(mysql.Model):
    __tablename__ = 'posts'

    id_post = mysql.Column(mysql.Integer, primary_key=True, autoincrement=True)
    fecha = mysql.Column(mysql.Date, default=date.today)
    titulo = mysql.Column(mysql.String(100), nullable=False)
    contenido = mysql.Column(mysql.String(2500), nullable=False)
    ruta = mysql.Column(mysql.String(200), nullable=False)
    id_usuario = mysql.Column(mysql.Integer, mysql.ForeignKey('usuarios.id_usuario', ondelete='CASCADE', onupdate='CASCADE'))
    id_tema = mysql.Column(mysql.Integer, mysql.ForeignKey('temas.id_tema', ondelete='CASCADE', onupdate='CASCADE'))

class Respuesta(mysql.Model):
    __tablename__ = 'respuestas'

    id_post = mysql.Column(mysql.Integer, mysql.ForeignKey('posts.id_post', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    id_respuesta = mysql.Column(mysql.Integer, primary_key=True, autoincrement=True)
    id_usuario = mysql.Column(mysql.Integer, mysql.ForeignKey('usuarios.id_usuario', ondelete='CASCADE', onupdate='CASCADE'))
    contenido = mysql.Column(mysql.String(2500), nullable=False)
    ruta = mysql.Column(mysql.String(200), nullable=False)
    fecha = mysql.Column(mysql.Date, default=date.today)