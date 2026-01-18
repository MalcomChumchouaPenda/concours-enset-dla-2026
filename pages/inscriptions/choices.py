
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l
from services.concours_v0_0 import models as cmdl
from services.regions_v0_0 import models as rmdl


def _local_text(obj, field, locale):
    # get locale value
    value = getattr(obj, f'{field}_{locale}')
    return value.upper()


def niveaux(locale):
    items = [('', _('Choisir'))]
    for id_, niveau in cmdl.NIVEAUX.items():
        text = _local_text(niveau, 'nom', locale)
        item = (f'N{id_}', text)
        items.append(item)
    return items

def filieres(locale):
    items = []
    for classe in cmdl.ClasseConcours.query.all():
        filiere = classe.option.filiere
        chain = f'N{classe.niveau_id}'
        value = filiere.id
        text = _local_text(filiere, 'nom', locale)
        item = value, text, chain
        items.append(item)
    items = list(set(items))  # remove duplicated
    items = [(x, y, {'data-chained':z}) for x, y, z in items]
    items.insert(0, ('', _('Choisir'), {}))
    return items

def options(locale):
    items = [('', _('Choisir'), {})]
    for option in cmdl.OptionConcours.query.all():
        chain = option.filiere_id
        value = option.id
        text = _local_text(option, 'nom', locale)
        item = value, text, {'data-chained':chain}
        items.append(item)
    return items

def centres():
    items = [('', _('Choisir'))]
    for centre in cmdl.CentreConcours.query.all():
        value = centre.id
        text = centre.nom.upper()
        item = value, text
        items.append(item)
    return items


def nationalites():
    items = [('', _('Choisir'))]
    for pays in rmdl.Pays.query.all():
        value = pays.id
        text = pays.nationalite.upper()
        item = value, text
        items.append(item)
    return items

def regions():
    items = [('', _('Choisir'), {})]
    for region in rmdl.Region.query.all():
        value = region.id
        text = region.nom.upper()
        chain = region.pays_id
        item = value, text, {'data-chained':chain}
        items.append(item)
    return items

def departements():
    items = [('', _('Choisir'), {})]
    for dep in rmdl.Departement.query.all():
        value = dep.id
        text = dep.nom.upper()
        chain = dep.region_id
        item = value, text, {'data-chained':chain}
        items.append(item)
    return items


def diplomes(locale):
    items = [('', _('Choisir'), {})]
    for diplome in cmdl.DiplomeConcours.query.all():
        if diplome.ouvert:
            value = diplome.id
            text = _local_text(diplome, 'nom', locale)
            chain = f'N{diplome.niveau_id}'
            item = value, text, {'data-chained':chain}
            items.append(item)
    return items


def sexes(locale):
    items = [('', _('Choisir'))]
    for id_, sexe in cmdl.SEXES.items():
        text = _local_text(sexe, 'nom', locale)
        item = (id_, text)
        items.append(item)
    return items

def langues(locale):
    items = [('', _('Choisir'))]
    for id_, langue in cmdl.LANGUES.items():
        text = _local_text(langue, 'nom', locale)
        item = (id_, text)
        items.append(item)
    return items

def situations(locale):
    items = [('', _('Choisir'))]
    for id_, situation in cmdl.SITUATIONS.items():
        text = _local_text(situation, 'nom', locale)
        item = (id_, text)
        items.append(item)
    return items
