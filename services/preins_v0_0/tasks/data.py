
import os
import csv
import json
from datetime import datetime
from core.auth.tasks import get_user, add_user, add_roles_to_user
from ..models import Inscription, Admission, Requete, CommuniqueAdmission


cur_dir = os.path.dirname(__file__)
store_dir = os.path.join(os.path.dirname(cur_dir), 'store')


def _read_csv(filename, sep=','):
    filepath = os.path.join(store_dir, filename)
    with open(filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=sep,)
        records = list(reader)
    return records

def _read_json(filename):
    filepath = os.path.join(store_dir, filename)
    with open(filepath, mode='r', encoding='utf-8') as file:
        records = json.load(file)
    return records


def upload_communiques(session, filename, sep=','):
    data = _read_csv(filename, sep=sep)
    for row in data:
        query = session.query(CommuniqueAdmission)
        query = query.filter_by(id=row['id'])
        if not query.first():
            communique = CommuniqueAdmission(**row)
            session.add(communique)
            session.commit()

def download_communiques(session, filename, sep=','):
    headers = ['id', 'numero', 'objet', 'annee_academique']
    filepath = os.path.join(store_dir, filename)
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=sep)
        writer.writerow(headers)
        query = session.query(CommuniqueAdmission)
        for record in query.all():
            writer.writerow([
                record.id, record.numero, record.objet,
                record.annee_academique
            ])


def upload_admissions(session, filename, sep=','):    
    data = _read_csv(filename, sep=sep)
    for row in data:
        id = row['id']
        query = session.query(Admission)
        query = query.filter_by(id=id)
        if not query.first():
            nom = row.pop('nom')
            pwd = row.pop('pwd')
            add_user(session, id, nom, pwd)
            add_roles_to_user(session, id, 'admis')
            if id.startswith('dev'):
                add_roles_to_user(session, id, 'developper')
            matricule = row.get('matricule')
            if matricule:
                add_user(session, matricule, nom, pwd)
                add_roles_to_user(session, matricule, 'student')
            row['nom_complet'] = nom
            session.add(Admission(**row))
            session.commit()

def download_admissions(session, filename, sep=','):
    headers = ['id', 'nom', 'statut', 'classe_id', 
               'communique_id', 'matricule']
    filepath = os.path.join(store_dir, filename)
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=sep)
        writer.writerow(headers)
        query = session.query(Admission)
        for record in query.all():
            writer.writerow([
                record.id, record.nom_complet, record.statut,
                record.classe_id, record.communique_id,
                record.matricule
            ])


def upload_inscriptions(session, filename, sep=','):
    data = _read_csv(filename, sep=sep)
    for row in data:
        query = session.query(Inscription)
        query = query.filter_by(admission_id=row['admission_id'])
        if not query.first():
            dkey = 'date_naissance'
            row[dkey] = datetime.strptime(row[dkey], '%d/%m/%Y')
            session.merge(Inscription(**row))
            session.commit()

def download_inscriptions(session, filename, sep=','):
    headers = ['id', 'admission_id', 'nom', 'prenom', 'date_naissance', 'lieu_naissance',
               'sexe_id', 'situation_matrimoniale_id', 'departement_origine_id',
               'telephone', 'email', 'langue_id', 'diplome', 'annee_diplome',
               'nom_pere', 'profession_pere', 'telephone_pere', 'residence_pere',
               'nom_mere', 'profession_mere', 'telephone_mere', 'residence_mere',
               'date_inscription']
    filepath = os.path.join(store_dir, filename)
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=sep)
        writer.writerow(headers)
        query = session.query(Inscription)
        for record in query.all():
            writer.writerow([
                record.id, record.admission_id, record.nom, record.prenom,
                record.date_naissance.strftime('%Y-%m-%d'), record.lieu_naissance,
                record.sexe_id, record.situation_matrimoniale_id, record.departement_origine_id,
                record.telephone, record.email, record.langue_id, record.diplome, 
                record.annee_diplome, record.nom_pere, record.profession_pere,
                record.telephone_pere, record.residence_pere, record.nom_mere,
                record.profession_mere, record.telephone_mere, record.residence_mere,
                record.date_inscription.strftime('%Y-%m-%d %H:%M:%S')
            ])


def upload_requetes(session, filename, sep=','):
    data = _read_csv(filename, sep=sep)
    for row in data:
        query = session.query(Requete)
        query = query.filter_by(admission_id=row['admission_id'])
        if not query.first():
            session.merge(Requete(**row))
            session.commit()   

def download_requetes(session, filename, sep=','):
    headers = ['id', 'admission_id', 'nom_correct', 
               'filiere_correct_id','niveau_correct_id', 
               'justificatifs', 'date_requete']
    filepath = os.path.join(store_dir, filename)
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=sep)
        writer.writerow(headers)
        query = session.query(Requete)
        for record in query.all():
            writer.writerow([
                record.id, record.admission_id, record.nom_correct,
                record.filiere_correct_id, record.niveau_correct_id,
                record.justificatifs, record.date_requete.strftime('%Y-%m-%d %H:%M:%S')
            ])
