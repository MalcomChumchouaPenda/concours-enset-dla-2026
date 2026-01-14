
from .models import db, DepartementAcademique, Niveau, Filiere, Classe


def chercher_classe(id):
    query = db.session.query(Classe)
    query = query.filter_by(id=id)
    return query.one_or_none()

def list_departements():
    query = db.session.query(DepartementAcademique)
    return [(obj.id, obj.nom) for obj in query.all()]

def list_niveaux():
    query = db.session.query(Niveau)
    return [(obj.id, obj.nom) for obj in query.all()]

def list_filieres():
    query = db.session.query(Filiere)
    return [(obj.id, obj.nom) for obj in query.all()]
