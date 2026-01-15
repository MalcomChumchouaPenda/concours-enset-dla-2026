
import re
from sqlalchemy.exc import IntegrityError
from core.auth.tasks import get_user, add_user, add_roles_to_user
from core.auth.models import User
from services.formations_v0_1.models import Classe, Filiere, Niveau
from services.regions_v0_0.models import Departement
from services.regions_v0_0 import tasks as region_tasks
from services.formations_v0_1 import tasks as format_tasks
from ..models import db, Inscription, Admission, Requete, CommuniqueAdmission


# GESTION DES NOMS

def former_nom(nom, prenom=''):
    resultat = ' '.join([nom, prenom])
    return nettoyer_nom(resultat)

def nettoyer_nom(nom):
    nom = re.sub('\s+', ' ', nom)
    nom = nom.strip()
    nom = nom.upper()
    return nom


# GESTION DES ADMISSIONS

def chercher_admission(id):
    query = db.session.query(Admission)
    query = query.filter_by(id=id)
    admission = query.one_or_none()
    return admission


# GESTION DES MATRICULES

def format_matricule(admission):
    annee = admission.communique.annee_academique[2:4]
    statut = admission.statut[0]
    classe = admission.classe
    prefix = classe.filiere.prefix
    niveau = classe.niveau.id[-1]
    if statut == 'C':
        num_size = 2
        filtre = f'{annee}N{prefix}{niveau}%'
    else:
        if niveau == '4':
            num_size = 2
            filtre = f'{annee}N{prefix}L%{statut}'
        elif niveau == '3':
            num_size = 2
            filtre = f'{annee}N{prefix}B%{statut}'
        else:
            num_size = 3
            filtre = f'{annee}N{prefix}%{statut}'
    return filtre, num_size

def enregistrer_matricule(session, matricule, inscription, admission):
    add_user(session, matricule, inscription.nom, '0000', first_name=inscription.prenom)
    add_roles_to_user(session, matricule, 'student')
    admission.matricule = matricule
    session.commit()

def creer_matricule(session, inscription):
    query = session.query(Admission)
    query = query.filter_by(id=inscription.admission_id)
    admission = query.one()
    filtre, num_size = format_matricule(admission)
    for _ in range(10):
        try:
            count = session.query(User).filter(User.id.like(filtre)).count()
            num = str(count + 1).rjust(num_size, '0')
            matricule = filtre.replace('%', num)
            enregistrer_matricule(session, matricule, inscription, admission)
            return matricule
        except IntegrityError as e:
            session.rollback()


# GESTION DES INSCRIPTIONS

def ajouter_inscription(user, data):
    session = db.session
    matricule = data.pop('matricule')
    inscription = Inscription(**data)
    if matricule:
        query = session.query(Admission)
        query = query.filter_by(id=data['admission_id'])
        admission = query.one()
        enregistrer_matricule(session, matricule, inscription, admission)
    else:
        creer_matricule(session, inscription)
    user.first_name = inscription.prenom
    user.last_name = inscription.nom
    session.add(inscription)
    session.commit()

def modifier_inscription(user, data):
    session = db.session
    inscription = Inscription(**data)
    user.first_name = inscription.prenom
    user.last_name = inscription.nom 
    session.add(inscription)
    session.commit()
    
def corriger_inscription(data):
    matricule = data.pop('matricule')
    session = db.session
    query = session.query(Admission)
    query = query.filter_by(id=data['admission_id'])
    admission = query.one()
    inscription = Inscription(**data)
    if matricule != admission.matricule:
        enregistrer_matricule(session, matricule, inscription, admission)
    session.add(inscription)
    session.commit()

def rechercher_inscription(user_id):
    query = db.session.query(Inscription)
    query = query.filter_by(admission_id=user_id)
    query = query.order_by(Inscription.id.desc())
    inscriptions = query.all()
    if len(inscriptions) == 0:
        return None
    return inscriptions[0]


# GESTION DES REQUETES

def ajouter_requete(data):
    requete = Requete(**data)
    db.session.add(requete)
    db.session.commit()
    return requete


def rechercher_requete(user_id):
    query = db.session.query(Requete)
    query = query.filter_by(admission_id=user_id)
    query = query.order_by(Requete.id.desc())
    requetes = query.all()
    if len(requetes) == 0:
        return None
    return requetes[0]

