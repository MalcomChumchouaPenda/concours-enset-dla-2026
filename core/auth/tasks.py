
from flask import current_app
from flask_login import login_user, logout_user
from flask_principal import Identity, AnonymousIdentity, identity_changed
from core.config import db, login_manager
from .models import User, Role


def connect_user(userid, pwd):
    session = db.session
    user = session.query(User).filter_by(id=userid).first()
    if user and user.check_password(pwd):
        login_user(user)
        identity_changed.send(
            current_app._get_current_object(), 
            identity=Identity(user.id)
        )
        return True
    return False

def disconnect_user():
    logout_user()
    identity_changed.send(
        current_app._get_current_object(), 
        identity=AnonymousIdentity()
    )
    return True


def get_user(uid):
    return User.query.filter_by(id=uid).one_or_none()

def add_user(uid, last_name, password, first_name=None, commit=True):
    user = User(id=uid, last_name=last_name, first_name=first_name)
    user.set_password(password)
    db.session.add(user)
    if commit:
        db.session.commit()
    return user

def remove_user(user, commit=True):
    db.session.delete(user)
    if commit:
        db.session.commit()


def get_role(uid):
    return Role.query.filter_by(id=uid).one_or_none()

def add_role(uid, name, commit=True):
    role = Role(id=uid, name=name)
    db.session.add(role)
    if commit:
        db.session.commit()
    return role

def remove_role(role, commit=True):
    db.session.delete(role)
    if commit:
        db.session.commit()


def add_role_to_user(user, role, commit=True):
    if role not in user.roles:
        user.roles.append(role)
    if commit:
        db.session.commit()

def remove_role_from_user(user, role, commit=True):
    if role and role in user.roles:
        user.roles.remove(role)
    if commit:
        db.session.commit()

def add_roles_to_user(user, roles, commit=True):
    for role in roles:
        if role not in user.roles:
            user.roles.append(role)
    if commit:
        db.session.commit()

def remove_roles_from_user(user, roles, commit=True):
    for role in roles:
        if role and role in user.roles:
            user.roles.remove(role)
    if commit:
        db.session.commit()


def refresh_current_user(id):
    disconnect_user()
    user = get_user(id)
    connect_user(user.id, user.password)
    print('\nrefresh user', user, type(user), user.roles)
