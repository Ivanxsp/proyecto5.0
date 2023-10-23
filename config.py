from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

app=Flask(__name__)

app.config["SECRET_KEY"] = 'Miproy3ct0-1.0'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://foroUser:f0r0DB@localhost/foro'

engine = create_engine('mysql://foroUser:f0r0DB@localhost/foro')

mysql = SQLAlchemy(app)

conn = engine.connect()

Session = sessionmaker(bind=engine)

session = Session()

login_manager = LoginManager(app)