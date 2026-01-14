
from core.utils import sidebar, navbar
from flask_babel import lazy_gettext as _l

dashmenu = sidebar.add('concours_menu', _l('Inscription'), rank=0, accepted=['developper'])
dashmenu.add('concours_identity_pg', 'Etape 1: Identite', endpoint='concours.identity', rank=0)
dashmenu.add('concours_options_pg', 'Etape 2: Options', endpoint='concours.options', rank=2)
dashmenu.add('concours_contacts_pg', 'Etape 3: Contacts', endpoint='concours.contacts', rank=3)
dashmenu.add('concours_summary_pg', 'Fiche', endpoint='concours.summary', rank=4)
