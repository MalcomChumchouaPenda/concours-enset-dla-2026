
CONTACT = {
    "addresse":"Campus Ndogbong, Universite de Douala",
    "ville":"Douala - Cameroun",
    "tel": "(+237) 699753095 / 653005295 /694284900",
    "email": "cabenset@yahoo.fr",
    "postal": "1872 Douala-Cameroun",
    "twitter":"",
    "facebook":"",
    "instagram":"",
    "linkedin":""
}

LINKS = [
    {
        "group":"Liens Utiles",
        "links":[
            {"url":"https://www.univ-douala.cm/", "nom":"Universite de Douala"},
            {"url":"http://www.systhag-online.cm/", "nom":"Systhag Online"},
            {"url":"https://www.minesup.gov.cm/", "nom":"Ministere de l'Enseignement Superieur"}
        ]
    }
]

def get_contact(name=None):
    return CONTACT

def get_links(group=None):
    return LINKS

