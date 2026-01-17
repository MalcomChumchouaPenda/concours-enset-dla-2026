
import os
import re

import Levenshtein as lv
from flask import render_template, request, url_for, redirect, flash, send_file
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField
from wtforms.validators import DataRequired

from core.config import login_manager, db
from core.utils import UiBlueprint, read_json, get_locale, default_deadline, read_markdown
from core.auth.tasks import connect_user, disconnect_user, get_user, add_roles_to_user, add_user
from services.concours_v0_0 import models as cmdl


ui = UiBlueprint(__name__)
static_dir = os.path.join(os.path.dirname(__file__), 'static')


@ui.route('/')
def index():
    locale = get_locale() 
    print('\n\tlocale', locale)
    msg = os.path.join(static_dir, f'md/hero-msg-{locale}.md')
    img = f'img/hero-bg.jpg'
    hero = dict(msg=msg, img=img)
    disconnect_user()
    return render_template('home.jinja', hero=hero)


@ui.route('/help')
def help():
    f = lambda n:read_markdown(os.path.join(static_dir, n))
    return render_template('home-help.jinja', 
                           help_intro=f('md/help-intro.md'), 
                           help_new_inscr=f('md/help-new-inscr.md'), 
                           help_edit_inscr=f('md/help-edit-inscr.md'), 
                           help_print_inscr=f('md/help-print-inscr.md'))


@ui.route('/communique')
def communique():
    nom_fichier_pdf = 'Concours-ENSET-Douala-2026_1er-et-2nd-cycle.pdf'
    chemin_pdf = os.path.join(static_dir, nom_fichier_pdf)
    return send_file(chemin_pdf, as_attachment=False, download_name=nom_fichier_pdf)


@ui.route('/wait')
def wait():
    return render_template('landing/coming-soon.jinja',
                           deadline='2026/1/16',
                           title='Concours 2026',
                           alert_title='En maintenance',
                           alert_msg='Cette plateforme est en maintenance. Elle sera disponible dans:')


class RegisterForm(FlaskForm):
    id = StringField(_l('numero de paiement'), validators=[DataRequired()])
    pwd = PasswordField(_l('mot de passe'), validators=[DataRequired()])
    confirm_pwd = PasswordField(_l('confirmer mot de passe'), validators=[DataRequired()])


def _check_id(id_):
    return re.match(r'^\d+$', id_)


@ui.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        uid = form.id.data
        if not _check_id(uid):
            flash('Numero de paiement invalide', 'danger')
            return render_template('home-register.jinja', form=form)
        
        next = url_for('inscriptions.new')
        if get_user(db.session, uid):
            return render_template('landing/message.jinja',
                                    title=_("Avertissement"),
                                    message=_("Ce numero de paiement a deja ete utilise pour une inscription"),
                                    actions = [{'text':_("Voir l'inscription"), 'url':url_for('inscriptions.view')},
                                               {'text':_("Revenir a l'accueil"), 'url':url_for('home.logout')}])

        pwd = form.pwd.data
        if pwd != form.confirm_pwd.data:
            flash('Mot de passe non confirme', 'danger')
            return render_template('home-register.jinja', form=form)
        
        add_user(db.session, uid, uid, pwd)
        add_roles_to_user(db.session, uid, 'candidat')
        connect_user(uid, pwd)
        return redirect(next)

    flash('Vous devez payer vos frais de concours avant cette etape', 'warning')  
    return render_template('home-register.jinja', form=form)


class LoginForm(FlaskForm):
    id = StringField(_l('numero de paiement'), validators=[DataRequired()])
    pwd = PasswordField(_l('mot de passe'), validators=[DataRequired()])


@ui.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    next = request.args.get('next')
    if not next:
        next = url_for('inscriptions.view')

    if form.validate_on_submit():
        uid = form.id.data
        if not _check_id(uid):
            flash('Numero de paiement invalide', 'danger')
            return render_template('home-login.jinja', form=form, next=next)
        
        if not get_user(db.session, uid):
            flash("Aucune inscription en cours", 'danger')
            return render_template('home-login.jinja', form=form, next=next)

        pwd = form.pwd.data
        if not connect_user(uid, pwd):
            flash('Mot de passe incorrecte', 'danger')
            return render_template('home-login.jinja', form=form, next=next)
        
        return redirect(next)
    return render_template('home-login.jinja', form=form, next=next)


@ui.route('/logout')
def logout():
    if current_user.is_authenticated:
        disconnect_user()
    return redirect(url_for('home.index'))

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('home.login', next=request.path))


@ui.route('/denied')
def access_denied():
    msg = _("Vous n'avez pas les autorisations nécessaires pour accéder à cette page.")
    actions = [{'text':_("Revenir a l'accueil"), 'url':'/'}]
    prev = request.referrer
    if prev is not None:
        actions.append({'text':_("Revenir a la page precedente"), 'url':prev})
    return render_template('landing/error.jinja', number=403, actions=actions, message=msg), 403

@ui.route('/profile')
def profile():
    return render_template('home-dashboard-profile.jinja')


class RecoverPasswordForm(FlaskForm):
    id = StringField(_l('numero de paiement'), validators=[DataRequired()])
    nom_complet = StringField(_l('Noms et prenoms'), validators=[DataRequired()])
    date_naissance = StringField(_l('Date de naissance'), validators=[DataRequired()])
    lieu_naissance = StringField(_l('Lieu de naissance'), validators=[DataRequired()])


def _verification_infos(inscription, data):
    ratio1 = lv.ratio(data['nom_complet'].upper(), inscription.nom_complet.upper())
    ratio2 = lv.ratio(data['date_naissance'], inscription.date_naissance.strftime(r'%d/%m/%Y'))
    ratio3 = lv.ratio(data['lieu_naissance'].upper(), inscription.lieu_naissance.upper())
    ratio_moy = sum([ratio1, ratio2, ratio3]) / 3
    return ratio_moy >= 0.85

@ui.route('/recover-password', methods=['GET', 'POST'])
def recover_password():
    next = request.args.get('next')
    if not next:
        next = url_for('inscriptions.view')

    form = RecoverPasswordForm()
    if form.validate_on_submit():
        data = form.data
        query = cmdl.InscriptionConcours.query.filter_by(id=data['id'])
        inscription = query.one_or_none()
        if inscription is None:
            flash('Numero de paiement inconnu', 'danger')
            return render_template('home-recover-password.jinja', form=form, next=next)
        
        if not _verification_infos(inscription, data):
            flash('Informations incorrectes', 'danger')
            return render_template('home-recover-password.jinja', form=form, next=next)
        user = get_user(db.session, inscription.id)
        user.set_password('X')
        db.session.commit()
        connect_user(user.id, 'X')
        return redirect(url_for('home.change_password', next=next))
    return render_template('home-recover-password.jinja', form=form, next=next)


class ChangePasswordForm(FlaskForm):
    new_pwd = PasswordField(_l('Nouveau mot de passe'), validators=[DataRequired()])
    confirm_pwd = PasswordField(_l('Confirmer mot de passe'), validators=[DataRequired()])

@ui.route('/change-password', methods=['GET', 'POST'])
def change_password():
    next = request.args.get('next')
    if not next:
        next = url_for('home.profile')

    form = ChangePasswordForm()
    if form.validate_on_submit():
        new_pwd = form.new_pwd.data
        if new_pwd == form.confirm_pwd.data:
            current_user.set_password(new_pwd)
            db.session.commit()
            return redirect(next)
        flash("Mot de passe non confirmé", 'danger')
    return render_template('home-change-password.jinja', form=form, next=next)


@ui.route('/dashboard')
@ui.login_required
def dashboard():
    welcome = _("Bienvenue dans cette espace")
    return render_template('home-dashboard.jinja', welcome=welcome)

@ui.route('/student')
@ui.roles_accepted('student')
def student_dashboard():
    return redirect(url_for('home.dashboard'))

@ui.route('/teacher')
@ui.roles_accepted('teacher')
def teacher_dashboard():
    return redirect(url_for('home.dashboard'))

@ui.route('/admin')
@ui.roles_accepted('admin')
def admin_dashboard():
    return redirect(url_for('home.dashboard'))
