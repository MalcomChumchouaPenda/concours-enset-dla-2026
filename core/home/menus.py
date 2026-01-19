
from flask_babel import lazy_gettext as _l
from core.utils import navbar, sidebar


navbar.add('home_pg', _l('Accueil'), endpoint='home.index', rank=0)
navbar.add('communique_pdf', _l('Communique'), endpoint='home.communique', rank=2)
navbar.add('concours_help_pg', _l('Aide'), endpoint='home.help', rank=3)
navbar.add('contact_pg', _l('Contact'), url='#contact', rank=15)

# docmenu = navbar.add('doc_menu', _l('Procedures'), rank=1)
# workspacemenu = navbar.add('space_menu', _l('Espaces'), rank=2)
# workspacemenu.add('student_dash', _l('Etudiants'), endpoint='home.student_dashboard')
# workspacemenu.add('teacher_dash', _l('Enseignants'), endpoint='home.teacher_dashboard')
# workspacemenu.add('admin_dash', _l('Administration'), endpoint='home.admin_dashboard')

sidebar.add('home_pg', _l('Accueil'), endpoint='home.index', rank=0)
sidebar.add('profile_dash', _l('Profil'), endpoint='home.profile', rank=1)

