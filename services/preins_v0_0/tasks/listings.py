

from services.regions_v0_0 import tasks as region_tasks
from services.formations_v0_0 import tasks as format_tasks

def lister_nationalites():
    items = region_tasks.list_nationalites(full_id=True)
    return items

def lister_regions():
    items = region_tasks.list_regions(full_id=True)
    return items

def lister_departements_origines():
    items = region_tasks.list_departements(full_id=True)
    return items

def lister_departements_academiques():
    items = format_tasks.list_departements()
    return items

def lister_filieres():
    items = format_tasks.list_filieres()
    return items

def lister_niveaux():
    items = format_tasks.list_niveaux()
    return items
