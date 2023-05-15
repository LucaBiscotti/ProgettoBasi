from datetime import date
from flask import Blueprint, jsonify, render_template, request, url_for, redirect, flash
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

# @login_manager.unauthorized_handler
# def unauthorized():
#     flash('You must be logged in to view that page.')
#     return redirect(url_for('routes.login', login_url=request.path))

#Routes

@bp.route('/')
@login_required
def index():
    user = Docenti.query.get(int(current_user.id))
    corsi = ListaDocenti.query.filter(ListaDocenti.id_docente == user.id)
    return render_template('index.html', corsi=corsi, user=user)

@bp.route('/create/', methods=('GET', 'POST'))
@login_required
def create():
    ins = Insegnamenti.query.all()
    corsi = Corsi.query.all()
    if request.method == 'POST':
        cfu = int(request.form['cfu'])
        anno = request.form['anno']
        Sdatai = request.form['data_i']
        Sdataf = request.form['data_f']
        cod = request.form['codice']
        datai = date.fromisoformat(Sdatai)
        dataf = date.fromisoformat(Sdataf)
        exam = Esami(cfu = cfu,
                            anno_accademico=anno,
                            data_inizio=datai,
                            data_fine=dataf,
                            codice_corso=cod)
        db.session.add(exam)
        db.session.commit()
        id = exam.id
        doc = ListaDocenti(id_esame = id,
                            id_docente = current_user.id,
                            ruolo = Ruolo.presidente)
        db.session.add(doc)
        db.session.commit()
        return redirect(url_for('routes.index'))
    return render_template('create.html', insegnamenti = ins, corsi = corsi)

@bp.route('/corsi_by_insegnamento', methods=['GET'])
def corsi_by_insegnamento():
    codice_insegnamento = request.args.get('codice_insegnamento', '', type=str)
    corsi = Corsi.query.filter(Corsi.codice_insegnamento == codice_insegnamento).all()
    return jsonify([corso.serialize() for corso in corsi])


