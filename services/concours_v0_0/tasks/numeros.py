
import re
from sqlalchemy.exc import IntegrityError
from core.auth.tasks import get_user, add_user, add_roles_to_user
from core.auth.models import User
from core.config import db

def format_numero(inscription):
    annee = inscription.annee_concours[-2:]
    centre = inscription.centre_id
    diplome = inscription.diplome_id.replace('_', '-')
    filtre = f'{annee}{centre}-{diplome}%'
    num_size = 4
    return filtre, num_size

def enregistrer_numero(session, numero, inscription):
    add_user(session, numero, inscription.nom, inscription.id, first_name=inscription.prenom)
    add_roles_to_user(session, numero, 'student')
    inscription.numero_dossier = numero
    session.commit()

def creer_numero(session, inscription):
    filtre, num_size = format_numero(inscription)
    for _ in range(10):
        try:
            count = session.query(User).filter(User.id.like(filtre)).count()
            num = str(count + 1).rjust(num_size, '0')
            numero = filtre.replace('%', num)
            enregistrer_numero(session, numero, inscription)
            return numero
        except IntegrityError as e:
            session.rollback()