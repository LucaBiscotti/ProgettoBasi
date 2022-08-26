from flask import Flask, render_template, url_for, redirect, make_response, request
from flask_login import *
from sqlalchemy import PrimaryKeyConstraint, engine
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/postgres"

db = SQLAlchemy(app)

class Docenti(db.Model):
    __tablename__='Docenti'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40))
    cognome = db.Column(db.String(40))
    email = db.Column(db.String(40))
    pwd = db.Column(db.String(40))

    def __init__(self, nome, cognome, email, pwd) :
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.pwd = pwd

db.create_all()

@app.route('/')
def index():
    #Inseriamo un record, docente
    
    docente = Docenti('Luca','Biscotti','luca_figo@sesso.it','porcoddio')
    db.session.add(docente)
    db.session.commit()

    print(db.__doc__)

    #Ora facciamoci ridare la lista dei docenti

    docenti = db.session.query(Docenti).all()

    return "Hello, Flask!"