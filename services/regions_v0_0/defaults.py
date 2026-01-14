
import os
import csv
from core.config import db
from .models import Pays, Region, Departement


store_dir = os.path.join(os.path.dirname(__file__), 'store')

def _read_csv(filename, sep=','):
    filepath = os.path.join(store_dir, filename)
    with open(filepath, mode='r') as file:
        reader = csv.DictReader(file, delimiter=sep)
        records = list(reader)
    return records


def init_data():
    # pays
    code_etrangers = []
    code_national = "CM"
    data = _read_csv('nationalites.csv', sep=",")
    for row in data:
        id = row['code_enset']
        if id != code_national:
            code_etrangers.append(id)

        pays = Pays(
            id = id,
            code_enset = row['code_enset'],
            code_udo = row['code_udo'],
            nationalite = row['nationalite'],
            nom = row['pays'],
        )
        db.session.merge(pays)
    db.session.commit()

    # regions nationales
    data = _read_csv('regions.csv', sep=",")
    for row in data:
        region = Region(
            id = row['code_enset'],
            pays_id = code_national,
            code_enset = row['code_enset'],
            code_udo = row['code_udo'],
            nom = row['nom'],
        )
        db.session.merge(region)
    db.session.commit()
    
    # regions etrangeres
    for code_etranger in code_etrangers:
        region = Region(
            id = code_etranger,
            pays_id = code_etranger,
            code_enset = 'PB',
            code_udo = 'x',
            etranger = True,
            nom = 'autres'
        )
        db.session.merge(region)
    db.session.commit()

    # departements nationaux
    data = _read_csv('departements.csv', sep=";")
    for row in data:
        departement = Departement(
            id = row['numero'],
            code_udo = row['code'],
            nom = row['departement'],
            region_id = row['region']
        )
        db.session.merge(departement)
    db.session.commit()
    
    # departements etrangers
    for code_etranger in code_etrangers:
        departement = Departement(
            id = code_etranger,
            region_id = code_etranger,
            code_udo = 'AUTRES',
            etranger = True,
            nom = 'autres'
        )
        db.session.merge(departement)
    db.session.commit()

    