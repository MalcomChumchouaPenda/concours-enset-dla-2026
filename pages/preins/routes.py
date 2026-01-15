
import os
import re
import json
import Levenshtein as lv
from datetime import datetime

from flask_login import current_user
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l
from flask import render_template, url_for, redirect, send_file, flash, jsonify
from flask import request, session, current_app
from sqlalchemy import or_, and_

from core.config import db
from core.utils import UiBlueprint
from core.auth import tasks as atsk
from services.preins_v0_0 import tasks as tsk
from services.preins_v0_0 import models as mdl
from services.formations_v0_1 import models as fmdl
# from services.preins_v0_0.models import Inscription, Requete
from . import forms


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


@ui.route('/procedures')
@ui.login_required
def doc():
    nom_fichier = 'procedures_inscription_auditeurs_libres_2025_2026.jpg'
    chemin_doc = os.path.join(static_dir, 'images', 'procedures.jpg')
    return send_file(chemin_doc, as_attachment=True, download_name=nom_fichier)

@ui.route('/')
@ui.roles_accepted('admis')
def info():
    user_id = current_user.id
    inscription = tsk.rechercher_inscription(user_id)
    if inscription is None:
        return redirect(url_for('preins.new_info'))
    return render_template('preins-view-info.jinja', inscription=inscription)


def _pretraitement_inscription(data):
    # suppression des colonnes inutiles
    data['departement_origine_id'] = data['departement_origine_id'].split('-')[-1]
    inutiles = ['departement_academique', 'option', 'niveau', 'nationalite_id', 
                'region_origine_id', 'csrf_token']
    for name in inutiles:
        data.pop(name)

    # mise en majuscule des colonnes
    col_maj = ['nom', 'prenom', 'lieu_naissance', 'diplome',
               'nom_pere', 'profession_pere', 'residence_pere',
               'nom_mere', 'profession_mere', 'residence_mere']
    for name in col_maj:
        data[name] = data[name].upper()
    return data

def _verification_matricule(admission, data):
    matricule = data['matricule']
    if matricule:
        if admission.classe_id[:2] == 'CP':
            msg = f"Le matricule '{matricule}' est invalide "
            msg += '(Vous êtes un nouveau étudiant CPS)'
            return False, msg
        elif admission.classe_id[-1] != '4':
            msg = f"Le matricule '{matricule}' est invalide "
            msg += '(Vous êtes un nouveau étudiant)'
            return False, msg
        elif 'dipet' not in data['diplome'].lower():
            msg = f"Le matricule '{matricule}' est invalide "
            msg += '(Vous êtes un nouveau étudiant)'
            return False, msg
    return True, ''

def _verification_noms(admission, data):
    nom_complet = tsk.former_nom(data['nom'], data['prenom'])
    ratio = lv.ratio(nom_complet.upper(), admission.nom_complet.upper())
    if ratio >= 0.65:
        return True, ''
    msg = f"Ce compte est reserve a l'etudiant <b>{admission.nom_complet}</b> "
    msg += "(Vous n'etes pas dans votre compte)"
    return False, msg


@ui.route('/new', methods=['GET', 'POST'])
@ui.roles_accepted('admis')
def new_info():
    user_id = current_user.id
    inscription = mdl.Inscription() 
    admission = tsk.chercher_admission(user_id)
        
    # create a edit form
    form = forms.InfoForm(obj=inscription)
    form.nationalite_id.choices = forms.choices(tsk.lister_nationalites())
    form.region_origine_id.choices = forms.choices(tsk.lister_regions())
    form.departement_origine_id.choices = forms.choices(tsk.lister_departements_origines())
    
    # traitement et enregistrement des donnees
    # print('\ndata', form.data)
    # print('\nerrors', form.errors)
    # print('\nform', request.form)
    if form.validate_on_submit():
        data = form.data
        valid, msg = _verification_matricule(admission, data)
        if not valid:
            flash(msg, 'warning')
            return redirect(url_for('preins.new_info'))
        
        valid, msg = _verification_noms(admission, data)
        if not valid:
            flash(msg, 'danger')
            return redirect(url_for('preins.new_info'))

        # print('\n', valid, data)
        data['admission_id'] = admission.id
        data = _pretraitement_inscription(data)
        tsk.ajouter_inscription(current_user, data)
        flash('inscription effectue avec succes', 'success')
        return redirect(url_for('preins.info'))

    # fixation des valeurs par defaut
    classe = admission.classe
    form.matricule.data = admission.matricule
    form.departement_academique.data = classe.filiere.departement.nom.upper()
    form.option.data = classe.filiere.nom.upper()
    form.niveau.data = classe.niveau.nom.upper()
    return render_template('preins-add-info.jinja', form=form)


@ui.route('/edit', methods=['GET', 'POST'])
@ui.roles_accepted('admis')
def edit_info():
    user_id = current_user.id
    inscription = tsk.rechercher_inscription(user_id)
    if inscription is None:
        return redirect(url_for('preins.new_info'))
    
    # creation du formulaire avce controle des modifications
    admission = inscription.admission
    if request.method == 'POST':
        form = forms.InfoForm()
    else:
        count_max = admission.max_inscriptions
        count = len(admission.inscriptions)
        if count > count_max:
            flash(f'Vous ne pouvez modifier cette fiche plus de {count_max} fois', 'danger')
            return redirect(url_for('preins.info'))
        flash(f'Vous pourrez encore modifier cette fiche {count_max-count+1} fois', 'warning')
        form = forms.InfoForm(obj=inscription)
    
    # parametrage des options
    form.nationalite_id.choices = forms.choices(tsk.lister_nationalites())
    form.region_origine_id.choices = forms.choices(tsk.lister_regions())
    form.departement_origine_id.choices = forms.choices(tsk.lister_departements_origines())
    
    # traitement et enregistrement des donnees
    # print('\n', form.data)
    if form.validate_on_submit():
        data = form.data
        data['admission_id'] = admission.id
        data = _pretraitement_inscription(data)
        data.pop('matricule')
        tsk.modifier_inscription(current_user, data) 
        flash('modification effectue avec succes', 'success')
        return redirect(url_for('preins.info'))

    # fixation des valeurs par defaut
    classe = admission.classe
    form.matricule.data = admission.matricule
    departement_origine = inscription.departement_origine
    form.departement_academique.data = classe.filiere.departement.nom.upper()
    form.option.data = classe.filiere.nom.upper()
    form.niveau.data = classe.niveau.nom.upper()
    form.nationalite_id.data = departement_origine.region.pays.full_id
    form.region_origine_id.data = departement_origine.region.full_id
    form.departement_origine_id.data = departement_origine.full_id
    return render_template('preins-edit-info.jinja', form=form)


@ui.route('/print')
@ui.roles_accepted('admis')
def print_info():
    user_id = current_user.id
    inscription = tsk.rechercher_inscription(user_id)
    if inscription is None:
        return redirect(url_for('preins.edit_info'))
    nom_fichier_pdf = f"fiche_inscription_{user_id.lower()}.pdf"
    nom_fichier_pdf = nom_fichier_pdf.replace('-', '_')
    chemin_pdf_final = os.path.join(temp_dir, nom_fichier_pdf)
    fichier_pdf = tsk.generer_fiche_inscription(inscription, chemin_pdf_final)
    return send_file(fichier_pdf, as_attachment=True, download_name=nom_fichier_pdf)


@ui.route('/admin/inscriptions')
@ui.roles_accepted('admin_preins')
def search_infos():
    filters = request.args.get('filters', '{}')
    filters = json.loads(filters)
    keywords = request.args.get('keywords', '{}')
    keywords = json.loads(keywords)

    # filtre par classe
    if len(filters) > 0:
        title = 'Fiches '

        # identification des classes
        query = db.session.query(fmdl.Classe)
        query = query.join(fmdl.Filiere)
        opt_id = filters.get('filiere_id')
        dept_id = filters.get('departement_academique_id')
        if opt_id:
            title += f"pour option {opt_id} "
            query = query.filter(fmdl.Filiere.id==opt_id)
        elif dept_id:
            title += f'du Departement {dept_id} '
            query = query.filter(fmdl.Filiere.departement_id==dept_id)
        niv_id = filters.get('niveau_id')
        if niv_id:
            title += f'Niveau {niv_id[-1]}'
            query = query.filter(fmdl.Classe.niveau_id==niv_id)

        # identification des inscriptions
        classe_ids = [classe.id for classe in query.all()]
        if len(classe_ids) == 0:
            filtered = []
        else:
            query = db.session.query(mdl.Inscription)
            query = query.join(mdl.Admission)
            query = query.filter(mdl.Admission.classe_id.in_(classe_ids))
            nom_exp = keywords.get('name')
            if nom_exp:
                title += f'"{nom_exp}"'
                nom_exp = nom_exp.upper().strip()
                nom_exp = re.sub('\s+', '%', nom_exp)
                nom_exp = f'%{nom_exp}%'
                query = query.filter(mdl.Inscription.nom_complet.like(nom_exp))
            id_exp = keywords.get('id')
            if id_exp:
                title += f'{nom_exp}'
                query = query.filter(or_(mdl.Admission.id==id_exp, 
                                        mdl.Admission.matricule==id_exp))
            query = query.order_by(mdl.Inscription.date_inscription.desc())
            print('\n', query.statement)
            filtered = query.all()

    # recherche par mots cles
    elif len(keywords) > 0:
        title = 'Resultat recherche '
        query = db.session.query(mdl.Inscription)
        query = query.join(mdl.Admission)
        id_exp = keywords.get('id')
        if id_exp:
            title += f'{id_exp}'
            query = query.filter(or_(mdl.Admission.id==id_exp, 
                                    mdl.Admission.matricule==id_exp))
        query = query.order_by(mdl.Inscription.date_inscription.desc())
        print('\n', query.statement)
        nom_exp = keywords.get('name')
        if nom_exp:
            title += f'"{nom_exp}"'
            nom_exp = nom_exp.upper().strip()
            nom_exp = re.sub('\s+', ' ', nom_exp)
            filtered = []
            for record in query.all():
                if nom_exp in record.nom_complet.upper():
                    filtered.append(record)
        else:
            filtered = query.all()

    # recherche recentes
    else:
        query = db.session.query(mdl.Inscription)
        query = query.order_by(mdl.Inscription.date_inscription.desc())
        query = query.limit(25)
        title = "Fiches recentes"
        print('\n', query.statement)
        filtered = query.all()
    
    # elaboration des formulaires
    dept_ids = forms.choices(tsk.lister_departements_academiques(), only_keys=True)
    opt_ids = forms.choices(tsk.lister_filieres(), only_keys=True)
    niv_ids = forms.choices(tsk.lister_niveaux(), only_keys=True)
    filter_form = forms.FilterInfosForm()
    filter_form.departement_academique_id.choices = dept_ids
    filter_form.filiere_id.choices = opt_ids
    filter_form.niveau_id.choices = niv_ids
    search_form = forms.SearchInfosForm()

    # retour des items filtres
    page = request.args.get('page', 1, type=int)
    records = db.paginate_list(filtered, page=page, per_page=15)
    return render_template('preins-search-infos.jinja', 
                           records=records,
                           title=title,
                           search_form=search_form, 
                           filter_form=filter_form,
                           keywords=json.dumps(keywords),
                           filters=json.dumps(filters))


@ui.route('/admin/inscriptions', methods=['POST'])
@ui.roles_accepted('admin_preins')
def search_infos_with_keywords():
    form = forms.SearchInfosForm()
    data = form.data
    data.pop('csrf_token')
    keywords = json.dumps({k:v for k,v in data.items() if v})
    return redirect(url_for('preins.search_infos', keywords=keywords))

@ui.route('/admin/inscriptions/filtered', methods=['POST'])
@ui.roles_accepted('admin_preins')
def search_infos_with_filters():
    form = forms.FilterInfosForm()
    data = form.data
    data.pop('csrf_token')
    filters = json.dumps({k:v for k,v in data.items() if v})
    return redirect(url_for('preins.search_infos', filters=filters))


@ui.route('/admin/inscriptions/<search_id>')
@ui.roles_accepted('admin_preins')
def search_info(search_id):
    previous = request.referrer
    if url_for('preins.search_infos') not in previous:
        previous = url_for('preins.search_infos')
    record = db.session.query(mdl.Inscription).filter_by(id=search_id).one()
    if record.modified:
        flash('Cette fiche a ete modifiee!', 'danger')
    return render_template('preins-search-info.jinja', 
                           inscription=record, 
                           previous=previous)


@ui.route('/admin/inscriptions/<search_id>/debug', methods=['GET', 'POST'])
@ui.roles_accepted('admin_preins')
def debug_info(search_id):
    session = db.session
    inscription = session.query(mdl.Inscription).filter_by(id=search_id).one()
    form = forms.InfoForm() if request.method == 'POST' else forms.InfoForm(obj=inscription)
    
    # parametrage des options
    form.nationalite_id.choices = forms.choices(tsk.lister_nationalites())
    form.region_origine_id.choices = forms.choices(tsk.lister_regions())
    form.departement_origine_id.choices = forms.choices(tsk.lister_departements_origines())
    
    # traitement et enregistrement des donnees
    # print('\n', form.data)
    previous = request.args.get('previous', url_for('preins.search_infos'))
    if form.validate_on_submit():
        data = form.data
        data['admission_id'] = inscription.admission_id
        data = _pretraitement_inscription(data)
        tsk.corriger_inscription(data) 
        flash('modification effectue avec succes', 'success')
        return redirect(previous)

    # fixation des valeurs par defaut
    admission = inscription.admission
    classe = admission.classe
    form.matricule.data = admission.matricule
    departement_origine = inscription.departement_origine
    form.departement_academique.data = classe.filiere.departement.nom.upper()
    form.option.data = classe.filiere.nom.upper()
    form.niveau.data = classe.niveau.nom.upper()
    form.nationalite_id.data = departement_origine.region.pays.full_id
    form.region_origine_id.data = departement_origine.region.full_id
    form.departement_origine_id.data = departement_origine.full_id
    return render_template('preins-debug-info.jinja', search_id=search_id,  
                           form=form, previous=previous)


@ui.route('/admin/inscriptions/<search_id>/clean')
@ui.roles_accepted('admin_preins')
def clean_info(search_id):
    session = db.session
    record = session.query(mdl.Inscription).filter_by(id=search_id).one()
    clean_id = record.admission.id
    session.delete(record)
    session.commit()
    flash(f'Une fiche {clean_id} a ete supprimee', 'success')
    previous = request.args.get('previous')
    if previous:
        return redirect(previous)
    return redirect(url_for('preins.search_infos'))


@ui.route('/coming-soon')
@ui.login_required
def coming():
    return render_template('dashboard/coming-soon.jinja',
                           deadline=datetime(2025, 10, 30),
                           page_id="preins_error_pg")


@ui.route('/requete')
@ui.roles_accepted('admis')
def error():
    user_id = current_user.id
    requete = tsk.rechercher_requete(user_id)
    if requete is None:
        return redirect(url_for('preins.new_error'))
    return render_template('preins-view-error.jinja', requete=requete)


@ui.route('/requete/new', methods=['GET', 'POST'])
@ui.roles_accepted('admis')
def new_error():
    user_id = current_user.id
    requete = mdl.Requete() 
    admission = tsk.chercher_admission(user_id)       
    if tsk.rechercher_inscription(user_id) is None:
        flash("Vous devez d'abord vous inscrire", "warning")
        return redirect(url_for('preins.edit_info'))
    
    # create a edit form
    form = forms.ErrorForm(obj=requete)
    form.filiere_correct_id.choices = forms.choices(tsk.lister_filieres())
    form.niveau_correct_id.choices = forms.choices(tsk.lister_niveaux())
    
    # traitement et enregistrement des donnees
    # print('\n', form.data)
    if form.validate_on_submit():
        data = form.data
        data['admission_id'] = admission.id
        inutiles = ['nom_admis', 'filiere_admis', 
                    'niveau_admis', 'csrf_token']
        for name in inutiles:
            data.pop(name)
        tsk.ajouter_requete(data)
        flash('Requete cree avec succes', 'success')
        return redirect(url_for('preins.error'))

    # fixation des valeurs par defaut
    classe = admission.classe
    form.nom_admis.data = admission.nom_complet.upper()
    form.filiere_admis.data = classe.filiere.nom.upper()
    form.niveau_admis.data = classe.niveau.nom.upper()
    return render_template('preins-add-error.jinja', form=form)


@ui.route('requete/edit', methods=['GET', 'POST'])
@ui.roles_accepted('admis')
def edit_error():
    user_id = current_user.id
    requete = tsk.rechercher_requete(user_id)
    if requete is None:
        return redirect(url_for('preins.new_error'))
    
    # creation du formulaire avce controle des modifications
    admission = requete.admission
    if request.method == 'POST':
        form = forms.ErrorForm()
    else:
        count_max = admission.max_requetes
        count = len(admission.requetes)
        if count > count_max:
            flash(f'Vous ne pouvez modifier cette requete plus de {count_max} fois', 'danger')
            return redirect(url_for('preins.error'))
        flash(f'Vous pourrez encore modifier cette requete {count_max-count+1} fois', 'warning')
        form = forms.ErrorForm(obj=requete)
    
    # parametrage des options
    form.filiere_correct_id.choices = forms.choices(tsk.lister_filieres())
    form.niveau_correct_id.choices = forms.choices(tsk.lister_niveaux())
    
    # traitement et enregistrement des donnees
    # print('\n', form.data)
    if form.validate_on_submit():
        data = form.data
        data['admission_id'] = admission.id
        inutiles = ['nom_admis', 'filiere_admis',
                    'niveau_admis', 'csrf_token']
        for name in inutiles:
            data.pop(name)
        tsk.ajouter_requete(data)
        flash('Requete modifiee avec succes', 'success')
        return redirect(url_for('preins.error'))

    # fixation des valeurs par defaut
    classe = admission.classe
    form.nom_admis.data = admission.nom_complet.upper()
    form.filiere_admis.data = classe.filiere.nom.upper()
    form.niveau_admis.data = classe.niveau.nom.upper()
    return render_template('preins-edit-error.jinja', form=form)


@ui.route('/requete/print')
@ui.roles_accepted('admis')
def print_error():
    user_id = current_user.id
    inscription = tsk.rechercher_inscription(user_id)
    requete = tsk.rechercher_requete(user_id)
    if requete is None:
        return redirect(url_for('preins.new_error')) 

    nom_fichier_pdf = f"requete_correction_{user_id.lower()}.pdf"
    nom_fichier_pdf = nom_fichier_pdf.replace('-', '_')
    chemin_pdf_final = os.path.join(temp_dir, nom_fichier_pdf)
    fichier_pdf = tsk.generer_fiche_correction(requete, inscription, chemin_pdf_final)
    return send_file(fichier_pdf, as_attachment=True, download_name=nom_fichier_pdf)


@ui.route('/config/communiques', methods=['POST'])
@ui.roles_accepted('admin_preins')
def config_communiques():
    if not request.is_json:
        return jsonify({'error':'le contenu doit etre json'}), 400
    
    i = j = 0
    data = request.get_json()
    session = db.session
    for row in data:
        query = session.query(mdl.CommuniqueAdmission)
        query = query.filter_by(id=row['id'])
        print(row)
        if not query.first():
            communique = mdl.CommuniqueAdmission(**row)
            session.add(communique)
            session.commit()
            j += 1
        i += 1
    return jsonify({'message': f'{i} communiques analysees, {j} communiques crees'}), 200
    

@ui.route('/config/admissions', methods=['POST'])
@ui.roles_accepted('admin_preins')
def config_admissions():
    if not request.is_json:
        return jsonify({'error':'le contenu doit etre json'}), 400
    
    i = j = 0
    data = request.get_json()
    session = db.session
    for row in data:
        id = row['id']
        query = session.query(mdl.Admission)
        query = query.filter_by(id=id)
        if not query.first():
            nom = row.pop('nom')
            pwd = row.pop('pwd')
            atsk.add_user(session, id, nom, pwd)
            atsk.add_roles_to_user(session, id, 'admis')
            if id.startswith('dev'):
                atsk.add_roles_to_user(session, id, 'developper')
            matricule = row.get('matricule')
            if matricule:
                atsk.add_user(session, matricule, nom, pwd)
                atsk.add_roles_to_user(session, matricule, 'student')
            row['nom_complet'] = nom
            session.add(mdl.Admission(**row))
            session.commit()
            j += 1
        i += 1
    return jsonify({'message': f'{i} admission analysees, {j} admission crees'}), 200
    

@ui.route('/config/filieres', methods=['POST'])
@ui.roles_accepted('admin_preins')
def config_filieres():
    if not request.is_json:
        return jsonify({'error':'le contenu doit etre json'}), 400
    
    i = j = 0
    data = request.get_json()
    session = db.session
    for row in data:
        filiere = fmdl.Filiere(
            id  = row['code_filiere'],
            prefix= row['prefix'],
            code_udo = row['code_sco'],
            code_enset = row['code_filiere'],
            nom = row['nom'],
            departement_id = row['code_dept'],
            formation_id = row['code_formation']
        )
        session.merge(filiere)
        j += 1
        i += 1
    session.commit()
    return jsonify({'message': f'{i} filieres analysees, {j} filieres crees'}), 200


@ui.route('/config/classes', methods=['POST'])
@ui.roles_accepted('admin_preins')
def config_classes():
    if not request.is_json:
        return jsonify({'error':'le contenu doit etre json'}), 400
    
    i = j = 0
    data = request.get_json()
    session = db.session
    for row in data:
        classe = fmdl.Classe(
            id  = row['code_filiere'] + row['code_niveau'][-1],
            filiere_id = row['code_filiere'],
            niveau_id = row['code_niveau']
        )
        session.merge(classe)
        j += 1
        i += 1
    session.commit()
    return jsonify({'message': f'{i} classes analysees, {j} classes crees'}), 200

