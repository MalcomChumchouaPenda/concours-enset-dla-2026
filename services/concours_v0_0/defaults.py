
import os
import csv
from flask import current_app
from datetime import datetime
from core.config import db
from core.auth import tasks as auth_tsk
from . import models as mdl


store_dir = os.path.join(os.path.dirname(__file__), 'store')

def _read_csv(filename, sep=','):
    filepath = os.path.join(store_dir, filename)
    with open(filepath, mode='r') as file:
        reader = csv.DictReader(file, delimiter=sep)
        records = list(reader)
    return records

def _init_concours():
    role = auth_tsk.get_role('candidat_concours')
    if role is None:
        auth_tsk.add_role('candidat_concours', 'Candidat')
    role = auth_tsk.get_role('inscrit_concours')
    if role is None:
        auth_tsk.add_role('inscrit_concours', 'Candidat inscrit')

    data = _read_csv('diplomes.csv', sep=';')
    for row in data:
        db.session.merge(mdl.DiplomeConcours(
            id  = row['code'],
            nom_fr = row['nom_fr'],
            nom_en = row['nom_en'],
            niveau_id = row['niveau'],
            ouvert = row['ouvert'],
            prefix = row['prefix']
        ))
    db.session.commit()
    
    data = _read_csv('filieres.csv', sep=',')
    for row in data:
        db.session.merge(mdl.FiliereConcours(
            id  = row['code'],
            nom_fr = row['nom_fr'],
            nom_en = row['nom_en']
        ))
    db.session.commit()
    
    data = _read_csv('options.csv', sep=';')
    for row in data:
        db.session.merge(mdl.OptionConcours(
            id  = row['code_filiere'],
            nom_fr = row['nom_fr'],
            nom_en = row['nom_en'],
            filiere_id = row['code_dept']
        ))
    db.session.commit()

    data = _read_csv('classes.csv', sep=';')
    for row in data:
        db.session.merge(mdl.ClasseConcours(
            id  = row['code_filiere'] + str(row['niveau']),
            option_id = row['code_filiere'],
            niveau_id = row['niveau']
        ))
    db.session.commit()

    data = _read_csv('centres.csv', sep=',')
    for row in data:
        db.session.merge(mdl.CentreConcours(
            id  = row['code'],
            nom = row['nom']
        ))
    db.session.commit()


def _init_candidates():
    uid = '0000'
    pwd = '0000'

    candidat = {
        'id': uid,
        'prenom': 'ARISTIDE JUNIOR', 
        'nom': 'KONOFINO NEMALA', 
        'date_naissance': datetime(2026, 1, 22).date(), 
        'lieu_naissance': 'DOUALA', 
        'sexe_id': 'F', 
        'statut_matrimonial_id': 'C', 
        'departement_origine_id': 'CO', 
        'langue_id': 'EN', 
        'classe_id': 'BTP1', 
        'centre_id': 'BAF', 
        'telephone': '655234566', 
        'email': '',
        'diplome_id':'BAC_C',
        'numero_dossier':'26BAF-BACCDE-0001'
    }
    
    cursus = [
        {
            'annee': '2004', 
            'diplome': 'BAC C', 
            'etablissement': 'LYCEE DE NEW-BELL',
            'mention': 'ASSEZ BIEN',
            'inscription_id':uid,
        },
        {
            'annee': '2003', 
            'diplome': 'PROBATOIRE C', 
            'etablissement': 'LYCEE DE NEW-BELL',
            'mention': 'BIEN',
            'inscription_id':uid,
        }
    ]
    
    role = auth_tsk.get_role('inscrit_concours')
    user = auth_tsk.add_user(uid, candidat['id'], pwd)
    auth_tsk.add_role_to_user(user, role)

    db.session.add(mdl.InscriptionConcours(**candidat))
    for row in cursus:
        db.session.add(mdl.EtapeCursus(**row))
    db.session.commit()

def init_data():
    _init_concours()    
    config = current_app.config
    if config['DEBUG']:
        _init_candidates()
    


