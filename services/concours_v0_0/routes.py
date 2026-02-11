from flask import request, abort
from flask_restx import Resource, fields
from core.config import db
from core.utils import ApiNamespace
from .models import InscriptionConcours


ns = ApiNamespace('concours', description="Gestion du concours")


inscr_model = ns.model('inscription', {
    'id': fields.String,
    'numero_dossier': fields.String,
    'date_inscription': fields.Date,
    'annee_concours': fields.String,
    'nom': fields.String,
    'prenom': fields.String,
    'date_naissance': fields.Date,
    'lieu_naissance': fields.String,
    'sexe_id': fields.String,
    'statut_matrimonial_id': fields.String,
    'departement_origine_id': fields.String,
    'langue_id': fields.String,
    'telephone': fields.String,
    'email': fields.String,
    'classe_id': fields.String,
    'centre_id': fields.String,
    'diplome_id': fields.String,
})


@ns.route('/inscriptions/<inscription_id>')
class InscriptionApi(Resource):

    @ns.marshal_with(inscr_model)
    @ns.doc('find_inscription')
    def get(self, inscription_id):
        inscr = InscriptionConcours.query.filter_by(id=inscription_id).first()
        return inscr

    @ns.doc('add_inscription')
    def post(self, inscription_id):
        data = request.json
        pwd = data.pop('password')
        inscription = InscriptionConcours(**data)
        inscription.id = inscription_id
        inscription.set_password(pwd)
        session = db.session
        session.add(inscription)
        session.commit()
        return {"message": "inscription added"}, 200

    # @ns.doc('update_inscription')
    # def put(self, inscription_id):
    #     inscription = Inscription.query.filter_by(id=inscription_id).first()
    #     data = request.json
    #     password = data.get('password')
    #     if password:
    #         inscription.set_password(password)

    #     lang = data.get('lang')
    #     if lang:
    #         inscription.lang = lang
    #     db.session.commit()
    #     return {"message": "inscription updated"}, 200

    # @ns.doc('delete_inscription')
    # def delete(self, inscription_id):
    #     inscription = Inscription.query.filter_by(id=inscription_id).first()
    #     session = db.session
    #     session.delete(inscription)
    #     session.commit()
    #     return "", 204