
from core.config import db


class Formation(db.Model):
    __bind_key__ = 'formations_v0'
    __tablename__ = 'formations'
    id = db.Column(db.String(5), primary_key=True)
    code_systhag = db.Column(db.Integer)
    nom = db.Column(db.String(50))
    filieres = db.relationship('Filiere', back_populates='formation')


class Niveau(db.Model):
    __bind_key__ = 'formations_v0'
    __tablename__ = 'niveaux'
    id = db.Column(db.String(2), primary_key=True)
    code_cycle = db.Column(db.String(2)) # Exple: L1
    nom = db.Column(db.String(50))       # Exple: Niveau 1 Licence


class DepartementAcademique(db.Model):
    __bind_key__ = 'formations_v0'
    __tablename__ = 'departements'
    id = db.Column(db.String(10), primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    filieres = db.relationship('Filiere', back_populates='departement')
    

class Filiere(db.Model):
    __bind_key__ = 'formations_v0'
    __tablename__ = 'filieres'
    id = db.Column(db.String(10), primary_key=True)
    prefix = db.Column(db.String(2), nullable=False)
    code_udo = db.Column(db.String(10), nullable=False)
    code_enset = db.Column(db.String(10), nullable=False)
    nom = db.Column(db.String(200), nullable=False)
    classes = db.relationship('Classe', back_populates='filiere')
    departement_id = db.Column(db.String(10), db.ForeignKey('departements.id'))
    departement = db.relationship('DepartementAcademique', back_populates='filieres')
    formation_id = db.Column(db.String(5), db.ForeignKey('formations.id'))
    formation = db.relationship('Formation', back_populates='filieres')


class Classe(db.Model):
    __bind_key__ = 'formations_v0'
    __tablename__ = 'classes'
    id = db.Column(db.String(10), primary_key=True)
    niveau_id = db.Column(db.String(2), db.ForeignKey('niveaux.id'))
    niveau = db.relationship('Niveau')
    filiere_id = db.Column(db.String(10), db.ForeignKey('filieres.id'))
    filiere = db.relationship('Filiere', back_populates='classes')

    @property
    def code_complet(self):
        return f'{self.filiere.code_udo}{self.niveau_id[-1]}'

