
from sqlalchemy.exc import IntegrityError
from core.config import db
from .. import models as mdl


def format_numero(inscr, diplome):
    annee = inscr.annee_concours[-2:]
    centre = inscr.centre_id
    diplome = diplome.prefix
    filtre = f'{annee}{centre}-{diplome}-%'
    num_size = 4
    return filtre, num_size

def creer_numero(inscr):
    diplome = mdl.DiplomeConcours.query.filter_by(id=inscr.diplome_id).one()
    filtre, num_size = format_numero(inscr, diplome)
    query = mdl.InscriptionConcours.query
    query = query.filter(mdl.InscriptionConcours.numero_dossier.like(filtre))
    for _ in range(10):
        try:
            count = query.count()
            num = str(count + 1).rjust(num_size, '0')
            numero = filtre.replace('%', num)
            inscr.numero_dossier = numero
            db.session.commit()
            return numero
        except IntegrityError as e:
            db.session.rollback()

