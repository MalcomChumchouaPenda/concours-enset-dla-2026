
import os
import re
from datetime import datetime

import Levenshtein as lv
from flask import request, session
from flask import render_template, url_for, redirect, flash, send_file
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l
from flask_login import current_user, login_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField
from wtforms.validators import DataRequired

from core.config import login_manager, db
from core.utils import UiBlueprint, read_json, get_locale, default_deadline, read_markdown
from core.auth import tasks as auth_tsk
from services.concours_v0_0 import models as con_mdl
from services.concours_v0_0 import tasks as con_tsk


ui = UiBlueprint(__name__)
static_dir = os.path.join(os.path.dirname(__file__), 'static')


@ui.route('/')
def index():
    t0 = datetime.now()
    img = f'img/hero-bg.jpg'

    deadline = os.getenv('DATE_FIN_MAINTENANCE')
    t1 = datetime.strptime(deadline, r'%Y/%m/%d')
    print(t1, t0)
    if t0 < t1:
        return redirect(url_for('home.wait'))
    
    deadline = os.getenv('DATE_FIN_CONCOURS')
    t1 = datetime.strptime(deadline, r'%Y/%m/%d')
    if t0 > t1:
        return redirect(url_for('home.closed'))
    return render_template('home.jinja', img=img, deadline=deadline)


@ui.route('/help')
def help():
    locale = get_locale() 
    read = lambda n:read_markdown(os.path.join(static_dir, n))
    return render_template('home-help.jinja', 
                           help_intro=read(f'md/help-intro-{locale}.md'), 
                           help_new_inscr=read(f'md/help-new-{locale}.md'), 
                           help_edit_inscr=read(f'md/help-edit-{locale}.md'), 
                           help_print_inscr=read(f'md/help-print-{locale}.md'))


@ui.route('/communique')
def communique():
    nom_fichier_pdf = 'Concours-ENSET-Douala-2026_1er-et-2nd-cycle.pdf'
    chemin_pdf = os.path.join(static_dir, nom_fichier_pdf)
    return send_file(chemin_pdf, as_attachment=False, download_name=nom_fichier_pdf)


@ui.route('/wait')
def wait():
    deadline = os.getenv('DATE_FIN_MAINTENANCE')
    if datetime.now() >= datetime.strptime(deadline, r'%Y/%m/%d'):
        return redirect(url_for('home.index'))
    return render_template('landing/coming-soon.jinja',
                           deadline=deadline,
                           title=_('Concours 2026'),
                           alert_title=_('En maintenance'),
                           alert_msg=_('Cette plateforme est en maintenance. Elle sera disponible dans:'))

@ui.route('/closed')
def closed():
    deadline = os.getenv('DATE_FIN_CONCOURS')
    if datetime.now() < datetime.strptime(deadline, r'%Y/%m/%d'):
        return redirect(url_for('home.index'))
    img = f'img/hero-bg.jpg'
    return render_template('home-closed.jinja', img=img)



class RegisterForm(FlaskForm):
    bid = StringField(_l('code banque'), validators=[DataRequired()])
    rid = StringField(_l('numero recu'), validators=[DataRequired()])
    pwd = PasswordField(_l('mot de passe'), validators=[DataRequired()])
    confirm_pwd = PasswordField(_l('confirmer mot de passe'), validators=[DataRequired()])


def _check_id(bid, rid):
    if not re.match(os.getenv('CODE_BANQUE_EXP'), bid):
        return False
    return re.match(os.getenv('NUMERO_RECU_EXP'), rid)

def _clean_roles(user, inscr):
    if inscr is None:
        if user.has_role('inscrit_concours'):
            wrong_role = auth_tsk.get_role('inscrit_concours')
            auth_tsk.remove_role_from_user(user, wrong_role)
        if not user.has_role('candidat_concours'):
            good_role = auth_tsk.get_role('candidat_concours')
            auth_tsk.add_role_to_user(user, good_role)
    else:
        if user.has_role('candidat_concours'):
            wrong_role = auth_tsk.get_role('candidat_concours')
            auth_tsk.remove_role_from_user(user, wrong_role)
        if not user.has_role('inscrit_concours'):
            good_role = auth_tsk.get_role('inscrit_concours')
            auth_tsk.add_role_to_user(user, good_role)


@ui.route('/register', methods=['GET', 'POST'])
def register():
    inscr_query = con_mdl.InscriptionConcours.query
    if current_user.is_authenticated:
        inscr = inscr_query.filter_by(id=current_user.id).one_or_none()
        auth_tsk.get_user(current_user.id)
        _clean_roles(current_user, inscr)
        
        user = auth_tsk.get_user(current_user.id)
        login_user(user, remember=True)
        if user.has_role('inscrit_concours'):
            return redirect(url_for('inscriptions.view'))
        return redirect(url_for('inscriptions.new'))

    form = RegisterForm()
    if form.validate_on_submit():
        bid = form.bid.data
        rid = form.rid.data
        if not _check_id(bid, rid):
            flash(_('Recu de paiement invalide'), 'danger')
            return render_template('home-register.jinja', form=form)
        
        uid = f'{bid}{rid}'
        user = auth_tsk.get_user(uid)
        if user is not None:
            inscr = inscr_query.filter_by(id=uid).one_or_none()
            _clean_roles(user, inscr)

            if inscr is None:
                pwd = form.pwd.data
                if pwd != form.confirm_pwd.data:
                    flash(_('Mot de passe non confirme'), 'danger')
                    return render_template('home-register.jinja', form=form)
                
                user.set_password(pwd)
                auth_tsk.connect_user(uid, pwd)
                print('\n\treconnect user', current_user, current_user.is_authenticated)
                flash(_("Vous n'avez pas terminer votre inscription precedente"), 'warning')
                return redirect(url_for('inscriptions.new'))
            
            return render_template('landing/message.jinja',
                                    title=_("Avertissement"),
                                    message=_("Ce recu de paiement a deja ete utilise pour une inscription"),
                                    actions = [{'text':_("Voir l'inscription"), 'url':url_for('home.login')},
                                               {'text':_("Revenir a l'accueil"), 'url':url_for('home.logout')}])

        pwd = form.pwd.data
        if pwd != form.confirm_pwd.data:
            flash(_('Mot de passe non confirme'), 'danger')
            return render_template('home-register.jinja', form=form)
        
        role = auth_tsk.get_role('candidat_concours')
        user = auth_tsk.add_user(uid, f'Candidat {uid}', pwd, commit=False)
        auth_tsk.add_role_to_user(user, role, commit=True)
        auth_tsk.connect_user(uid, pwd)
        print('\n\tconnect user', current_user, current_user.is_authenticated)
        return redirect(url_for('inscriptions.new'))

    flash(_('Vous devez payer vos frais de concours avant cette etape'), 'warning')  
    return render_template('home-register.jinja', form=form)


class LoginForm(FlaskForm):
    bid = StringField(_l('code banque'), validators=[DataRequired()])
    rid = StringField(_l('numero recu'), validators=[DataRequired()])
    pwd = PasswordField(_l('mot de passe'), validators=[DataRequired()])


@ui.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    next = request.args.get('next')
    if not next:
        next = url_for('inscriptions.view')

    if 'inscriptions/new' in next:
        return redirect(url_for('home.register'))

    if form.validate_on_submit():
        bid = form.bid.data
        rid = form.rid.data
        if not _check_id(bid, rid):
            flash(_('Recu de paiement invalide'), 'danger')
            return render_template('home-login.jinja', form=form, next=next)
        
        uid = f'{bid}{rid}'
        user = auth_tsk.get_user(uid)
        if user is None:
            flash(_("Aucune inscription en cours"), 'danger')
            return render_template('home-login.jinja', form=form, next=next)
        
        inscr = con_mdl.InscriptionConcours.query.filter_by(id=uid).one_or_none()
        if inscr and inscr.numero_dossier is None:
            con_tsk.creer_numero(inscr)
        _clean_roles(user, inscr)

        pwd = form.pwd.data
        if not auth_tsk.connect_user(uid, pwd):
            flash(_('Mot de passe incorrecte'), 'danger')
            return render_template('home-login.jinja', form=form, next=next)
        
        if inscr is None and 'inscriptions/new' not in next:
            flash(_("Vous n'avez pas terminer votre inscription precedente"), 'warning')
            return redirect(url_for('inscriptions.new'))
        return redirect(next)
    return render_template('home-login.jinja', form=form, next=next)


@ui.route('/logout')
def logout():
    user = current_user
    if user.is_authenticated:
        if user.has_role('candidat_concours'):
            if user.has_role('inscrit_concours'):
                role = auth_tsk.get_role('candidat_concours')
                auth_tsk.remove_role_from_user(user, role)
            else:
                auth_tsk.remove_user(user)
        auth_tsk.disconnect_user()
    return redirect(url_for('home.index'))

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('home.login', next=request.path))


@ui.route('/denied')
def access_denied():
    print('\n\tdenied=>', request.url, current_user, current_user.roles)
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
    bid = StringField(_l('code banque'), validators=[DataRequired()])
    rid = StringField(_l('numero recu'), validators=[DataRequired()])
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
        bid = form.bid.data
        rid = form.rid.data
        if not _check_id(bid, rid):
            flash(_('Recu de paiement invalide'), 'danger')
            return render_template('home-recover-password.jinja', form=form, next=next)
        
        uid = f'{bid}{rid}'
        query = con_mdl.InscriptionConcours.query.filter_by(id=uid)
        inscription = query.one_or_none()
        if inscription is None:
            flash(_('Recu de paiement invalide'), 'danger')
            return render_template('home-recover-password.jinja', form=form, next=next)
        
        if not _verification_infos(inscription, data):
            flash(_('Informations incorrectes'), 'danger')
            return render_template('home-recover-password.jinja', form=form, next=next)
        user = auth_tsk.get_user(inscription.id)
        user.set_password('X')
        db.session.commit()
        auth_tsk.connect_user(user.id, 'X')
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
        flash(_("Mot de passe non confirmé"), 'danger')
    return render_template('home-change-password.jinja', form=form, next=next)
