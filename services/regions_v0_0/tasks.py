
from .models import db, Pays, Region, Departement


def chercher_departement(id):
    query = db.session.query(Departement)
    query = query.filter_by(id=id)
    return query.one_or_none()

def list_nationalites(full_id=False):
    query = db.session.query(Pays)
    if full_id:
        return [(obj.full_id, obj.nom) for obj in query.all()]
    return [(obj.id, obj.nom) for obj in query.all()]

def list_regions(full_id=False):
    query = db.session.query(Region)
    if full_id:
        return [(obj.full_id, obj.nom) for obj in query.all()]
    return [(obj.id, obj.nom) for obj in query.all()]

def list_departements(full_id=False):
    query = db.session.query(Departement)
    if full_id:
        return [(obj.full_id, obj.nom) for obj in query.all()]
    return [(obj.id, obj.nom) for obj in query.all()]

