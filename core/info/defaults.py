
from core.config import db
from core.utils import Stat, Alert
from .schemas import Course


data = [dict(id="ECO3", title="Economie 3"),
        dict(id="ECO4", title="Economie 4"),
        dict(id="INFO5", title="Informatique 5")]


def init_data():
    for row in data:
        course = Course(**row)
        db.session.merge(course)
    db.session.commit()


def init_stats(user):
    stats = []
    if user.has_role('teacher'):
        stats.extend([
            Stat('Demo', 'Étudiants encadrés', value='28 étudiants', rank=99),
            Stat('Demo', 'Cours ce semestre', value="4 unités d'enseignement", rank=99),
            Stat('Demo', 'Copies à corriger', value='132 copies en attente', rank=99)
        ])
    if user.has_role('student'):
        stats.extend([
            Stat('Demo', 'Crédits validés', value='72/120 ECTS', rank=99),
            Stat('Demo', 'Moyenne générale', value='13.8 / 20', rank=99),
        ])
    return stats


def init_alerts(user):
    alerts = []
    if user.has_role('teacher'):
        alerts.extend([
            Alert('Date limite de saisie des notes', "La saisie des notes pour l'UE « Programmation Orientée Objet » doit être finalisée avant le 30 mai 2025."),
            Alert('Nouveau message administratif', "Une réunion pédagogique est prévue le 3 juin à 10h en salle B203. Votre présence est requise.")
        ])
    return alerts
