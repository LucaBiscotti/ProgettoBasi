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


#Routes

@bp.route('/')
@login_required
def index():
    user = Docenti.query.get(int(current_user.id))

    #SELECT * FROM Esami e NATURAL JOIN ListaDocenti l WHERE l.id_docente == x JOIN Corsi ON (codice_corso == Corsi.codice)
    esami = Esami.query.join(ListaDocenti).filter(ListaDocenti.id_docente == user.id).join(Corsi, Esami.codice_corso == Corsi.codice).add_columns(Esami,Corsi.titolo.label('titolo'))
    return render_template('index.html', corsi=esami, user=user)

@bp.route('/create_exam/', methods=('GET', 'POST'))
@login_required
def create():
    ins = Insegnamenti.query.all()
    corsi = Corsi.query.all()

    if request.method == 'POST':
        #Create Esami record
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
        
        #Create ListaDocenti record
        id = exam.id
        doc = ListaDocenti(id_esame = id,
                            id_docente = current_user.id,
                            ruolo = Ruolo.presidente)
        db.session.add(doc)
        db.session.commit()
        return redirect(url_for('routes.index'))
    return render_template('create.html', insegnamenti = ins, corsi = corsi)


@bp.route('/create_prova/<int:id>', methods=('GET', 'POST'))
@login_required
def create_prova(id):
    tipo_voto_enum = TipoVoto
    tipo_scad_enum = TipoScadenza
    if request.method == 'POST':
        titolo = request.form['titolo']
        percentuale = int(request.form['percentuale'])
        tipo_voto = request.form['tipo_voto']
        aula = request.form['aula']
        durata = request.form['durata']
        data = request.form['data_i']
        data_inizio = date.fromisoformat(data)
        tipo_scadenza = request.form['tipo_scadenza']
        id_doc = current_user.id
        id_esame = id
        perc = percentuale/100
        prova = Prove(titolo = titolo,
                      percentuale = perc,
                      tipo_voto = tipo_voto,
                      aula = aula,
                      durata = durata,
                      data_inizio = data_inizio,
                      tipo_scadenza = tipo_scadenza,
                      id_docente = id_doc,
                      id_esame = id_esame)
        db.session.add(prova)
        db.session.commit()
        return redirect(url_for('routes.exam', esame_id = id))
    return render_template('create_prova.html',scad = tipo_scad_enum, voto = tipo_voto_enum, id = id)

@bp.route('/corsi_by_insegnamento', methods=['GET'])
def corsi_by_insegnamento():
    codice_insegnamento = request.args.get('codice_insegnamento', '', type=str)
    corsi = Corsi.query.filter(Corsi.codice_insegnamento == codice_insegnamento).all()
    return jsonify([corso.serialize() for corso in corsi])


@bp.route('/exam/<int:esame_id>', methods=('GET', 'POST'))
@login_required
def exam(esame_id):
    esame = Esami.query.get(esame_id)
    prove = Prove.query.filter(Prove.id_esame == esame.id).all()
    return render_template('exam.html',esame = esame, prove=prove)


@bp.route('/students/<int:id>', methods=('GET', 'POST'))
@login_required
def students(id):
    lista = Studenti.query.all()
    return render_template('students.html', studenti=lista)


@bp.route('/student_exam/<int:id>', methods=('GET', 'POST'))
@login_required
def student_exam(id):
    from itertools import groupby

    esame = Esami.query.get(id)
    prove = Prove.query.filter(Prove.id_esame == id).all()
    lista = Studenti.query.join(ListaIscritti, Studenti.matricola == ListaIscritti.matricola_studente).join(Prove, ListaIscritti.id_prova == Prove.id).join(EsamiSvolti, isouter=True).filter(Prove.id_esame == esame.id).add_columns(Prove.titolo,ListaIscritti.id_prova,EsamiSvolti.voto)
    
    studenti = []
    lista_ordinata = sorted(lista, key=lambda x: x.Studenti.matricola)  # Ordina per matricola
    for matricola, group in groupby(lista_ordinata, key=lambda x: x.Studenti.matricola):  # Raggruppa per matricola
        sos = [0] * len(prove)  # Crea una lista di zeri per le prove
        voto = None
        for row in group:
            for i, prova in enumerate(prove):
                if row.id_prova == prova.id:
                    sos[i] = 1
            if row.voto is not None:
                voto = row.voto

        studenti.append({
            'studente': row.Studenti,
            'fatto': sos,
            'voto': voto
        })

    return render_template('student_exam.html',studenti = studenti, prove = prove)

@bp.route('/student_prove/<int:id>', methods=('GET', 'POST'))
@login_required
def student_prove(id):
    if request.method == 'POST':
        voto = request.form['voto']
        mat = request.form['mat']
        verbal = ListaIscritti.query.filter(ListaIscritti.id_prova == id, ListaIscritti.matricola_studente == mat).first()
        verbal.voto = voto
        verbal.sostenuto = True
        verbal.accettato = True
        db.session.add(verbal)
        db.session.commit()
        
    prova = Prove.query.get(id)
    lista = Studenti.query.join(ListaIscritti, Studenti.matricola == ListaIscritti.matricola_studente).filter(ListaIscritti.id_prova == prova.id).add_columns(ListaIscritti.voto).add_columns(ListaIscritti.data_scadenza, ListaIscritti.accettato)
    return render_template('student_prove.html',prova = prova, studenti = lista)