
import os
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black, blue, grey, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors


cur_dir = os.path.dirname(__file__)
service_dir = os.path.dirname(cur_dir)
store_dir = os.path.join(service_dir, 'store')

def generer_entete(canvas, size):
    c = canvas
    width, height = size
    couleur_bleu_ud = Color(0/255, 60/255, 120/255)

    # definition de la police
    font_path = os.path.join(store_dir, 'fonts', 'times.ttf')
    font_name = 'times'
    pdfmetrics.registerFont(TTFont(font_name, font_path))
        
    # Positions fixes pour les logos
    logo_ud_path = os.path.join(store_dir, 'imgs', 'udo.jpg')
    logo_enset_path = os.path.join(store_dir, 'imgs', 'enset.jpg')
    fili = os.path.join(store_dir, 'imgs', 'filigrane.jpg')

    # Vérifier l'existence des fichiers d'image
    if os.path.exists(logo_ud_path):
        # Le logo ENSET est placé en haut à gauche
        c.drawImage(logo_ud_path, 15*mm, height - 40*mm, width=30*mm, height=30*mm)
    else:
        c.rect(20*mm, height - 40*mm, 20*mm, 20*mm, stroke=1)
        c.drawString(25*mm, height - 30*mm, "Logo ENSET")

    if os.path.exists(logo_enset_path):
        # Le logo de l'Université de Douala est placé en haut à droite, au-dessus de la photo
        c.drawImage(logo_enset_path, width - 45*mm, height - 40*mm, width=32*mm, height=32*mm)
    else:
        c.rect(width - 40*mm, height - 40*mm, 20*mm, 20*mm, stroke=1)
        c.drawString(width - 35*mm, height - 30*mm, "Logo UD")

    if os.path.exists(fili):
        c.drawImage(fili, (width-130*mm)/2, (height-130*mm)/2, width=130*mm, height=130*mm, mask='auto') 
    else:
        c.rect(width - 80*mm, height - 40*mm, 20*mm, 20*mm, stroke=0)

    c.setFont(font_name, 16)
    c.setFillColor(couleur_bleu_ud)
    c.drawCentredString(width/2, height - 15*mm, "UNIVERSITÉ DE DOUALA")

    c.setStrokeColorRGB(0,0,0)
    c.setLineWidth(0.5)
    c.line(80*mm, height - 18*mm, width - 80*mm, height - 18*mm)

    c.setFont(font_name, 12)
    c.drawCentredString(width/2, height - 25*mm, "ÉCOLE NORMALE SUPÉRIEURE")
    c.drawCentredString(width/2, height - 30*mm, "D'ENSEIGNEMENT TECHNIQUE")

    c.setStrokeColorRGB(0,0,0)
    c.setLineWidth(0.5)
    c.line(85*mm, height - 33*mm, width - 85*mm, height - 33*mm)

    c.setFont(font_name, 10)
    c.drawCentredString(width/2, height - 39*mm, "BP 1872 Douala - Cameroun Tél: (Fax) (237) 33 42 44 39")
    c.drawCentredString(width/2, height - 43*mm, "www.enset-douala.cm - email: cabenset@yahoo.fr")


def generer_fiche_inscription(inscription, nom_fichier):

    # Créer le canvas
    c = canvas.Canvas(nom_fichier, pagesize=A4)
    width, height = A4

    # Définir les couleurs
    couleur_bleu_ud = Color(0/255, 60/255, 120/255)
    couleur_texte_noir = black
            
    # Texte principal de l'en-tête (centré)
    font_path = os.path.join(store_dir, 'fonts', 'times.ttf')
    font_name = 'times'

    font_bold_path = os.path.join(store_dir, 'fonts', 'Crimson-Bold.ttf')
    font_bold_name = 'Crimson-Bold'

    pdfmetrics.registerFont(TTFont(font_bold_name, font_bold_path))
    pdfmetrics.registerFont(TTFont(font_name, font_path))

  
    # --- 1. EN-TÊTE AVEC LOGOS ET TEXTE ---
    generer_entete(c, A4)
    
    # --- 2. TITRE DU FORMULAIRE ---
    c.setFont(font_bold_name, 18)
    c.setFillColor(couleur_bleu_ud)
    c.drawCentredString(width/2, height - 58*mm, f"FICHE D'INSCRIPTION CONCOURS 2026")
    
    c.setFont(font_bold_name, 14)
    c.drawCentredString(width/2, height - 68*mm, "TEST NOTHING")

    # --- 3. NOTE IMPORTANTE ---
    # c.setFont("Helvetica-Oblique", 9)
    # c.setFillColor(couleur_texte_noir)
    # c.drawString(20*mm, height - 71*mm, "NB : À faire remplir par le candidat lui-même car ses informations sont d'une importance capitale pour la")
    # c.drawString(20*mm, height - 75*mm, "délivrance des effets académiques.")

    # --- 4. CHAMPS DU FORMULAIRE AVEC COORDONNÉES FIXES ---

    # DEFINITION DES COORDONNEES

    # le premier systeme de coordonnee a deux colonnes
    x_a1 = 20*mm
    x_a2 = width/2

    # le second systeme de coordonnee a trois colonnes
    x_b1 = x_a1
    x_b2 = x_a2 - 20*mm
    x_b3 = x_a2 + 25*mm

    # le systeme d'ecart entre les lignes
    y_a = height - 85*mm
    dy_a = 9*mm
    dy_b = 12*mm


    # MATRICULE + NUM DOSSIER PHYSIQUE

    c.setFillColor(couleur_texte_noir)
    c.setFont(font_name, 9)
    c.drawString(x_b1, y_a, "N° D'ORDRE :")
    c.setFillColor(couleur_bleu_ud)
    c.setFont(font_bold_name, 10)
    c.drawString(x_b1 + 22*mm, y_a, inscription.id)

    c.setFillColor(couleur_texte_noir)
    c.setFont(font_name, 9)
    c.drawString(x_b3, y_a, "MATRICULE :")
    c.setFillColor(couleur_bleu_ud)
    c.setFont(font_bold_name, 10)
    c.drawString(x_b3 + 22*mm, y_a, 'Nothing')
    y_a -= dy_b


    # INFORMATIONS GENERALES
        
    c.setFillColor(couleur_texte_noir)
    c.setFont(font_name, 9)
    c.drawString(x_a1, y_a, "NOM ET PRÉNOMS :")
    c.setFont(font_bold_name, 10)
    c.drawString(x_a1 + 32*mm, y_a, inscription.nom_complet.upper())
    y_a -= dy_a

    c.setFont(font_name, 9)
    c.drawString(x_b1, y_a, "DATE DE NAISSANCE :")
    c.setFont(font_bold_name, 10)
    c.drawString(x_b1 + 36*mm, y_a, inscription.date_naissance.strftime('%d/%m/%Y'))

    c.setFont(font_name, 9)
    c.drawString(x_b2, y_a, "LIEU :")
    c.setFont(font_bold_name, 10)
    c.drawString(x_b2 + 11*mm, y_a, inscription.lieu_naissance.upper())
    y_a -= dy_a

    c.setFont(font_name, 9)
    c.drawString(x_b1, y_a, "SEXE (F/M) :")
    c.setFont(font_bold_name, 10)
    c.drawString(x_b1 + 20*mm, y_a, inscription.sexe.upper())

    c.setFont(font_name, 9)
    c.drawString(x_b2, y_a, "SITUATION MATRIMONIALE (M/C/D) :")
    c.setFont(font_bold_name, 10)
    c.drawString(x_b2 + 58*mm, y_a, inscription.situation_matrimoniale.upper())
    y_a -= dy_b


    # ORIGINE GEOGRAPHIQUE

    c.setFont(font_name, 9)
    c.drawString(x_b1, y_a, "LANGUE (F/A) :")
    c.setFont(font_bold_name, 10)
    c.drawString(x_b1 + 25*mm, y_a, inscription.langue.upper())

    departement_origine = inscription.departement_origine
    region = departement_origine.region
    pays = region.pays
    
    c.setFont(font_name, 9)
    c.drawString(x_b2, y_a, "NATIONALITÉ :")
    c.setFont(font_bold_name, 10)
    c.drawString(x_b2 + 25*mm, y_a, pays.nationalite.upper())
    y_a -= dy_a

    c.setFont(font_name, 9)
    c.drawString(x_b1, y_a, "RÉGION D'ORIGINE :")
    c.setFont(font_bold_name, 10)
    c.drawString(x_b1 + 31*mm, y_a, region.nom.upper())
    
    c.setFont(font_name, 9)
    c.drawString(x_b2, y_a, "DÉPARTEMENT D'ORIGINE :")
    c.setFont(font_bold_name, 10)
    c.drawString(x_b2 + 43*mm, y_a, departement_origine.nom.upper())
    y_a -= dy_b


    # TELEPHONES + EMAIL

    c.setFont(font_name, 9)
    c.drawString(x_a1, y_a, "TÉLÉPHONE :")
    c.setFont(font_bold_name, 10)
    c.drawString(x_a1 + 22*mm, y_a, inscription.telephone)

    c.setFont(font_name, 9)
    c.drawString(x_a2, y_a, "EMAIL :")
    c.setFont(font_bold_name, 9)
    c.drawString(x_a2 + 14*mm, y_a, inscription.email)
    y_a -= dy_b


    # INFORMATIONS ACADEMIQUES
    classe = inscription.classe
    filiere_concours = classe.option.filiere
    c.setFont(font_name, 9)
    c.drawString(x_a1, y_a, "FILIERE CHOISIE :")
    c.setFont(font_bold_name, 10)
    c.drawString(x_a1 + 40*mm, y_a, f'{filiere_concours.id}-{filiere_concours.nom_fr}'.upper())
    y_a -= dy_a

    option_concours = classe.option
    c.setFont(font_name, 9)
    c.drawString(x_a1, y_a, "OPTION CHOISIE :")
    c.setFont(font_bold_name, 10)
    c.drawString(x_a1 + 28*mm, y_a, f"{option_concours.id}-{option_concours.nom_fr}".upper())
    y_a -= dy_a

    c.setFont(font_name, 9)
    c.drawString(x_b1, y_a, "NIVEAU EXAMEN :")
    c.setFont(font_bold_name, 10)
    c.drawString(x_b1 + 31*mm, y_a, classe.niveau.upper())
    
    c.setFont(font_name, 9)
    c.drawString(x_b3, y_a, "ANNÉE D'OBTENTION :")
    c.setFont(font_bold_name, 10)
    c.drawString(x_b3 + 36*mm, y_a, 'Test')
    y_a -= dy_b

    
    # SIGNATURE ET CACHET
    c.setFont(font_name, 10)
    c.drawString(width - 70*mm, y_a-10*mm, "SIGNATURE DE L'ETUDIANT(E)")
    c.line(width - 190*mm, y_a, width - 15*mm, y_a)


    # METADONNEES ---
    print_date = datetime.now().strftime('%d/%m/%Y')
    create_date = inscription.date_inscription.strftime('%d/%m/%Y')
    footer = f"fiche créée le {create_date} et generée le {print_date}"
    c.setFont(font_name, 9)
    c.drawCentredString(width/2, 7*mm, footer)

    # Sauvegarder le PDF
    c.save()
    return nom_fichier


