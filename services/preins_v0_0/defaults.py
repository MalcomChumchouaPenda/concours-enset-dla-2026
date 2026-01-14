
import os
import csv
import json
import random
from datetime import datetime
from core.config import db
from core.utils import Stat, Alert
from core.auth.tasks import add_role, add_user, add_roles_to_user
from .models import Admission, Inscription, CommuniqueAdmission, Requete
from .tasks import upload_communiques, upload_admissions, upload_inscriptions, upload_requetes



def init_stats(user):
    stats = []
    session = db.session
    if user.has_role('admin_preins'):
        q1 = session.query(Inscription)
        q2 = session.query(Requete)
        q3 = session.query(Admission)
        q4 = q3.filter(Admission.matricule == None)

        stats.extend([
            Stat('Inscriptions', "Nombre d'inscriptions", value=q1.count(), rank=0),
            Stat('Inscriptions', "Nombre de requetes", value=q2.count(), rank=1),
            Stat('Inscriptions', "Nombre d'admis", value=q3.count(), rank=1),
            Stat('Inscriptions', "Taux d'inscription (en % d'admis)", value=q4.count(), rank=2),
        ])
    return stats


def init_alerts(user):
    alerts = []
    if user.has_role('developper'):
        alerts.extend([
            Alert('Vos quitus ont ete generes', 'PC Portable Dell XPS 15 - Il y a 15 minutes', icon='bi bi-laptop', priority=1),
        ])
    return alerts


def init_data():
    session = db.session
    add_role(session, 'admis', 'Etudiants admis')
    add_role(session, 'admin_preins', 'Gestionnaire Inscription')
    add_roles_to_user(session, 'dev1', 'admin_preins')
    upload_communiques(session, 'communiques_demo.csv', sep=';')
    upload_admissions(session, 'admissions_demo.csv', sep=';')
    upload_inscriptions(session, 'inscriptions_demo.csv', sep=';')
    upload_requetes(session, 'requetes_demo.csv', sep=';')
    
