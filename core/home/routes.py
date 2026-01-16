
import os
import re
from flask import render_template, request, url_for, redirect, flash
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField
from wtforms.validators import DataRequired

from core.config import login_manager, db
from core.utils import UiBlueprint, read_json, get_locale, default_deadline
from core.auth.tasks import connect_user, disconnect_user, get_user, add_roles_to_user, add_user


ui = UiBlueprint(__name__)
static_dir = os.path.join(os.path.dirname(__file__), 'static')


@ui.route('/')
def index():
    locale = get_locale() 
    print('\n\tlocale', locale)
    msg = os.path.join(static_dir, f'md/hero-msg-{locale}.md')
    img = f'img/hero-bg.jpg'
    hero = dict(msg=msg, img=img)
    return render_template('home.jinja', hero=hero)


@ui.route('/wait')
def wait():
    return render_template('landing/coming-soon.jinja',
                           deadline='2026/1/16',
                           title='Concours 2026',
                           alert_title='En maintenance',
                           alert_msg='Cette plateforme est en maintenance. Elle sera disponible dans:')
    # locale = get_locale() 
    # print('\n\tlocale', locale)
    # msg = os.path.join(static_dir, f'md/hero-msg-{locale}.md')
    # img = f'img/hero-bg.jpg'
    # hero = dict(msg=msg, img=img)
    # return render_template('home.jinja', hero=hero)


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
        
        next = url_for('concours.new_inscr')
        if get_user(db.session, uid):
            return render_template('landing/message.jinja',
                                    title=_("Avertissement"),
                                    message=_("Ce numero de paiement a deja ete utilise pour une inscription"),
                                    actions = [{'text':_("Voir l'inscription"), 'url':url_for('concours.view_inscr')},
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
        next = url_for('concours.view_inscr')

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


class ChangePasswordForm(FlaskForm):
    new_pwd = PasswordField(_l('Nouveau mot de passe'), validators=[DataRequired()])
    confirm_pwd = PasswordField(_l('Confirmer mot de passe'), validators=[DataRequired()])

@ui.route('/change-password', methods=['GET', 'POST'])
def change_password():
    error = None
    form = ChangePasswordForm()
    if form.validate_on_submit():
        new_pwd = form.new_pwd.data
        if new_pwd == form.confirm_pwd.data:
            current_user.set_password(new_pwd)
            db.session.commit()
            return redirect(url_for('home.profile'))
        error = "Mot de passe non confirmé"
        form = ChangePasswordForm()
    return render_template('home-change-password.jinja', form=form, error=error)


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
