import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from sqlalchemy.sql import func

from models import db,Studenti,Docenti,Esami,Corsi,Insegnamenti,Prove,ListaIscritti,EsamiSvolti,ListaDocenti

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
    
@app.route('/')
def index():
    students = Studenti.query.all()
    return render_template('index.html', students=students)

@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        matricola = int(request.form['matricola'])
        firstname = request.form['nome']
        lastname = request.form['cognome']
        email = request.form['email']
        pwd = request.form['password']
        student = Studenti(matricola = matricola,
                            nome=firstname,
                            cognome=lastname,
                            email=email,)
        student.set_password(pwd)
        db.session.add(student)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('create.html')
