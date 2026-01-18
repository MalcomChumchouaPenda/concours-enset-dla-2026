
from .models import db, Pays, Region, Departement


def chercher_departement(id):
    query = db.session.query(Departement)
    query = query.filter_by(id=id)
    return query.one_or_none()


