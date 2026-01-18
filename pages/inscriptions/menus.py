
from core.utils import sidebar, navbar
from flask_babel import lazy_gettext as _l


navbar.add('register_pg', _l('Inscription'), endpoint='inscriptions.view', rank=1)


dashmenu = sidebar.add('inscription_view_pg', _l('Inscription'), 
                       endpoint='inscriptions.view', rank=10,
                       accepted=['inscrit_concours'])

dashmenu = sidebar.add('inscription_new_pg', _l('Inscription'), 
                       endpoint='inscriptions.new', rank=10,
                       accepted=['candidat_concours'])
