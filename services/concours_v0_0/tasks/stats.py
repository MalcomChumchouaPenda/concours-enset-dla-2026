
import os
import csv
from sqlalchemy import func
from core.config import db
from .. import models as mdl


def list_candidats(temp_dir):
    Centre = mdl.CentreConcours 
    Diplome = mdl.DiplomeConcours
    Classe = mdl.ClasseConcours
    Option = mdl.OptionConcours
    Filiere = mdl.FiliereConcours
    Inscr = mdl.InscriptionConcours

    query = db.session.query(
        Centre.nom.label('centre'),
        Classe.niveau_id.label('niveau'),
        Inscr.nom,
        Inscr.prenom,
        Inscr.date_naissance,
        Inscr.lieu_naissance,
        Inscr.sexe_id,
        Inscr.langue_id.label('langue'),
        Inscr.numero_dossier,
        Diplome.nom_fr.label('diplome'),
        Option.nom_fr.label('option'),
        Filiere.nom_fr.label('filiere')
    )

    query = query.join(Centre)\
                .join(Diplome)\
                .join(Classe)\
                .join(Option)\
                .join(Filiere)
    
    output_name = 'candidats_concours.csv'
    output_path = os.path.join(temp_dir, output_name)
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['centre',
                         'niveau',
                         'nom', 
                         'prenom', 
                         'date_naiss',
                         'lieu_naiss',
                         'genre',
                         'langue',
                         'numero_dossier',
                         'option',
                         'filiere'
                         ])
        for row in query.all():
            writer.writerow(row)
    return output_path


def count_candidats_by_center(temp_dir): 
    Centre = mdl.CentreConcours 
    Diplome = mdl.DiplomeConcours
    Classe = mdl.ClasseConcours
    Option = mdl.OptionConcours
    Inscr = mdl.InscriptionConcours

    query = db.session.query(
        Centre.nom.label('centre'),
        Diplome.nom_fr.label('diplome'),
        Classe.niveau_id.label('niveau'),
        Option.nom_fr.label('filiere'),
        Inscr.langue_id.label('langue'),
        func.count(Inscr.id).label('effectif')
    )
    query = query.join(Centre).join(Diplome).join(Classe).join(Option)
    query = query.group_by(Centre.id, Diplome.id, Classe.id, 
                           Option.id, Inscr.langue_id)

    output_name = 'effectif_centres.csv'
    output_path = os.path.join(temp_dir, output_name)
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['centre', 
                         'diplome', 
                         'niveau',
                         'filiere',
                         'langue',
                         'effectif'
                         ])
        for row in query.all():
            writer.writerow(row)
    return output_path
