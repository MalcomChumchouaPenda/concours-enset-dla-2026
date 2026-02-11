
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


def _create_user(uid, roleids):
    user = auth_tsk.add_user(uid, uid, '0000')
    for roleid in roleids:
        role = auth_tsk.get_role(roleid)
        auth_tsk.add_role_to_user(user, role)
    return user

def _create_inscr(uid, numero):
    inscr = mdl.InscriptionConcours(
        id = uid,
        numero_dossier = numero,
        prenom = 'ARISTIDE JUNIOR', 
        nom = 'KONOFINO NEMALA', 
        date_naissance = datetime(2026, 1, 22).date(), 
        lieu_naissance = 'DOUALA', 
        sexe_id = 'F', 
        statut_matrimonial_id = 'C', 
        departement_origine_id = 'CO',
        diplome_id = 'BAC_C',
        langue_id = 'EN', 
        classe_id = 'BTP1', 
        centre_id = 'BAF', 
        telephone = '655234566', 
        email = ''
    )
    db.session.add(inscr)
    db.session.commit()
    return inscr

def _create_cursus(uid): 
    for year, diplome in [(2004, 'BAC C'), (2003, 'PROBATOIRE C')]:
        etape = mdl.EtapeCursus(
            annee = year, 
            diplome = diplome, 
            etablissement = 'LYCEE DE NEW-BELL',
            mention = 'ASSEZ BIEN',
            inscription_id = uid
        )  
        db.session.add(etape)
    db.session.commit()


def _init_candidates():
    _create_user('06800000000', ['inscrit_concours'])
    _create_inscr('06800000000', '26BAF-BACCDE-0001')
    _create_cursus('06800000000')


def _init_errors():
    _create_user('06800000001', [])
    _create_user('06800000002', ['candidat_concours'])
    _create_user('06800000003', ['inscrit_concours', 'candidat_concours'])
    _create_user('06800000004', ['inscrit_concours'])

    _create_inscr('06800000001', '26BAF-BACCDE-0002')
    _create_inscr('06800000002', '26BAF-BACCDE-0003')    
    _create_inscr('06800000003', '26BAF-BACCDE-0004')
    _create_inscr('06800000004', None)

    _create_user('06800000005', [])
    _create_user('06800000006', ['candidat_concours'])
    _create_user('06800000007', ['inscrit_concours'])    
    _create_user('06800000008', ['inscrit_concours', 'candidat_concours'])


def init_data():
    _init_concours()    
    config = current_app.config
    if config['DEBUG']:
        _init_candidates()
        _init_errors()
    


