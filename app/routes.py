from flask import Blueprint, render_template, request, url_for, redirect, flash
from models import *
from forms import LoginForm
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
login_manager = LoginManager()

bp = Blueprint('routes', __name__)

#Login and logout handler
@login_manager.user_loader
def load_user(user_id):
    return Docenti.query.get(int(user_id))

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = LoginForm()
    if form.validate_on_submit():
        docente = Docenti.query.filter_by(email=form.email.data).first()
        if docente is not None and docente.check_password(form.password.data):
            login_user(docente)
            return redirect(url_for('routes.index'))
        else:
            flash('Invalid email or password')
    return render_template('login.html', form=form)

@bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('routes.login', login_url=request.path))

@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view that page.')
    return redirect(url_for('routes.login', login_url=request.path))

#Routes

@bp.route('/')
@login_required
def index():
    students = Studenti.query.all()
    return render_template('/index.html', students=students)

@bp.route('/create/', methods=('GET', 'POST'))
@login_required
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

        return redirect(url_for('routes.index'))
    return render_template('create.html')