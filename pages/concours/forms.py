from datetime import datetime
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, EmailField, TextAreaField, DateField
from wtforms.validators import DataRequired, ValidationError
from services.concours_v0_0 import models as cmdl


def choices(data, only_keys=False):
    if only_keys:
        if isinstance(data, dict):
            items = sorted([(k, k) for k in data.keys()])
        else:
            items = sorted([(k, k) for k, _ in data])
    else:
        if isinstance(data, dict):
            items = sorted([(k,v.upper()) for k,v in data.items()])
        else:
            items = sorted([(k,v.upper()) for k,v in data])
    items.insert(0, ('', 'Choisir...'))
    return items

def validators1():
    return [DataRequired()]


def list_filieres():
    query = cmdl.FiliereConcours.query
    items = [('', 'Choisir')]
    items.extend([(obj.full_id, obj.nom_fr) for obj in query.all()])
    return items

def list_options():
    query = cmdl.OptionConcours.query
    items = [('', 'Choisir')]
    items.extend([(obj.full_id, obj.nom_fr) for obj in query.all()])
    return items

def list_classes():
    query = cmdl.ClasseConcours.query
    items = [('', 'Choisir')]
    items.extend([(obj.full_id, cmdl.NIVEAUX[obj.niveau_id]) 
                  for obj in query.all()])
    return items

def list_centres():
    query = cmdl.CentreConcours.query
    items = [('', 'Choisir')]
    items.extend([(obj.id, obj.nom) for obj in query.all()])
    return items


class CandidatForm(FlaskForm):
    
    # Informations personnelles de base
    prenom = StringField(_l('Prenoms'))
    nom = StringField(_l('Noms'), validators=validators1())
    date_naissance = DateField(_l('Date de naissance'), validators=validators1())
    lieu_naissance = StringField(_l('Lieu de naissance'), validators=validators1())
    sexe_id = SelectField(_l('Sexe'), validators=validators1(), choices=choices(cmdl.SEXES))
    situation_matrimoniale_id = SelectField(_l('Situation Matrimoniale'), 
                                            validators=validators1(), 
                                            choices=choices(cmdl.SITUATIONS))

    # Origine géographique
    nationalite_id = SelectField(_l('Nationalité'), validators=validators1())    
    region_origine_id = SelectField(_l("Region d'origine"), validators=validators1())    
    departement_origine_id = SelectField(_l("Departement d'origine"), validators=validators1())    
    langue_id = SelectField(_l('Langue'), validators=validators1(), choices=choices(cmdl.LANGUES))

    # Choix concours
    filiere_id = SelectField(_l('Filière sollicitée'), validators=validators1())
    option_id = SelectField(_l('Option sollicitée'), validators=validators1())
    classe_id = SelectField(_l("Niveau examen"), validators=validators1())
    centre_id = SelectField(_l("Centre examen"), validators=validators1())
    # diplome_id = StringField(_l("Diplôme donnant droit au concours"), validators=validators1())

    # Coordonnées
    telephone = StringField(_l('Téléphone'), validators=validators1())    
    email = EmailField(_l('Email'))

    