import os
from flask import current_app, render_template, redirect, url_for, flash, send_file
from flask_login import current_user
from core.config import db
from core.utils import UiBlueprint
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
@ui.login_required
def new_inscr():
    user_id = current_user.id

    # create a edit form
    form = forms.NewInscrForm()
    form.nationalite_id.choices = forms.list_nationalites()
    form.region_origine_id.choices = forms.list_regions()
    form.departement_origine_id.choices = forms.list_departements()
    form.filiere_id.choices = forms.list_filieres()
    form.option_id.choices = forms.list_options()
    form.classe_id.choices = forms.list_classes()
    form.centre_id.choices = forms.list_centres()

    # traitement et enregistrement des donnees
    if form.validate_on_submit():
        data = form.data
        data['id'] = user_id
        invalid_cols = ['csrf_token', 'nationalite_id', 
                        'region_origine_id', 'filiere_id', 
                        'option_id']
        for col in invalid_cols:
            data.pop(col)

        candidat = cmdl.Candidat(**data)
        db.session.add(candidat)
        db.session.commit()
        return redirect(url_for('concours.view_inscr'))

    return render_template('concours-new-inscr.jinja', form=form)


@ui.route('/view')
@ui.login_required
def view_inscr():
    user_id = current_user.id
    inscription = cmdl.Candidat.query.filter_by(id=user_id).one_or_none()
    if inscription is None:
        return redirect(url_for('concours.new_inscr'))
    return render_template('concours-view-inscr.jinja', inscription=inscription)



# @ui.route('/procedure')
# def procedure():
#     return render_template('concours-procedure.jinja')


@ui.route('/print')
def print_inscr():
    user_id = current_user.id
    inscription = cmdl.Candidat.query.filter_by(id=user_id).one_or_none()
    if inscription is None:
        return redirect(url_for('concours.new_inscr'))
    nom_fichier_pdf = f"fiche_inscription_{user_id.lower()}.pdf"
    nom_fichier_pdf = nom_fichier_pdf.replace('-', '_')
    chemin_pdf_final = os.path.join(temp_dir, nom_fichier_pdf)
    fichier_pdf = ctsk.generer_fiche_inscription(inscription, chemin_pdf_final)
    return send_file(fichier_pdf, as_attachment=True, download_name=nom_fichier_pdf)
