
from core.auth import models as auth_mdl
from services.concours_v0_0 import models as con_mdl


def list_incomplete_inscriptions():
    found = []
    for user in auth_mdl.User.query.all():
        print(user)
        query = con_mdl.InscriptionConcours.query
        if not query.filter_by(id=user.id).one_or_none():
            found.append(user)
    return found
