
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func
from core.config import db
from services.formations_v0_1.models import Classe, Filiere, Niveau
from services.regions_v0_0.models import Departement


SEXES = {'F':'Feminin', 'M':'Masculin'}
SITUATIONS = {'C': 'Celibataire', 'M':'Marie(e)', 'V':'Veuf(ve)', 'D':'Divorce(e)'}
LANGUES = {'FR': 'Francais', 'EN': 'Anglais'}
NIVEAUX = {1:'BACCALAUREAT', 4:'LICENCE'}


class DiplomeConcours(db.Model):
    __bind_key__ = 'concours_v0'
    __tablename__ = 'diplome_concours'

    id = db.Column(db.String(10), primary_key=True)     # correspond au diplome d'entree
    niveau_id = db.Column(db.Integer, nullable=False)
    nom_fr = db.Column(db.String(200), nullable=False)
    nom_en = db.Column(db.String(200), nullable=False)


class FiliereConcours(db.Model):
    __bind_key__ = 'concours_v0'
    __tablename__ = 'filiere_concours'
    
    id = db.Column(db.String(10), primary_key=True)     # correspond au departement
    nom_fr = db.Column(db.String(200), nullable=False)
    nom_en = db.Column(db.String(200), nullable=False)
    options = db.relationship('OptionConcours', back_populates='filiere')

    @property
    def full_id(self):
        return self.id


class OptionConcours(db.Model):
    __bind_key__ = 'concours_v0'
    __tablename__ = 'option_concours'

    id = db.Column(db.String(10), primary_key=True)          # correspond aux filieres
    nom_fr = db.Column(db.String(200), nullable=False)
    nom_en = db.Column(db.String(200), nullable=False)
    filiere_id = db.Column(db.String(10), db.ForeignKey('filiere_concours.id'))
    filiere = db.relationship('FiliereConcours', back_populates='options')
    classes = db.relationship('ClasseConcours', back_populates='option')

    @property
    def full_id(self):
        return self.filiere.full_id + '-' + self.id
    

class ClasseConcours(db.Model):
    __bind_key__ = 'concours_v0'
    __tablename__ = 'classe_concours'

    id = db.Column(db.String(10), primary_key=True)          # correspond aux classes
    niveau_id = db.Column(db.Integer, nullable=False)
    option_id = db.Column(db.String(10), db.ForeignKey('option_concours.id'))
    option = db.relationship('OptionConcours', back_populates='classes')
    candidats = db.relationship('Candidat', back_populates='classe')

    @property
    def full_id(self):
        return self.option.full_id + '-' + self.id
    
    @property
    def niveau(self):
        return NIVEAUX[self.niveau_id]
    

class CentreConcours(db.Model):
    
    __bind_key__ = 'concours_v0'
    __tablename__ = 'centre_concours'

    id = db.Column(db.String(5), primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    candidats = db.relationship('Candidat', back_populates='centre')


class Candidat(db.Model):
    __bind_key__ = 'concours_v0'
    __tablename__ = 'candidats'

    # Métadonnées
    id = db.Column(db.String(20), primary_key=True)  # numero paiement
    date_inscription = db.Column(db.DateTime, default=datetime.now)

    # Informations personnelles de base
    nom = db.Column(db.String(200), nullable=False)
    prenom = db.Column(db.String(200), nullable=True, default='')
    date_naissance = db.Column(db.DateTime, nullable=False)
    lieu_naissance = db.Column(db.String(100), nullable=False)
    sexe_id = db.Column(db.String(10), nullable=False)  
    situation_matrimoniale_id = db.Column(db.String(50), nullable=False)
    
    # Origine géographique
    departement_origine_id = db.Column(db.String(100), nullable=False)
    langue_id = db.Column(db.String(10), nullable=False)  
    
    # Coordonnées
    telephone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    
    # Informations académiques
    # diplome = db.Column(db.String(200), nullable=False)
    # annee_diplome = db.Column(db.Integer, nullable=False)
    
    # options examens
    classe_id = db.Column(db.String(10), db.ForeignKey('classe_concours.id'))
    classe = db.relationship('ClasseConcours', back_populates='candidats')
    centre_id = db.Column(db.String(10), db.ForeignKey('centre_concours.id'))
    centre = db.relationship('CentreConcours', back_populates='candidats')

    @property
    def nom_complet(self):
        return ' '.join([self.nom, self.prenom])
    
    @property
    def sexe(self):
        return SEXES[self.sexe_id]

    @property
    def situation_matrimoniale(self):
        return SITUATIONS[self.situation_matrimoniale_id]
    
    @property
    def langue(self):
        return LANGUES[self.langue_id]
    
    @property
    def naissance(self):
        return f"{self.date_naissance.strftime('%d/%m/%Y')} à {self.lieu_naissance}"
    
    @property
    def departement_origine(self):
        query = db.session.query(Departement)
        query = query.filter_by(id=self.departement_origine_id)
        return query.one_or_none()
    
