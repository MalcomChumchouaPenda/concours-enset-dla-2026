
import os
import csv
from core.config import db
from .models import (
    Niveau, 
    Formation, 
    DepartementAcademique,
    Filiere,
    Classe
)


store_dir = os.path.join(os.path.dirname(__file__), 'store')

def _read_csv(filename, sep=','):
    filepath = os.path.join(store_dir, filename)
    with open(filepath, mode='r') as file:
        reader = csv.DictReader(file, delimiter=sep)
        records = list(reader)
    return records


def init_data():
    # niveaux
    data = _read_csv('niveaux.csv', sep=',')
    for row in data:
        niveau = Niveau(
            id  = row['code'],
            code_cycle = row['cycle'],
            nom = row['nom']
        )
        db.session.merge(niveau)
    db.session.commit()

    # formations
    formations = [('FI', 1, 'Formation Initiale'), ('CPS', 3, 'Formation Continue (CPS)')]
    for id, code, nom in formations:
        formation = Formation(id=id, code_systhag=code, nom=nom)
        db.session.merge(formation)
    db.session.commit()

    # departements
    data = _read_csv('departements.csv', sep=',')
    for row in data:
        departement = DepartementAcademique(
            id  = row['code'],
            nom = row['nom']
        )
        db.session.merge(departement)
    db.session.commit()
    
    # filieres
    data = _read_csv('filieres.csv', sep=';')
    for row in data:
        filiere = Filiere(
            id  = row['code_filiere'],
            prefix= row['prefix'],
            code_udo = row['code_sco'],
            code_enset = row['code_filiere'],
            nom = row['nom'],
            departement_id = row['code_dept'],
            formation_id = row['code_formation']
        )
        db.session.merge(filiere)
    db.session.commit()

    # classes
    data = _read_csv('classes.csv', sep=';')
    for row in data:
        classe = Classe(
            id  = row['code_filiere'] + row['code_niveau'][-1],
            filiere_id = row['code_filiere'],
            niveau_id = row['code_niveau']
        )
        db.session.merge(classe)
    db.session.commit()

