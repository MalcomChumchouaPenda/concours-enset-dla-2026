
import os
import csv
from sqlalchemy import func
from core.config import db
from .. import models as mdl


def list_candidats(temp_dir):
    Inscr = mdl.InscriptionConcours
    query = Inscr.query

    output_name = 'candidats_concours.csv'
    output_path = os.path.join(temp_dir, output_name)
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['numero_dossier', 
                         'numero_paiement', 
                         'nom_complet'])
        for row in query.all():
            writer.writerow([
                row.numero_dossier,
                row.id,
                row.nom_complet
            ])
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
        func.count(Inscr.id).label('effectif')
    )
    query = query.join(Centre).join(Diplome).join(Classe).join(Option)
    query = query.group_by(Centre.id, Diplome.id, Classe.id, Option.id)

    output_name = 'effectif_centres.csv'
    output_path = os.path.join(temp_dir, output_name)
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['centre', 
                         'diplome', 
                         'niveau',
                         'filiere',
                         'effectif'
                         ])
        for row in query.all():
            writer.writerow(row)
    return output_path
