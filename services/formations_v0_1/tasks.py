
from .models import db, DepartementAcademique, Niveau, Filiere, Classe


def chercher_classe(id):
    query = db.session.query(Classe)
    query = query.filter_by(id=id)
    return query.one_or_none()

def list_departements(full_id=False):
    query = db.session.query(DepartementAcademique)
    if full_id:
        return [(obj.full_id, obj.nom) for obj in query.all()]
    return [(obj.id, obj.nom) for obj in query.all()]

def list_niveaux():
    query = db.session.query(Niveau)
    return [(obj.id, obj.nom) for obj in query.all()]

def list_filieres(full_id=False):
    query = db.session.query(Filiere)
    if full_id:
        return [(obj.full_id, obj.nom) for obj in query.all()]
    return [(obj.id, obj.nom) for obj in query.all()]

def list_classes(full_id=False):
    query = db.session.query(Classe)
    if full_id:
        return [(obj.full_id, obj.nom) for obj in query.all()]
    return [(obj.id, obj.nom) for obj in query.all()]