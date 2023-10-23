from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,  PasswordField, BooleanField, SubmitField, TextAreaField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from models.models import Usuario
from flask import flash
from flask_wtf.file import FileField, FileAllowed


class LoginForm(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired(), Length(min=3,max=25, message="Entre 3 y 25 cracteres")])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=8, max=40)])
    submit = SubmitField('Entrar')


class RegistrationForm(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired(), Length(min=3,max=25, message="Entre 3 y 25 cracteres")])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=10, max=100, message="Entre 5 y 100 caracteres")])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=8, max=40)])
    password2 = PasswordField('Repite la contraseña', validators=[DataRequired(), EqualTo('password'), Length(min=8, max=15)])
    id_rol = 1
    submit = SubmitField('Registrarse')

    def validate_Usuario(self, usuario):
        user = Usuario.query.filter_by(usuario=usuario.data).first()
        if user is not None:
            flash('Usuario ya registrado, elija otro nombre.')

    def validate_email(self, email):
        user = Usuario.query.filter_by(email=email.data).first()
        if user is not None:
            flash('Email ya registrado, use otro email.')

class NewPostForm(FlaskForm):
    titulo = StringField('Titulo', validators=[DataRequired(),  Length(min=5, max=100, message="Entre 5 y 100 caracteres")])
    contenido = TextAreaField('Contenido', validators=[DataRequired(), Length(min=10, max=2500, message="Máximo 2500 caracteres")])
    fecha = DateTimeField("Fecha", default=datetime.now(), validators=[DataRequired()])
    foto = FileField('Foto', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    id_tema = SelectField(
        "Tema",
        choices = [
            (1, 'Motos'),
            (2, 'Rutas'),
            (3, 'Averías')
        ],
        validators=[DataRequired()])
    submit = SubmitField('Publicar')

class ResponsePostForm(FlaskForm):
    contenido = TextAreaField('Contenido', validators=[DataRequired(), Length(min=2, max=2500, message="Máximo 2500 caracteres")])
    fecha = DateTimeField("Fecha", default=datetime.now(), validators=[DataRequired()])
    foto = FileField('Foto', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Enviar respuesta')

class UpdateDataForm(FlaskForm):
    usuario = StringField('Usuario', validators=[Length(min=3,max=25, message="Entre 3 y 25 cracteres")])
    email = StringField('Email:', validators=[Email(),  Length(min=10, max=100, message="Entre 5 y 100 caracteres")])
    actual_pass = PasswordField('Contraseña actual', validators=[DataRequired()])
    password = PasswordField('Nueva contraseña:', validators=[Length(min=8, max=40)])
    password2 = PasswordField('Repite la contraseña:', validators=[Length(min=8, max=40)])
    submit = SubmitField('Cambiar datos')

class EditForm(FlaskForm):
    contenido = TextAreaField('Contenido', validators=[DataRequired(),Length(min=2, max=2500, message="Máximo 2500 caracteres")])
    foto = FileField("Archivos .jpg .jpeg y .png", validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Guardar')