import os
import re
from datetime import datetime

import Levenshtein as lv
from flask import current_app, request, session
from flask import render_template, redirect, url_for, flash, send_file
from flask_login import current_user
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l

from core.config import db
from core.utils import UiBlueprint, get_locale
from core.auth import tasks as auth_tsk
from services.concours_v0_0 import tasks as con_tsk
from services.concours_v0_0 import models as con_mdl
from . import forms
from . import choices


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
            logger.warning

def _upper_data_values(data):
    keys = list(data.keys())
    for key in keys:
        if key.endswith('_id'):
            continue
        value = data[key]
        if isinstance(value, str):
            data[key] = value.upper()
    return data


@ui.route('/new', methods=['GET', 'POST'])
@ui.roles_accepted('candidat_concours', 'inscrit_concours')
def new():    
    if current_user.has_role('inscrit_concours'):
        auth_tsk.disconnect_user()
        return redirect(url_for('home.register'))
    
    # creation du formulaire
    locale = get_locale()
    form = forms.NewInscrForm()
    form.sexe_id.choices = choices.sexes(locale)
    form.langue_id.choices = choices.langues(locale)
    form.statut_matrimonial_id.choices = choices.situations(locale)
    form.nationalite_id.choices = choices.nationalites(locale)
    form.region_origine_id.choices = choices.regions(locale)
    form.departement_origine_id.choices = choices.departements(locale)
    form.niveau_id.choices = choices.niveaux(locale)
    form.filiere_id.choices = choices.filieres(locale)
    form.option_id.choices = choices.options(locale)
    form.centre_id.choices = choices.centres()
    form.diplome_id.choices = choices.diplomes(locale)

    # traitement et enregistrement des donnees
    if form.validate_on_submit():
        data = form.data
        user = current_user

        # pretraitement des donnees
        uid = user.id
        classe_id = data['option_id'] + data['niveau_id'][-1]
        date_naiss = datetime.strptime(data['date_naissance'], r'%d/%m/%Y')
        date_naiss = date_naiss.date()
        data['id'] = uid
        data['classe_id'] = classe_id
        data['date_naissance'] = date_naiss
        data = _upper_data_values(data)

        # retrait des donnees inutiles
        invalid_cols = ['csrf_token', 'nationalite_id', 
                        'region_origine_id', 'filiere_id', 
                        'option_id', 'niveau_id']
        for col in invalid_cols:
            data.pop(col)

        # traitement du cursus
        cursus = data.pop('cursus') 
        for row in cursus:  
            row['inscription_id'] = uid
            row = _upper_data_values(row)
            etape = con_mdl.EtapeCursus(**row)
            db.session.add(etape)

        # creation de l'inscription
        inscr = con_mdl.InscriptionConcours(**data)
        db.session.add(inscr)    
        user.last_name = inscr.nom
        user.first_name = inscr.prenom
        old_role = auth_tsk.get_role('candidat_concours')
        new_role = auth_tsk.get_role('inscrit_concours')
        auth_tsk.remove_role_from_user(user, old_role, commit=False)
        auth_tsk.add_role_to_user(user, new_role, commit=False)
        con_tsk.creer_numero(inscr)

        # finalisation
        db.session.commit()
        flash(_('Inscription enregistree avec success'), 'success')
        return redirect(url_for('inscriptions.view'))

    print('\nerrors=>\t', form.errors)
    return render_template('inscriptions/new.jinja', form=form)


@ui.route('/view')
@ui.roles_accepted('inscrit_concours')
def view():
    user_id = current_user.id
    inscr = con_mdl.InscriptionConcours.query.filter_by(id=user_id).one_or_none()
    if inscr is None:
        return redirect(url_for('inscriptions.new'))
    return render_template('inscriptions/view.jinja', inscription=inscr)



# @ui.route('/procedure')
# def procedure():
#     return render_template('concours-procedure.jinja')


@ui.route('/print')
@ui.roles_accepted('inscrit_concours')
def print_():
    user_id = current_user.id
    inscr = con_mdl.InscriptionConcours.query.filter_by(id=user_id).one_or_none()
    if inscr is None:
        return redirect(url_for('inscriptions.new'))
    nom_fichier_pdf = f"fiche_inscription_{user_id.lower()}.pdf"
    nom_fichier_pdf = nom_fichier_pdf.replace('-', '_')
    chemin_pdf_final = os.path.join(temp_dir, nom_fichier_pdf)
    fichier_pdf = con_tsk.generer_fiche_inscription(inscr, chemin_pdf_final)
    return send_file(fichier_pdf, as_attachment=False, download_name=nom_fichier_pdf)


def _verification_noms(inscr, data):
    nom_complet = ' '.join([data['nom'], data['prenom']])
    ratio = lv.ratio(nom_complet.upper(), inscr.nom_complet.upper())
    print('\n\ttest =>', nom_complet.upper(), inscr.nom_complet.upper(), ratio)
    return ratio >= 0.75


@ui.route('/edit', methods=['GET', 'POST'])
@ui.roles_accepted('inscrit_concours')
def edit():
    user_id = current_user.id
    inscr = con_mdl.InscriptionConcours.query.filter_by(id=user_id).one_or_none()
    if request.method == 'POST':
        form = forms.EditInscrForm()
    else:
        form = forms.EditInscrForm(obj=inscr)
        form.date_naissance.data = inscr.date_naissance.strftime(r'%d/%m/%Y')
        form.nationalite_id.data = inscr.departement_origine.region.pays_id
        form.region_origine_id.data = inscr.departement_origine.region_id
        form.departement_origine_id.data = inscr.departement_origine_id

    locale = get_locale()
    form.filiere.data = inscr.classe.option.filiere.nom(locale).upper()
    form.option.data = inscr.classe.option.nom(locale).upper()
    form.diplome.data = inscr.diplome.nom(locale).upper()
    form.niveau.data = inscr.classe.niveau(locale).upper()
    form.centre.data = inscr.centre.nom.upper()    
    form.sexe_id.choices = choices.sexes(locale)
    form.langue_id.choices = choices.langues(locale)
    form.statut_matrimonial_id.choices = choices.situations(locale)
    form.nationalite_id.choices = choices.nationalites(locale)
    form.region_origine_id.choices = choices.regions(locale)
    form.departement_origine_id.choices = choices.departements(locale)

    # traitement et enregistrement des donnees
    if form.validate_on_submit():
        data = form.data

        # verification du noms
        if not _verification_noms(inscr, data):
            msg = _("Ce compte est reserve au candidat ")
            msg += f"<b>{inscr.nom_complet}</b> "
            msg += _("(Vous n'etes pas dans votre inscription)")
            flash(msg, 'danger')
            return redirect(url_for('inscriptions.view'))

        # pretraitement des donnees
        date_naiss = datetime.strptime(data['date_naissance'], r'%d/%m/%Y')
        date_naiss = date_naiss.date()
        inscr.date_naissance = date_naiss
        data = _upper_data_values(data)

        # modification simple
        simple_fields = ['prenom', 'nom', 'lieu_naissance', 
                         'sexe_id', 'statut_matrimonial_id',
                         'departement_origine_id', 'langue_id', 
                         'telephone', 'email']
        for field in simple_fields:
            setattr(inscr, field, data[field])

        # clear previous cursus
        cursus = data.pop('cursus')
        for etape in inscr.cursus:
            db.session.delete(etape)

        # add new cursus
        for row in cursus:
            row['inscription_id'] = user_id
            row = _upper_data_values(row)
            etape = con_mdl.EtapeCursus(**row)
            db.session.add(etape)

        db.session.commit()
        session['step'] = 'edited'
        flash(_('Inscription modifiee avec success'), 'success')
        return redirect(url_for('inscriptions.view'))

    print('\nerrors=>\t', form.errors)
    return render_template('inscriptions/edit.jinja', form=form)
