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
from core.utils import UiBlueprint, read_markdown
from core.auth import models as amdl
from core.auth.tasks import get_user, add_user, add_roles_to_user, connect_user
from services.regions_v0_0 import tasks as rtsk
from services.formations_v0_1 import tasks as ftsk
from services.concours_v0_0 import tasks as ctsk
from services.concours_v0_0 import models as cmdl
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
            logger.warning


@ui.route('/new', methods=['GET', 'POST'])
def new():
    # verification des etapes
    current_step = session.get('step', 'undefined')
    if current_step in ['undefined', 'submitted']:
        session['step'] = 'reset'
        for key in ['candidat_id', 'candidat_pwd']:
            if key in session:
                session.pop(key)
        return redirect(url_for('home.register'))
    
    # creation du formulaire
    form = forms.NewInscrForm()
    form.nationalite_id.choices = forms.list_nationalites()
    form.region_origine_id.choices = forms.list_regions()
    form.departement_origine_id.choices = forms.list_departements()
    form.niveau_id.choices = forms.list_niveaux()
    form.filiere_id.choices = forms.list_filieres()
    form.option_id.choices = forms.list_options()
    form.centre_id.choices = forms.list_centres()
    form.diplome_id.choices = forms.list_diplomes()

    # traitement et enregistrement des donnees
    if form.validate_on_submit():
        data = form.data

        # pretraitement des donnees
        uid = session['candidat_id']
        classe_id = data['option_id'] + data['niveau_id'][-1]
        date_naiss = datetime.strptime(data['date_naissance'], r'%d/%m/%Y')
        date_naiss = date_naiss.date()
        data['id'] = uid
        data['classe_id'] = classe_id
        data['date_naissance'] = date_naiss

        # retrait des donnees inutiles
        invalid_cols = ['csrf_token', 'nationalite_id', 
                        'region_origine_id', 'filiere_id', 
                        'option_id', 'niveau_id']
        for col in invalid_cols:
            data.pop(col)

        # traitement du cursus
        cursus = data.pop('cursus')
        inscription = cmdl.InscriptionConcours(**data)
        ctsk.creer_numero(db.session, inscription)
        db.session.add(inscription)     
        for row in cursus:  
            row['inscription_id'] = uid
            etape = cmdl.EtapeCursus(**row)
            db.session.add(etape)

        # creation du compte utilisateur
        uid = session.pop('candidat_id')
        pwd = session.pop('candidat_pwd')
        role = amdl.Role.query.get('candidat')
        user = amdl.User(id=uid, last_name=uid)
        user.set_password(pwd)
        user.roles.append(role)
        db.session.add(user)
        
        # finalisation
        db.session.commit()
        connect_user(uid, pwd)
        session['step'] = 'submitted'
        flash('Inscription enregistree avec success', 'success')
        return redirect(url_for('inscriptions.view'))

    print('\nerrors=>\t', form.errors)
    return render_template('inscriptions/new.jinja', form=form)


@ui.route('/view')
@ui.login_required
def view():
    user_id = current_user.id
    inscription = cmdl.InscriptionConcours.query.filter_by(id=user_id).one_or_none()
    if inscription is None:
        return redirect(url_for('inscriptions.new'))
    return render_template('inscriptions/view.jinja', inscription=inscription)



# @ui.route('/procedure')
# def procedure():
#     return render_template('concours-procedure.jinja')


@ui.route('/print')
def print_():
    user_id = current_user.id
    inscription = cmdl.InscriptionConcours.query.filter_by(id=user_id).one_or_none()
    if inscription is None:
        return redirect(url_for('inscriptions.new'))
    nom_fichier_pdf = f"fiche_inscription_{user_id.lower()}.pdf"
    nom_fichier_pdf = nom_fichier_pdf.replace('-', '_')
    chemin_pdf_final = os.path.join(temp_dir, nom_fichier_pdf)
    fichier_pdf = ctsk.generer_fiche_inscription(inscription, chemin_pdf_final)
    return send_file(fichier_pdf, as_attachment=False, download_name=nom_fichier_pdf)


def _verification_noms(inscription, data):
    nom_complet = ' '.join([data['nom'], data['prenom']])
    ratio = lv.ratio(nom_complet.upper(), inscription.nom_complet.upper())
    print('\n\ttest =>', nom_complet.upper(), inscription.nom_complet.upper(), ratio)
    return ratio >= 0.75

@ui.route('/edit', methods=['GET', 'POST'])
@ui.login_required
def edit():
    user_id = current_user.id
    inscription = cmdl.InscriptionConcours.query.filter_by(id=user_id).one_or_none()
    if request.method == 'POST':
        form = forms.EditInscrForm()
    else:
        form = forms.EditInscrForm(obj=inscription)
        form.date_naissance.data = inscription.date_naissance.strftime(r'%d/%m/%Y')
        form.nationalite_id.data = inscription.departement_origine.region.pays_id
        form.region_origine_id.data = inscription.departement_origine.region_id
        form.departement_origine_id.data = inscription.departement_origine_id

    form.filiere.data = inscription.classe.option.filiere.nom_fr
    form.option.data = inscription.classe.option.nom_fr
    form.niveau.data = inscription.classe.niveau
    form.centre.data = inscription.centre.nom
    form.diplome.data = inscription.diplome.nom_fr
    form.nationalite_id.choices = forms.list_nationalites()
    form.region_origine_id.choices = forms.list_regions()
    form.departement_origine_id.choices = forms.list_departements()

    # traitement et enregistrement des donnees
    if form.validate_on_submit():
        data = form.data

        # verification du noms
        if not _verification_noms(inscription, data):
            msg = "Ce compte est reserve au candidat "
            msg += f"<b>{inscription.nom_complet}</b> "
            msg += "(Vous n'etes pas dans votre inscription)"
            flash(msg, 'danger')
            return redirect(url_for('inscriptions.view'))

        # pretraitement des donnees
        date_naiss = datetime.strptime(data['date_naissance'], r'%d/%m/%Y')
        date_naiss = date_naiss.date()
        inscription.date_naissance = date_naiss

        # modification simple
        simple_fields = ['prenom', 'nom', 'lieu_naissance', 
                         'sexe_id', 'situation_matrimoniale_id',
                         'departement_origine_id', 'langue_id', 
                         'telephone', 'email']
        for field in simple_fields:
            setattr(inscription, field, data[field])

        # clear previous cursus
        cursus = data.pop('cursus')
        for etape in inscription.cursus:
            db.session.delete(etape)

        # add new cursus
        for row in cursus:
            row['inscription_id'] = user_id
            etape = cmdl.EtapeCursus(**row)
            db.session.add(etape)

        db.session.commit()
        flash('Inscription modifiee avec success', 'success')
        return redirect(url_for('inscriptions.view'))

    print('\nerrors=>\t', form.errors)
    return render_template('inscriptions/edit.jinja', form=form)
