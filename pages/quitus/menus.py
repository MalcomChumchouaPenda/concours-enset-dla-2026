from core.utils import sidebar, navbar
from flask_babel import lazy_gettext as _l


adminmenu = sidebar.add('admin_quitus_menu', _l('Paiements'), rank=0, accepted=['admin_quitus'])
adminmenu.add('admin_quitus_files_pg', _l('Fichiers'), endpoint='quitus.files', rank=0, 
              accepted=['admin_quitus'])

