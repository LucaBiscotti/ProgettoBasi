from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.orm import object_session
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
    lista_iscritti = db.relationship('ListaIscritti', backref='iscritto', lazy=True)
    esami_svolti = db.relationship('EsamiSvolti', backref='registrato', lazy=True)

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
    prove = db.relationship('ListaDocenti',backref='doc_esame', lazy=True)

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
    codice_corso = db.deferred(db.Column(db.String(5), db.ForeignKey('corsi.codice', deferrable=True, initially="DEFERRED")))
    prove = db.relationship('Prove', backref='prova_esame', lazy=True)
    esami_svolti = db.relationship('EsamiSvolti', backref='esame', lazy=True)
    esami_docenti = db.relationship('ListaDocenti', backref='esame_doc', lazy=True)


class Corsi(db.Model):
    codice = db.Column(db.String(5), unique=True, primary_key=True)
    titolo = db.Column(db.String(80))
    codice_insegnamento = db.deferred(db.Column(db.String(4), db.ForeignKey('insegnamenti.codice', deferrable=True, initially="DEFERRED")))
    esami = db.relationship('Esami', backref='corso', lazy=True)

    def serialize(self):
        return {
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
    id_docente = db.deferred(db.Column(db.Integer, db.ForeignKey('docenti.id', deferrable=True, initially="DEFERRED")))
    id_esame = db.deferred(db.Column(db.Integer, db.ForeignKey('esami.id', deferrable=True, initially="DEFERRED")))
    lista_iscritti = db.relationship('ListaIscritti', backref='prova', lazy=True)

class ListaIscritti(db.Model):
    id_prova = db.Column(db.Integer, db.ForeignKey('prove.id', deferrable=True, initially="DEFERRED"), primary_key=True)
    #id_prova = db.deferred(db.Column(db.Integer, db.ForeignKey('prove.id', deferrable=True, initially="DEFERRED"), primary_key=True))
    matricola_studente = db.Column(db.Integer, db.ForeignKey('studenti.matricola', deferrable=True, initially="DEFERRED"), primary_key=True)
    #matricola_studente = db.deferred(db.Column(db.Integer, db.ForeignKey('studenti.matricola', deferrable=True, initially="DEFERRED"), primary_key=True))
    voto = db.Column(db.String)
    sostenuto = db.Column(db.Boolean,nullable=False)
    accettato = db.Column(db.Boolean)
    data_scadenza = db.Column(db.Date, nullable=False)
    studente = db.relationship('Studenti', backref='iscrizioni')
    #prova = db.relationship('Prove', backref='lista_iscritti')


class EsamiSvolti(db.Model):
    id_esame = db.deferred(db.Column(db.Integer, db.ForeignKey('esami.id', deferrable=True, initially="DEFERRED"), primary_key=True))
    matricola_studente = db.deferred(db.Column(db.Integer, db.ForeignKey('studenti.matricola', deferrable=True, initially="DEFERRED"), primary_key=True))
    voto = db.Column(db.Integer, nullable=False)
    data = db.Column(db.Date, nullable=False)
    #studente = db.relationship("Studenti", backref="esami_svolti")
    #esame = db.relationship("Esami", backref="esami_sostenuti")

class ListaDocenti(db.Model):
    id_esame = db.Column(db.Integer, db.ForeignKey('esami.id', deferrable=True, initially="DEFERRED"), primary_key=True)
    id_docente = db.Column(db.Integer, db.ForeignKey('docenti.id', deferrable=True, initially="DEFERRED"), primary_key=True)
    ruolo = db.Column(db.Enum(Ruolo), nullable=False)

    esame = db.relationship('Esami', backref='lista_docenti')


@event.listens_for(ListaIscritti, 'after_update')
def check_prove_and_create_esami_svolti(target, value, oldvalue, initiator=None):
    if value is not None and oldvalue is None:
        session = object_session(target)

        # Controllo delle prove per lo studente e l'esame corrispondenti
        studente = target.iscritto
        esame = target.prova.prova_esame
        prove = (
            session.query(Prove)
            .join(ListaIscritti)
            .filter(ListaIscritti.iscritto == studente, Prove.prova_esame == esame,ListaIscritti.accettato == True, Esami.anno_accademico == esame.anno_accademico)
            .all()
        )

        # Calcolo della somma delle percentuali delle prove
        somma_percentuali = sum(prova.percentuale for prova in prove)

        # Se la somma delle percentuali arriva a 100, crea un elemento in EsamiSvolti
        if somma_percentuali == 1:
            esame_svolto = EsamiSvolti(
                esame=esame,
                studente=studente,
                voto= sum(prova.ListaIscritti.voto * prova.percentuale for prova in prove),
                data=None,  # Puoi impostare la data in base alle tue regole di business
            )
            session.add(esame_svolto)
            session.commit()