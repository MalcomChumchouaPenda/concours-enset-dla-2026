
from datetime import datetime
import pytest
from core.config import db
from core.auth import tasks as auth_tsk
from services.concours_v0_0 import models as con_mdl


def create_user(uid, roleids):
    user = auth_tsk.add_user(uid, uid, '0000')
    for roleid in roleids:
        role = auth_tsk.get_role(roleid)
        auth_tsk.add_role_to_user(user, role)
    return user

def create_inscr(uid, numero):
    inscr = con_mdl.InscriptionConcours(
        id = uid,
        numero_dossier = numero,
        prenom = 'ARISTIDE JUNIOR', 
        nom = 'KONOFINO NEMALA', 
        date_naissance = datetime(2026, 1, 22).date(), 
        lieu_naissance = 'DOUALA', 
        sexe_id = 'F', 
        statut_matrimonial_id = 'C', 
        departement_origine_id = 'CO',
        diplome_id = 'BAC_C',
        langue_id = 'EN', 
        classe_id = 'BTP1', 
        centre_id = 'BAF', 
        telephone = '655234566', 
        email = ''
    )
    db.session.add(inscr)
    db.session.commit()
    return inscr


@pytest.fixture
def new_user(app):
    with app.app_context():
        user = create_user('06800000009', ['inscrit_concours'])
        create_inscr('06800000009', '26BAF-BACCDE-0009')
    yield user
    db.session.remove()

# @pytest.fixture(scope="module")
# def test_client():
#     # Create a test client
#     app.config['TESTING'] = True
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
#     with app.test_client() as client:
#         yield client

# @pytest.fixture(scope="module", autouse=True)
# def init_db():
#     # Create the tables and populate them with the necessary data
#     db.create_all()
#     yield
#     db.drop_all()

BASE_URL = 'http://localhost:5000'


@pytest.mark.usefixtures('new_user')
def test_login_with_playwright(page):
    page.goto(f'{BASE_URL}/home/login')
    page.fill('input[name="bid"]', '06800')
    page.fill('input[name="rid"]', '000009')
    page.fill('input[name="password"]', '0000')
    page.click('input[type="submit"]')
    page.wait_for_url(f'{BASE_URL}/inscriptions/view')
    assert "Welcome to the Dashboard!" in page.inner_text('body')
