from datetime import datetime
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, EmailField, TextAreaField, DateField
from wtforms import FieldList, FormField
from wtforms.validators import DataRequired, ValidationError, Regexp
from core.utils import AttribSelectField


def validators1():
    return [DataRequired()]

def validators2():
     return [
          DataRequired(),
          Regexp(r'^\s*\d{2}/\d{2}/\d{4}\s*$',
                 message=_l("la forme de date valide est DD/MM/YYYY (Exemple:01/01/2000)"))
     ]


class AuthForm(FlaskForm):
    id = StringField(_l('numero de paiement'), validators=validators1())


class CursusRowForm(FlaskForm):

    # information d'un element du cursus
    annee = StringField(_l('Année'), validators=validators1())
    diplome = StringField(_l('Diplôme'), validators=validators1())
    etablissement = StringField(_l('Etablissement'), validators=validators1())
    mention = StringField(_l('Mention'), validators=validators1())

    class Meta:
        csrf = False


class InscrForm(FlaskForm):
    
    # Informations personnelles de base
    prenom = StringField(_l('Prenoms'))
    nom = StringField(_l('Noms'), validators=validators1())
    date_naissance = StringField(_l('Date de naissance'), validators=validators2())
    lieu_naissance = StringField(_l('Lieu de naissance'), validators=validators1())
    sexe_id = SelectField(_l('Sexe'), validators=validators1())
    statut_matrimonial_id = SelectField(_l('Situation Matrimoniale'), validators=validators1())

    # Origine géographique
    nationalite_id = SelectField(_l('Nationalité'), validators=validators1())    
    region_origine_id = AttribSelectField(_l("Region d'origine"), validators=validators1())    
    departement_origine_id = AttribSelectField(_l("Departement d'origine"), validators=validators1())    
    langue_id = SelectField(_l('Langue'), validators=validators1())

    # Coordonnées
    telephone = StringField(_l('Téléphone'), validators=validators1())    
    email = EmailField(_l('Email'))

    # cursus academique
    cursus = FieldList(FormField(CursusRowForm), min_entries=2)
    
    
class NewInscrForm(InscrForm):
   
    # Choix concours
    niveau_id = SelectField(_l("Niveau examen"), validators=validators1())
    filiere_id = AttribSelectField(_l('Filière sollicitée'), validators=validators1())
    option_id = AttribSelectField(_l('Option sollicitée'), validators=validators1())
    centre_id = SelectField(_l("Centre examen"), validators=validators1())
    diplome_id = SelectField(_l("Diplôme du candidat"), validators=validators1())


class EditInscrForm(InscrForm):
   
    # Choix concours
    niveau = StringField(_l("Niveau examen"))
    filiere = StringField(_l('Filière sollicitée'))
    option = StringField(_l('Option sollicitée'))
    centre = StringField(_l("Centre examen"))
    diplome = StringField(_l("Diplôme du candidat"))
