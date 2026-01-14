
from flask_restx import Resource, fields
from core.utils import ApiNamespace
from .models import Quitus


ns = ApiNamespace('quitus', description="Gestion des quitus de paiement")


quitus_model = ns.model('quitus_v0', {
    'id': fields.String,
    'matricule': fields.String,
    'classe_id': fields.String,
    'communique_id': fields.String
})


@ns.route('/quitus')
# @ns.roles_accepted('admin_preins')
class QuitusApi(Resource):

    @ns.marshal_list_with(quitus_model)
    def get(self):
        query = Quitus.query
        return query.all()
    
