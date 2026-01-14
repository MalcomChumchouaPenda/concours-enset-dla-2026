
from core.config import db


class Pays(db.Model):
    __bind_key__ = 'regions_v0'
    __tablename__ = 'pays'
    id = db.Column(db.String(5), primary_key=True)
    code_enset = db.Column(db.String(10))
    code_udo = db.Column(db.String(10))
    nom = db.Column(db.String(100), nullable=False)
    nationalite = db.Column(db.String(100))
    regions = db.relationship('Region', back_populates='pays')

    @property
    def full_id(self):
        return self.id



class Region(db.Model):
    __bind_key__ = 'regions_v0'
    __tablename__ = 'regions'
    id = db.Column(db.String(5), primary_key=True)
    code_enset = db.Column(db.String(10))
    code_udo = db.Column(db.String(10))
    pays_id = db.Column(db.String(5), db.ForeignKey('pays.id'))
    pays = db.relationship('Pays', back_populates='regions')
    nom = db.Column(db.String(100), nullable=False)
    etranger = db.Column(db.Boolean, default=False)
    departements = db.relationship('Departement', back_populates='region')

    @property
    def full_id(self):
        return self.pays.full_id + '-' + self.id
    

class Departement(db.Model):
    __bind_key__ = 'regions_v0'
    __tablename__ = 'departements'
    id = db.Column(db.String(5), primary_key=True)
    code_udo = db.Column(db.String(100))
    region_id = db.Column(db.String(5), db.ForeignKey('regions.id'))
    region = db.relationship('Region', back_populates='departements')
    nom = db.Column(db.String(100), nullable=False)
    etranger = db.Column(db.Boolean, default=False)

    @property
    def full_id(self):
        return self.region.full_id + '-' + self.id

