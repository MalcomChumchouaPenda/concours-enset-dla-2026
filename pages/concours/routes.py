import os
import re

from flask import current_app, request
from flask import render_template, redirect, url_for, flash, send_file
from flask_login import current_user
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l

from core.config import db
from core.utils import UiBlueprint
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


def _check_id(id_):
    return re.match(r'^\d+$', id_)


@ui.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.AuthForm()
    if form.validate_on_submit():
        id_ = form.id.data
        if not _check_id(id_):
            flash('ce numero de paiement est invalide', 'danger')
            return render_template('concours-register.jinja', form=form)

        if get_user(db.session, id_):
            return render_template('landing/message.jinja',
                                title=_("Avertissement"),
                                message=_("Ce numero de paiement a deja ete utilise pour une inscription"),
                                actions = [{'text':_("Voir l'inscription"), 'url':url_for('concours.view_inscr')},
                                        {'text':_("Revenir a l'accueil"), 'url':url_for('home.logout')}])

        add_user(db.session, id_, id_, id_)
        add_roles_to_user(db.session, id_, 'candidat')
        connect_user(id_, id_)
        return redirect(url_for('concours.new_inscr'))
    flash('Vous devez payer les frais de concours avant de debuter', 'warning')
    return render_template('concours-register.jinja', form=form)

@ui.route('/new', methods=['GET', 'POST'])
def new_inscr():
    user_id = current_user.id
    inscription = cmdl.InscriptionConcours.query.filter_by(id=user_id).one_or_none()
    if inscription is not None:
        return render_template('landing/message.jinja',
                            title=_("Avertissement"),
                            message=_("Ce numero de paiement a deja ete utilise pour une inscription"),
                            actions = [{'text':_("Voir l'inscription"), 'url':url_for('concours.view_inscr')},
                                       {'text':_("Revenir a l'accueil"), 'url':url_for('home.logout')}])

    # create a edit form
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
    data = form.data
    print('\ndata=>\t', data)
    if form.validate_on_submit():
        data = form.data
        data['id'] = user_id
        data['classe_id'] = data['option_id'] + data['niveau_id'][-1]
        invalid_cols = ['csrf_token', 'nationalite_id', 
                        'region_origine_id', 'filiere_id', 
                        'option_id', 'niveau_id']
        for col in invalid_cols:
            data.pop(col)

        cursus = data.pop('cursus')
        inscription = cmdl.InscriptionConcours(**data)
        ctsk.creer_numero(db.session, inscription)
        db.session.add(inscription)     
        for row in cursus:  
            row['inscription_id'] = user_id
            etape = cmdl.EtapeCursus(**row)
            db.session.add(etape)
        db.session.commit()
        return redirect(url_for('concours.view_inscr'))

    print('\nerrors=>\t', form.errors)
    return render_template('concours-new-inscr.jinja', form=form)


@ui.route('/view')
@ui.login_required
def view_inscr():
    user_id = current_user.id
    inscription = cmdl.InscriptionConcours.query.filter_by(id=user_id).one_or_none()
    if inscription is None:
        return redirect(url_for('concours.new_inscr'))
    return render_template('concours-view-inscr.jinja', inscription=inscription)



# @ui.route('/procedure')
# def procedure():
#     return render_template('concours-procedure.jinja')


@ui.route('/print')
def print_inscr():
    user_id = current_user.id
    inscription = cmdl.InscriptionConcours.query.filter_by(id=user_id).one_or_none()
    if inscription is None:
        return redirect(url_for('concours.new_inscr'))
    nom_fichier_pdf = f"fiche_inscription_{user_id.lower()}.pdf"
    nom_fichier_pdf = nom_fichier_pdf.replace('-', '_')
    chemin_pdf_final = os.path.join(temp_dir, nom_fichier_pdf)
    fichier_pdf = ctsk.generer_fiche_inscription(inscription, chemin_pdf_final)
    return send_file(fichier_pdf, as_attachment=True, download_name=nom_fichier_pdf)


@ui.route('/edit', methods=['GET', 'POST'])
@ui.login_required
def edit_inscr():
    user_id = current_user.id
    inscription = cmdl.InscriptionConcours.query.filter_by(id=user_id).one_or_none()
    # create a edit form
    form = forms.EditInscrForm(obj=inscription)
    form.nationalite_id.choices = forms.list_nationalites()
    form.region_origine_id.choices = forms.list_regions()
    form.departement_origine_id.choices = forms.list_departements()

    # traitement et enregistrement des donnees
    data = form.data
    print('\ndata=>\t', data)
    if form.validate_on_submit():
        data = form.data

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
        return redirect(url_for('concours.view_inscr'))

    print('\nerrors=>\t', form.errors)
    form.filiere.data = inscription.classe.option.filiere.nom_fr
    form.option.data = inscription.classe.option.nom_fr
    form.niveau.data = inscription.classe.niveau
    form.centre.data = inscription.centre.nom
    form.diplome.data = inscription.diplome.nom_fr
    form.nationalite_id.data = inscription.departement_origine.region.pays_id
    form.region_origine_id.data = inscription.departement_origine.region_id
    form.departement_origine_id.data = inscription.departement_origine_id
    return render_template('concours-edit-inscr.jinja', form=form)
