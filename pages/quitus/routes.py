
import os
import re
import json
import csv
from io import StringIO
from datetime import datetime

import Levenshtein as lv
from flask_login import current_user
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l
from flask import render_template, url_for, redirect, send_file, flash, jsonify
from flask import request, session, current_app
from sqlalchemy import or_, and_

from core.config import db
from core.utils import UiBlueprint
from services.preins_v0_0 import models as pmdl
from services.formations_v0_0 import models as fmdl
from services.quitus_v0_0 import models as qmdl
# from services.preins_v0_0.models import Inscription, Requete


ui = UiBlueprint(__name__)
static_dir = os.path.join(os.path.dirname(__file__), 'static')
temp_dir = os.path.join(static_dir, 'temp')
os.makedirs(temp_dir, exist_ok=True)


@ui.before_request
def prepare_request():
    _clean_temp_files()

@ui.after_request
def cleanup_request(response):
    _clean_temp_files()
    return response


def _clean_temp_files():
    filenames = os.listdir(temp_dir)
    logger = current_app.logger
    logger.debug(f'cleaning temp {len(filenames)} files :')
    for filename in filenames:
        filepath = os.path.join(temp_dir, filename)
        try:
            os.remove(filepath)
            logger.debug(f'clean {filename}')
        except OSError as e:
            logger.warning(e)
            continue


@ui.route('/')
@ui.route('/files')
def files():
    return render_template('quitus-files.jinja')


def _verification_matricule(admission, inscription):
    matricule = admission.matricule
    if not matricule:
        return False
    return True

def _verification_noms(admission, inscription):
    nom1 = admission.nom_complet.upper()
    nom2 = inscription.nom_complet.upper()
    ratio = lv.ratio(nom1, nom2)
    print('\t', ratio, nom1, nom2)
    return ratio >= 0.65

def _verification_quitus_existants(admission, inscription):
    matricule = admission.matricule
    annee = admission.communique.annee_academique
    query = qmdl.Quitus.query.filter_by(annee_academique=annee)
    query = query.filter_by(matricule=matricule)
    return query.count() > 0


@ui.route('/download-quitus/new')
@ui.roles_accepted('admin_quitus')
def download_new_quitus():
    num_inscr = 0
    session = db.session
    inscriptions = session.query(pmdl.Inscription).all()
    output_name = 'nouveaux_etudiants.csv'
    output_path = os.path.join(temp_dir, output_name)
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['matricule', 'nom', 'prenom', 'date_naiss', 
                         'lieu_naiss', 'sexe', 'situation_mat', 'pays',
                         'region', 'dept_orig', 'dept_acad', 'filiere',
                         'etape', 'formation', 'niveau', 'statut',
                         'langue', 'annee_acad', 'date_inscr'])
        for inscr in inscriptions:
            if inscr.modified:
                continue
            admission = inscr.admission
            matricule = admission.matricule
            if matricule is None:
                continue
            if not matricule[:2] == admission.communique.annee_academique[2:4]:
                continue
            if not _verification_matricule(admission, inscr):
                continue
            if not _verification_noms(admission, inscr):
                continue
            if _verification_quitus_existants(admission, inscr):
                continue
            classe = admission.classe 
            departement = inscr.departement_origine
            writer.writerow([admission.matricule, 
                             inscr.nom.upper(), 
                             inscr.prenom.upper() if inscr.prenom else " ",
                             inscr.date_naissance.strftime('="%Y-%m-%d"'),
                             inscr.lieu_naissance.upper(), 
                             inscr.sexe_id, 
                             'c',
                             departement.region.pays.code_udo,
                             departement.region.code_udo,
                             departement.code_udo,
                             classe.filiere.departement_id,
                             classe.filiere.code_udo,
                             classe.id,
                             classe.filiere.formation.code_systhag,
                             classe.niveau.code_cycle,
                             admission.statut,
                             inscr.langue_id.lower(),
                             admission.communique.annee_academique,
                             inscr.date_inscription.strftime('="%Y-%m-%d %H:%M:%S"')])
            num_inscr += 1
    flash(f'{num_inscr} quitus nouveaux etudiants a generer', 'success')
    return send_file(output_path,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='quitus_nouveaux_a_generer.csv')


@ui.route('/download-quitus/old')
@ui.roles_accepted('admin_quitus')
def download_old_quitus():
    num_inscr = 0
    session = db.session
    inscriptions = session.query(pmdl.Inscription).all()
    output_name = 'anciens_etudiants.csv'
    output_path = os.path.join(temp_dir, output_name)
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['matricule', 'dept_acad', 'filiere',
                         'etape', 'formation', 'niveau', 'statut',
                         'annee_acad', 'date_inscr'])
        for inscr in inscriptions:
            if inscr.modified:
                continue
            admission = inscr.admission
            matricule = admission.matricule
            if matricule is None:
                continue
            if matricule[:2] == admission.communique.annee_academique[2:4]:
                continue
            if not _verification_matricule(admission, inscr):
                continue
            if not _verification_noms(admission, inscr):
                continue
            if _verification_quitus_existants(admission, inscr):
                continue
            classe = admission.classe
            writer.writerow([admission.matricule,
                             classe.filiere.departement_id,
                             classe.filiere.code_udo,
                             classe.id,
                             classe.filiere.formation.code_systhag,
                             classe.niveau.code_cycle,
                             admission.statut,
                             admission.communique.annee_academique,
                             inscr.date_inscription.strftime('="%Y-%m-%d %H:%M:%S"')])
            num_inscr += 1
    flash(f'{num_inscr} quitus anciens etudiants a generer', 'success')
    return send_file(output_path,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='quitus_anciens_a_generer.csv')


@ui.route('/download-requetes')
@ui.roles_accepted('admin_quitus')
def download_requetes():
    session = db.session
    requetes = session.query(pmdl.Requete).all()
    output_name = 'requetes.csv'
    output_path = os.path.join(temp_dir, output_name)
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['identifiant', 'nom_communique', 'filiere_communique', 'niveau_communique', 
                         'correction_nom', 'correction_filiere', 'correction_niveau',
                         'annee_acad', 'date_requete'])
        for req in requetes:
            admission = req.admission
            classe = admission.classe
            id_ = req.admission_id
            nom_communique = admission.nom_complet
            filiere_communique = classe.filiere.code_udo
            niveau_communique = classe.niveau.code_cycle
            nom_correct = req.nom_correct if req.nom_correct else ""
            filiere_correct = req.filiere_correct.code_udo if req.filiere_correct_id else ""
            niveau_correct = req.niveau_correct.code_cycle if req.niveau_correct_id else ""
            writer.writerow([id_, nom_communique, filiere_communique, niveau_communique, 
                             nom_correct, filiere_correct, niveau_correct,
                             admission.communique.annee_academique,
                             req.date_requete.strftime('="%Y-%m-%d %H:%M:%S"')])
    return send_file(output_path,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='requetes.csv')


@ui.route('/download-anomalies')
@ui.roles_accepted('admin_quitus')
def download_anomalies():
    session = db.session
    inscriptions = session.query(pmdl.Inscription).all()
    output_name = 'anomalies.csv'
    output_path = os.path.join(temp_dir, output_name)
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['identifiant', 'nom_communique', 'nom_inscription', 
                         'matricule', 'telephone', 'annee_acad', 
                         'date_inscription'])
        for inscr in inscriptions:
            admission = inscr.admission
            if inscr.modified:
                continue
            if _verification_noms(admission, inscr):
                continue
            writer.writerow([admission.id, admission.nom_complet.upper(),
                             inscr.nom_complet.upper(), admission.matricule,
                             inscr.telephone, admission.communique.annee_academique,
                             inscr.date_inscription.strftime('="%Y-%m-%d %H:%M:%S"')])
    return send_file(output_path,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='anomalies.csv')


@ui.route('/upload-quitus', methods=['POST'])
@ui.roles_accepted('admin_quitus')
def update_quitus():
    if not request.is_json:
        return jsonify({'error':'le contenu doit etre json'}), 400
    
    i = 0
    data = request.get_json()
    session = db.session
    for row in data:
        quitus = qmdl.Quitus(
            id = row['num_quitus'],
            matricule = row['matricule'],
            code_etape = row['code_etape'],
            annee_academique = row['annee_academique'],
            tranche = row['code_tranche']
        )
        session.merge(quitus)
        i += 1
    session.commit()
    return jsonify({'message': f'{i} quitus traites'}), 200