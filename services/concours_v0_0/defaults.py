
import os
import csv
from datetime import datetime
from core.config import db
from core.auth.tasks import add_role, add_user, add_roles_to_user
from . import models as mdl


store_dir = os.path.join(os.path.dirname(__file__), 'store')

def _read_csv(filename, sep=','):
    filepath = os.path.join(store_dir, filename)
    with open(filepath, mode='r') as file:
        reader = csv.DictReader(file, delimiter=sep)
        records = list(reader)
    return records


def init_data():
    session = db.session
    add_role(session, 'candidat', 'Candidat')
    for i in range(10):
        id_ = str(i).rjust(4, '0')
        add_user(session, id_, id_, id_)
        add_roles_to_user(session, id_, 'candidat')
    
    data = _read_csv('diplomes.csv', sep=',')
    for row in data:
        db.session.merge(mdl.DiplomeConcours(
            id  = row['code'],
            nom_fr = row['nom_fr'],
            nom_en = row['nom_en'],
            niveau_id = row['niveau']
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

    test = {
        'id': '0000',
        'prenom': 'yu', 
        'nom': 'KONOFINO NEMALA ARISTIDE JUNIOR', 
        'date_naissance': datetime(2026, 1, 22).date(), 
        'lieu_naissance': 'rt', 
        'sexe_id': 'F', 
        'situation_matrimoniale_id': 'C', 
        'departement_origine_id': 'CO', 
        'langue_id': 'EN', 
        'classe_id': 'BTP1', 
        'centre_id': 'BAF', 
        'telephone': '65523', 
        'email': '',
        'diplome_id':'BAC_C',
        'numero_dossier':'26BAF-BAC-C0001'}
    db.session.add(mdl.InscriptionConcours(**test))
    db.session.commit()

