
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func
from core.config import db
from services.formations_v0_0.models import Classe, Filiere, Niveau
from services.regions_v0_0.models import Departement


SEXES = {'F':'Feminin', 'M':'Masculin'}
SITUATIONS = {'C': 'Celibataire', 'M':'Marie(e)', 'V':'Veuf(ve)', 'D':'Divorce(e)'}
LANGUES = {'FR': 'Francais', 'EN': 'Anglais'}


class CommuniqueAdmission(db.Model):
    __bind_key__ = 'preins_v0'
    __tablename__ = 'communiques_admissions'
    
    id = db.Column(db.String(20), primary_key=True)
    numero = db.Column(db.String(50), nullable=False)
    objet = db.Column(db.String(150), nullable=False)
    annee_academique = db.Column(db.String(20), nullable=False)


class Admission(db.Model):
    __bind_key__ = 'preins_v0'
    __tablename__ = 'admissions'
    
    id = db.Column(db.String(12), primary_key=True)
    nom_complet = db.Column(db.String(400), nullable=False)
    classe_id = db.Column(db.String(10), nullable=False)
    statut = db.Column(db.String(10), nullable=False) # code type
    matricule = db.Column(db.String(9), nullable=True)
    max_inscriptions = db.Column(db.Integer, default=3)
    max_requetes = db.Column(db.Integer, default=2)
    communique_id = db.Column(db.String(20), db.ForeignKey('communiques_admissions.id'))

    communique = db.relationship('CommuniqueAdmission')
    inscriptions = db.relationship('Inscription', 
                                   back_populates='admission', 
                                   order_by='Inscription.date_inscription.desc()')
    requetes = db.relationship('Requete', 
                               back_populates='admission',
                               order_by='Requete.date_requete.desc()')
    
    @property
    def classe(self):
        query = db.session.query(Classe)
        query = query.filter_by(id=self.classe_id)
        return query.one_or_none()
    
    @property
    def classe_paiement(self):
        classe = self.classe
        if classe is not None:
            code_filiere = classe.filiere.code_udo
            code_niveau = classe.niveau_id[-1]
            if self.statut[0] == 'A':
                return f'{code_filiere}_AL{code_niveau}'
            return f'{code_filiere}{code_niveau}'
                

class Inscription(db.Model):
    __bind_key__ = 'preins_v0'
    __tablename__ = 'inscriptions'
    id = db.Column(db.Integer, primary_key=True)
    admission_id = db.Column(db.String(12), db.ForeignKey('admissions.id'))
    admission = db.relationship('Admission', back_populates='inscriptions')
    
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
    diplome = db.Column(db.String(200), nullable=False)
    annee_diplome = db.Column(db.Integer, nullable=False)
    
    # Informations du père/tuteur
    nom_pere = db.Column(db.String(200), nullable=True)
    profession_pere = db.Column(db.String(100), nullable=True)
    telephone_pere = db.Column(db.String(20), nullable=True)
    residence_pere = db.Column(db.String(100), nullable=True)
    
    # Informations de la mère
    nom_mere = db.Column(db.String(200), nullable=True)
    profession_mere = db.Column(db.String(100), nullable=True)
    telephone_mere = db.Column(db.String(20), nullable=True)
    residence_mere = db.Column(db.String(100), nullable=True)
    
    # Métadonnées
    date_inscription = db.Column(db.DateTime, default=datetime.now) 


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
    
    @property
    def modified(self):
        others = self.admission.inscriptions
        if len(others) > 1:
            return self != others[0]
        return False
    

class Requete(db.Model):
    __bind_key__ = 'preins_v0'
    __tablename__ = 'requetes'

    id = db.Column(db.Integer, primary_key=True)
    admission_id = db.Column(db.String(12), db.ForeignKey('admissions.id'))
    admission = db.relationship('Admission', back_populates='requetes')

    # erreur d'identite
    nom_correct = db.Column(db.String(400), nullable=True)

    # erreur de filiere
    filiere_correct_id = db.Column(db.String(100), nullable=True)
    niveau_correct_id = db.Column(db.String(10), nullable=True)

    # pieces justificatives
    justificatifs = db.Column(db.Text, nullable=True)

    # Métadonnées
    date_requete = db.Column(db.DateTime, default=datetime.now) 

    @property
    def filiere_correct(self):
        query = db.session.query(Filiere)
        query = query.filter_by(id=self.filiere_correct_id)
        return query.one_or_none()
    
    @property
    def niveau_correct(self):
        query = db.session.query(Niveau)
        query = query.filter_by(id=self.niveau_correct_id)
        return query.one_or_none()
    
    @property
    def modified(self):
        others = self.admission.requetes
        if len(others) > 1:
            return self != others[0]
        return False
