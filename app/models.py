from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

db = SQLAlchemy()

class TipoVoto(Enum):
    idoneita = "IDONEITÀ"
    bonus = "BONUS"
    punteggio = "PUNTEGGIO"

class TipoScadenza(Enum):
    durata = "DURATA"
    data = "DATA"

class Ruolo(Enum):
    presidente = "PRESIDENTE"
    membro = "MEMBRO"

class Studenti(db.Model):
    matricola = db.Column(db.Integer, unique=True, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Studente {}>'.format(self.nome)

class Docenti(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    prove = db.relationship('Prove',backref='docente', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_active(self):
        return True
    
    def get_id(self):
        return str(self.id)
    
class Esami(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    cfu = db.Column(db.Integer, nullable=False)
    anno_accademico = db.Column(db.Integer, nullable=False)
    data_inizio = db.Column(db.Date, nullable=False)
    data_fine = db.Column(db.Date, nullable=False)
    codice_corso = db.Column(db.String(5), db.ForeignKey('corsi.codice'))

class Corsi(db.Model):
    codice = db.Column(db.String(5), unique=True, primary_key=True)
    titolo = db.Column(db.String(80))
    codice_insegnamento = db.Column(db.String(4), db.ForeignKey('insegnamenti.codice'))
    esami = db.relationship('Esami', backref='corso', lazy=True)

    def serialize(self):
        return {
            'codice': self.codice,
            'codice': self.codice,
            'titolo': self.titolo,
            'codice_insegnamento': self.codice_insegnamento
        }

class Insegnamenti(db.Model):
    codice = db.Column(db.String(4), unique=True, primary_key=True)
    nome = db.Column(db.String(80))
    corsi = db.relationship('Corsi', backref='insegnamento', lazy=True)

class Prove(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    titolo = db.Column(db.String(80),nullable=False)
    percentuale = db.Column(db.Integer, nullable=False)
    tipo_voto = db.Column(db.Enum(TipoVoto), nullable=False)
    aula = db.Column(db.String(80))
    durata = db.Column(db.Integer)
    data_inizio = db.Column(db.Date, nullable=False)
    tipo_scadenza = db.Column(db.Enum(TipoScadenza),nullable=False)
    id_docente = db.Column(db.Integer, db.ForeignKey('docenti.id'))

class ListaIscritti(db.Model):
    id_prova = db.Column(db.Integer, db.ForeignKey('prove.id'), primary_key=True)
    matricola_studente = db.Column(db.Integer, db.ForeignKey('studenti.matricola'), primary_key=True)
    voto = db.Column(db.String)
    sostenuto = db.Column(db.Boolean,nullable=False)
    accettato = db.Column(db.Boolean)
    data_scadenza = db.Column(db.Date, nullable=False)
    studente = db.relationship('Studenti', backref='iscrizioni')
    prova = db.relationship('Prove', backref='iscritti')

class EsamiSvolti(db.Model):
    id_esame = db.Column(db.Integer, db.ForeignKey('esami.id'), primary_key=True)
    matricola_studente = db.Column(db.Integer, db.ForeignKey('studenti.matricola'), primary_key=True)
    voto = db.Column(db.Integer, nullable=False)
    data = db.Column(db.Date, nullable=False)
    studente = db.relationship("Studenti", backref="esami_svolti")
    esame = db.relationship("Esami", backref="esami_sostenuti")

class ListaDocenti(db.Model):
    id_esame = db.Column(db.Integer, db.ForeignKey('esami.id'), primary_key=True)
    id_docente = db.Column(db.Integer, db.ForeignKey('docenti.id'), primary_key=True)
    ruolo = db.Column(db.Enum(Ruolo),nullable = False)
    docente = db.relationship("Docenti", backref="esami_docente")
    esame = db.relationship("Esami", backref="esami_creati")

