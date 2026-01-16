from datetime import datetime
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, EmailField, TextAreaField, DateField
from wtforms import FieldList, FormField
from wtforms.validators import DataRequired, ValidationError
from core.utils import AttribSelectField
from services.concours_v0_0 import models as cmdl
from services.regions_v0_0 import models as rmdl


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

def list_niveaux():
    items = [('', 'Choisir')]
    items.extend([(f'N{k}', v) for k,v in cmdl.NIVEAUX.items()])
    return items

def list_filieres():
    query = cmdl.ClasseConcours.query
    items = []
    for classe in query.all():
        filiere = classe.option.filiere
        item = (filiere.id, filiere.nom_fr, f'N{classe.niveau_id}')
        items.append(item)
    items = list(set(items))  # remove duplicated
    items = [(k, v, {'data-chained':d}) for k, v, d in items]
    items.insert(0, ('', 'Choisir', {}))
    return items

def list_options():
    f = lambda obj: (obj.id, obj.nom_fr, {'data-chained':obj.filiere_id})
    query = cmdl.OptionConcours.query
    items = [('', 'Choisir', {})]
    items.extend([f(obj) for obj in query.all()])
    print(items)
    return items

def list_centres():
    query = cmdl.CentreConcours.query
    items = [('', 'Choisir')]
    items.extend([(obj.id, obj.nom) for obj in query.all()])
    return items


def list_nationalites():
    query = rmdl.Pays.query
    items = [('', 'Choisir')]
    items.extend([(obj.id, obj.nom) for obj in query.all()])
    return items

def list_regions():
    f = lambda obj: (obj.id, obj.nom, {'data-chained':obj.pays_id})
    query = rmdl.Region.query
    items = [('', 'Choisir', {})]
    items.extend([f(obj) for obj in query.all()])
    return items

def list_departements():
    f = lambda obj: (obj.id, obj.nom, {'data-chained':obj.region_id})
    query = rmdl.Departement.query
    items = [('', 'Choisir', {})]
    items.extend([f(obj) for obj in query.all()])
    return items


def list_diplomes():
    f = lambda obj: (obj.id, obj.nom_fr, {'data-chained': f'N{obj.niveau_id}'})
    query = cmdl.DiplomeConcours.query
    items = [('', 'Choisir', {})]
    items.extend([f(obj) for obj in query.all()])
    return items

class AuthForm(FlaskForm):
    id = StringField(_l('numero de paiement'), validators=validators1())


class CursusRowForm(FlaskForm):

    # information d'un element du cursus
    annee = StringField(_l('Année'), validators=validators1())
    diplome = StringField(_l('Diplome'), validators=validators1())
    etablissement = StringField(_l('Etablissement'), validators=validators1())
    mention = StringField(_l('Mention'), validators=validators1())

    class Meta:
            csrf = False


class InscrForm(FlaskForm):
    
    # Informations personnelles de base
    prenom = StringField(_l('Prenoms'))
    nom = StringField(_l('Noms'), validators=validators1())
    date_naissance = StringField(_l('Date de naissance'), validators=validators1())
    lieu_naissance = StringField(_l('Lieu de naissance'), validators=validators1())
    sexe_id = SelectField(_l('Sexe'), validators=validators1(), choices=choices(cmdl.SEXES))
    situation_matrimoniale_id = SelectField(_l('Situation Matrimoniale'), 
                                            validators=validators1(), 
                                            choices=choices(cmdl.SITUATIONS))

    # Origine géographique
    nationalite_id = SelectField(_l('Nationalité'), validators=validators1())    
    region_origine_id = AttribSelectField(_l("Region d'origine"), validators=validators1())    
    departement_origine_id = AttribSelectField(_l("Departement d'origine"), validators=validators1())    
    langue_id = SelectField(_l('Langue'), validators=validators1(), choices=choices(cmdl.LANGUES))

    # Coordonnées
    telephone = StringField(_l('Téléphone'), validators=validators1())    
    email = EmailField(_l('Email'))

    # cursus academique
    cursus = FieldList(FormField(CursusRowForm), min_entries=1)
    
    
class NewInscrForm(InscrForm):
   
    # Choix concours
    niveau_id = SelectField(_l("Niveau examen"), validators=validators1(), choices=choices(cmdl.NIVEAUX))
    filiere_id = AttribSelectField(_l('Filière sollicitée'), validators=validators1())
    option_id = AttribSelectField(_l('Option sollicitée'), validators=validators1())
    centre_id = SelectField(_l("Centre examen"), validators=validators1())
    diplome_id = SelectField(_l("Diplôme donnant droit au concours"), validators=validators1())


class EditInscrForm(InscrForm):
   
    # Choix concours
    niveau = StringField(_l("Niveau examen"))
    filiere = StringField(_l('Filière sollicitée'))
    option = StringField(_l('Option sollicitée'))
    centre = StringField(_l("Centre examen"))
    diplome = StringField(_l("Diplôme donnant droit au concours"))
