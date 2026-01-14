from flask import request, abort
from flask_restx import Resource, fields
from core.utils import ApiNamespace
from .models import Admission


ns = ApiNamespace('preins', description="Gestion des inscriptions")


@ns.route('/admissions')
# @ns.roles_accepted('admin_preins')
class AdmissionsApi(Resource):

    def get(self):
        query = Admission.query
        return [
            { 
               "id":row.id,
               "matricule":row.matricule,
               "classe_id":row.classe_id,
               "niveau":row.classe.niveau_id,
               "communique_id":row.communique_id,
               "filiere":row.classe.filiere.nom,
               "departement_id":row.classe.filiere.departement_id,
               "departement":row.classe.filiere.departement.nom,
            } 
            for row in query.all()]
    

