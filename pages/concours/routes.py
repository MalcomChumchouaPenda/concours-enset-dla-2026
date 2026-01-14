import os
from flask import current_app, render_template, redirect, url_for, flash
from core.utils import UiBlueprint
from services.regions_v0_0 import tasks as rtsk
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
            logger.warnin

@ui.route('/procedure')
def procedure():
    return render_template('concours-procedure.jinja')

@ui.route('/identity', methods=['GET', 'POST'])
def identity():
    # create a edit form
    form = forms.IdentityForm()
    form.nationalite_id.choices = forms.choices(rtsk.list_nationalites(full_id=True))
    form.region_origine_id.choices = forms.choices(rtsk.list_regions(full_id=True))
    form.departement_origine_id.choices = forms.choices(rtsk.list_departements(full_id=True))

    # traitement et enregistrement des donnees
    if form.validate_on_submit():
        data = form.data
        return redirect(url_for('concours.options'))

    # fixation des valeurs par defaut
    # alert = """
    #     Compléter les champs obligatoires. 
    #     vous pouvez interrompre la procédure en vous deconnectant
    #     et la reprendre ultérieurement.
    #     """
    # flash(alert, 'warning')
    return render_template('concours-identity.jinja', form=form)


@ui.route('/options', methods=['GET', 'POST'])
def options():
    # create a edit form
    form = forms.OptionsForm()

    # traitement et enregistrement des donnees
    if form.validate_on_submit():
        data = form.data
        return redirect(url_for('concours.contacts'))

    # fixation des valeurs par defaut
    return render_template('concours-options.jinja', form=form)


@ui.route('/contacts', methods=['GET', 'POST'])
def contacts():
    # create a edit form
    form = forms.ContactsForm()

    # traitement et enregistrement des donnees
    if form.validate_on_submit():
        data = form.data
        return redirect(url_for('concours.summary'))

    # fixation des valeurs par defaut
    return render_template('concours-contacts.jinja', form=form)


@ui.route('/summary')
def summary():
    return 'final step'
    # user_id = current_user.id
    # inscription = tsk.rechercher_inscription(user_id)
    # if inscription is None:
    #     return redirect(url_for('preins.new_info'))
    # return render_template('preins-view-info.jinja', inscription=inscription)