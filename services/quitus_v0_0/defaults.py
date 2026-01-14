
import os
import csv
from core.config import db
from core.auth.tasks import add_role, add_user, add_roles_to_user, get_user


store_dir = os.path.join(os.path.dirname(__file__), 'store')

def _read_csv(filename, sep=','):
    filepath = os.path.join(store_dir, filename)
    with open(filepath, mode='r') as file:
        reader = csv.DictReader(file, delimiter=sep)
        records = list(reader)
    return records


def init_data():
    session = db.session
    if not get_user(session, 'dev0'):
        add_user(session, 'dev0', 'Root developper', '2025')
    add_role(session, 'admin_quitus', 'Gestionnaire Quitus')
    add_roles_to_user(session, 'dev0', 'admin_quitus', 'developper', 'admin_preins')

    