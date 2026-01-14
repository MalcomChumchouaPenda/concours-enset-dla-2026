
from core.config import db


class Quitus(db.Model):
    __bind_key__ = 'quitus_v0'
    __tablename__ = 'quitus'
    id = db.Column(db.String(15), primary_key=True)
    matricule = db.Column(db.String(9), nullable=False)
    code_etape = db.Column(db.String(15), nullable=False)
    annee_academique = db.Column(db.String(20), nullable=False)
    tranche = db.Column(db.String(10))
    montant_paye = db.Column(db.Integer)
    montant_a_payer = db.Column(db.Integer)


