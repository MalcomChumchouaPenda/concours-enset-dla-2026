
from .models import db, DepartementAcademique, Niveau, Filiere, Classe


def chercher_classe(id):
    query = db.session.query(Classe)
    query = query.filter_by(id=id)
    return query.one_or_none()
