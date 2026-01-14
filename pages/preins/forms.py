
from datetime import datetime
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, EmailField, TextAreaField, DateField
from wtforms.validators import DataRequired, ValidationError
from services.preins_v0_0.models import SEXES, SITUATIONS, LANGUES


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


class InfoForm(FlaskForm):

    # Informations personnelles de base
    admission_id = StringField(_l("No d'ordre"))
    matricule = StringField(_l('Matricule'))
    prenom = StringField(_l('Prenoms'))
    nom = StringField(_l('Noms'), validators=validators1())
    date_naissance = DateField(_l('Date de naissance'), validators=validators1())
    lieu_naissance = StringField(_l('Lieu de naissance'), validators=validators1())
    sexe_id = SelectField(_l('Sexe'), validators=validators1(), choices=choices(SEXES))
    situation_matrimoniale_id = SelectField(_l('Situation Matrimoniale'), 
                                            validators=validators1(), 
                                            choices=choices(SITUATIONS))

    # Origine géographique
    nationalite_id = SelectField(_l('Nationalité'), validators=validators1())    
    region_origine_id = SelectField(_l("Region d'origine"), validators=validators1())    
    departement_origine_id = SelectField(_l("Departement d'origine"), validators=validators1())    
    langue_id = SelectField(_l('Langue'), validators=validators1(), choices=choices(LANGUES))

    # Coordonnées
    telephone = StringField(_l('Téléphone'), validators=validators1())    
    email = EmailField(_l('Email'))
    
    # Informations académiques
    departement_academique = StringField(_l('Departement'))
    option = StringField(_l('Option'))
    niveau = StringField(_l('Niveau'))
    diplome = StringField(_l("Diplôme d'entrée"), validators=validators1())
    annee_diplome = IntegerField(_l("Année d'obtention"), validators=validators1())

    # Informations du père/tuteur
    nom_pere = StringField(_l('Nom du père'))
    profession_pere = StringField(_l('Profession du père'))
    telephone_pere = StringField(_l('Téléphone du père'))
    residence_pere = StringField(_l('Residence du père'))

    # Informations de la mère
    nom_mere = StringField(_l('Nom de la mère'))
    profession_mere = StringField(_l('Profession de la mère'))
    telephone_mere = StringField(_l('Téléphone de la mère'))
    residence_mere = StringField(_l('Residence de la mère'))


class SearchInfosForm(FlaskForm):

    id = StringField(_l('Identifiant ou matricule'))
    name = StringField(_l('Noms ou prenoms'))


class FilterInfosForm(FlaskForm):

    departement_academique_id = SelectField(_l('Departement'))
    filiere_id = SelectField(_l('Filiere'))
    niveau_id = SelectField(_l('Niveau'))


class ErrorForm(FlaskForm):

    nom_admis = StringField(_l('Noms et prénoms sur le communiqué'))
    nom_correct = StringField(_l('Noms et prénoms corrigés'))
    filiere_admis = StringField(_l('Option sur le communiqué'))
    filiere_correct_id = SelectField(_l('Option corrigée'))
    niveau_admis = StringField(_l('Niveau sur le communiqué'))
    niveau_correct_id = SelectField(_l('Niveau corrigée'))
    justificatifs = TextAreaField(_l('Pièces justificatives'))

