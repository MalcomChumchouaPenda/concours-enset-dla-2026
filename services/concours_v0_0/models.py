
from collections import namedtuple, OrderedDict
from datetime import datetime
from core.config import db
from services.regions_v0_0.models import Departement


_Sexe = namedtuple('Sexe', ['id', 'nom_fr', 'nom_en'])
_Situation = namedtuple('Situation', ['id', 'nom_fr', 'nom_en'])
_Langue = namedtuple('Langue', ['id', 'nom_fr', 'nom_en'])
_NiveauConcours = namedtuple('NiveauConcours', ['id', 'nom_fr', 'nom_en'])

SEXES = OrderedDict()
SEXES['F'] = _Sexe('F', 'Feminin', 'Female')
SEXES['M'] = _Sexe('M', 'Masculin', 'Male')

SITUATIONS = OrderedDict()
SITUATIONS['C'] = _Situation('C', 'Celibataire', 'Single')
SITUATIONS['M'] = _Situation('M', 'Marie(e)', 'Married')
SITUATIONS['V'] = _Situation('V', 'Veuf(ve)', 'Widowed')
SITUATIONS['D'] = _Situation('D', 'Divorce(e)', 'Divorced')

LANGUES = OrderedDict()
LANGUES['FR'] = _Langue('FR', 'Francais', 'French')
LANGUES['EN'] = _Langue('EN', 'Anglais', 'English')

NIVEAUX = OrderedDict()
NIVEAUX[1] = _NiveauConcours(1, 'NIVEAU 1', 'LEVEL 1')
NIVEAUX[4] = _NiveauConcours(4, 'NIVEAU 4', 'LEVEL 4')


class DiplomeConcours(db.Model):
    __bind_key__ = 'concours_v0'
    __tablename__ = 'diplome_concours'

    id = db.Column(db.String(10), primary_key=True)     # correspond au diplome d'entree
    nom_fr = db.Column(db.String(200), nullable=False)
    nom_en = db.Column(db.String(200), nullable=False)
    prefix = db.Column(db.String(7), nullable=True)
    ouvert = db.Column(db.Boolean, default=False)
    niveau_id = db.Column(db.Integer, nullable=False)
    inscriptions = db.relationship('InscriptionConcours', back_populates='diplome')

    def nom(self, locale='fr'):
        if locale == 'fr':
            return self.nom_fr
        return self.nom_en


class FiliereConcours(db.Model):
    __bind_key__ = 'concours_v0'
    __tablename__ = 'filiere_concours'
    
    id = db.Column(db.String(10), primary_key=True)     # correspond au departement
    nom_fr = db.Column(db.String(200), nullable=False)
    nom_en = db.Column(db.String(200), nullable=False)
    options = db.relationship('OptionConcours', back_populates='filiere')

    def nom(self, locale='fr'):
        if locale == 'fr':
            return self.nom_fr
        return self.nom_en


class OptionConcours(db.Model):
    __bind_key__ = 'concours_v0'
    __tablename__ = 'option_concours'

    id = db.Column(db.String(10), primary_key=True)          # correspond aux filieres
    nom_fr = db.Column(db.String(200), nullable=False)
    nom_en = db.Column(db.String(200), nullable=False)
    filiere_id = db.Column(db.String(10), db.ForeignKey('filiere_concours.id'))
    filiere = db.relationship('FiliereConcours', back_populates='options')
    classes = db.relationship('ClasseConcours', back_populates='option')

    def nom(self, locale='fr'):
        if locale == 'fr':
            return self.nom_fr
        return self.nom_en
    

class ClasseConcours(db.Model):
    __bind_key__ = 'concours_v0'
    __tablename__ = 'classe_concours'

    id = db.Column(db.String(10), primary_key=True)          # correspond aux classes
    niveau_id = db.Column(db.Integer, nullable=False)
    option_id = db.Column(db.String(10), db.ForeignKey('option_concours.id'))
    option = db.relationship('OptionConcours', back_populates='classes')
    inscriptions = db.relationship('InscriptionConcours', back_populates='classe')

    def niveau(self, locale='fr'):
        niveau = NIVEAUX[self.niveau_id]
        if locale == 'fr':
            return niveau.nom_fr
        return niveau.nom_en
    

class CentreConcours(db.Model):
    
    __bind_key__ = 'concours_v0'
    __tablename__ = 'centre_concours'

    id = db.Column(db.String(5), primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    inscriptions = db.relationship('InscriptionConcours', back_populates='centre')


class InscriptionConcours(db.Model):
    __bind_key__ = 'concours_v0'
    __tablename__ = 'inscription_concours'

    # Métadonnées
    id = db.Column(db.String(20), primary_key=True)  # numero paiement
    numero_dossier = db.Column(db.String(20), primary_key=True)  # numero paiement
    date_inscription = db.Column(db.DateTime, default=datetime.now)
    annee_concours = '2025/2026'

    # Informations personnelles de base
    nom = db.Column(db.String(200), nullable=False)
    prenom = db.Column(db.String(200), nullable=True, default='')
    date_naissance = db.Column(db.DateTime, nullable=False)
    lieu_naissance = db.Column(db.String(100), nullable=False)
    sexe_id = db.Column(db.String(10), nullable=False)  
    statut_matrimonial_id = db.Column(db.String(50), nullable=False)
    
    # Origine géographique
    departement_origine_id = db.Column(db.String(100), nullable=False)
    langue_id = db.Column(db.String(10), nullable=False)  
    
    # Coordonnées
    telephone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    
    # options examens
    classe_id = db.Column(db.String(10), db.ForeignKey('classe_concours.id'))
    classe = db.relationship('ClasseConcours', back_populates='inscriptions')
    centre_id = db.Column(db.String(10), db.ForeignKey('centre_concours.id'))
    centre = db.relationship('CentreConcours', back_populates='inscriptions')

    # cursus academique
    diplome_id = db.Column(db.String(200), db.ForeignKey('diplome_concours.id'))
    diplome = db.relationship('DiplomeConcours', back_populates='inscriptions')
    cursus = db.relationship('EtapeCursus', back_populates='inscription')

    @property
    def nom_complet(self):
        return ' '.join([self.nom, self.prenom])

    def sexe(self, locale='fr'):
        sexe = SEXES[self.sexe_id]
        if locale == 'fr':
            return sexe.nom_fr
        return sexe.nom_en
    
    def statut_matrimonial(self, locale='fr'):
        statut = SITUATIONS[self.statut_matrimonial_id]
        if locale == 'fr':
            return statut.nom_fr
        return statut.nom_en
    
    def langue(self, locale='fr'):
        langue = LANGUES[self.langue_id]
        if locale == 'fr':
            return langue.nom_fr
        return langue.nom_en
    
    
    @property
    def naissance(self):
        return f"{self.date_naissance.strftime('%d/%m/%Y')} à {self.lieu_naissance}"
    
    @property
    def departement_origine(self):
        query = db.session.query(Departement)
        query = query.filter_by(id=self.departement_origine_id)
        return query.one_or_none()


class EtapeCursus(db.Model):
    __bind_key__ = 'concours_v0'
    __tablename__ = 'etape_cursus'

    id = db.Column(db.Integer, primary_key=True) 
    annee = db.Column(db.String(20), nullable=False)
    etablissement = db.Column(db.String(200), nullable=False)
    diplome = db.Column(db.String(200), nullable=False)
    mention = db.Column(db.String(50), nullable=False)
    inscription_id = db.Column(db.String(20), db.ForeignKey('inscription_concours.id'))
    inscription = db.relationship('InscriptionConcours', back_populates='cursus')
