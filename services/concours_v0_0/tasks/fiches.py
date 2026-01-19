
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
        c.drawImage(logo_ud_path, 15*mm, height - 38*mm, width=27*mm, height=27*mm)
    else:
        c.rect(20*mm, height - 40*mm, 20*mm, 20*mm, stroke=1)
        c.drawString(25*mm, height - 30*mm, "Logo ENSET")

    if os.path.exists(logo_enset_path):
        # Le logo de l'Université de Douala est placé en haut à droite, au-dessus de la photo
        c.drawImage(logo_enset_path, width - 45*mm, height - 38*mm, width=29*mm, height=29*mm)
    else:
        c.rect(width - 40*mm, height - 40*mm, 20*mm, 20*mm, stroke=1)
        c.drawString(width - 35*mm, height - 30*mm, "Logo UD")

    if os.path.exists(fili):
        c.drawImage(fili, (width-130*mm)/2, (height-130*mm)/2, width=130*mm, height=130*mm, mask='auto') 
    else:
        c.rect(width - 80*mm, height - 40*mm, 20*mm, 20*mm, stroke=0)

    c.setFont(font_name, 14)
    c.setFillColor(couleur_bleu_ud)
    c.drawCentredString(width/2, height - 15*mm, "UNIVERSITÉ DE DOUALA")

    c.setStrokeColorRGB(0,0,0)
    c.setLineWidth(0.5)
    c.line(80*mm, height - 18*mm, width - 80*mm, height - 18*mm)

    c.setFont(font_name, 11)
    c.drawCentredString(width/2, height - 25*mm, "ÉCOLE NORMALE SUPÉRIEURE D'ENSEIGNEMENT TECHNIQUE")

    c.setStrokeColorRGB(0,0,0)
    c.setLineWidth(0.5)
    c.line(85*mm, height - 28*mm, width - 85*mm, height - 28*mm)

    c.setFont(font_name, 9)
    c.drawCentredString(width/2, height - 35*mm, "BP 1872 Douala - Cameroun Tél: (Fax) (237) 33 42 44 39")
    c.drawCentredString(width/2, height - 39*mm, "www.enset-douala.cm - email: cabenset@yahoo.fr")


def generer_petite_entete(canvas, size, y_start):
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

    # Vérifier l'existence des fichiers d'image
    if os.path.exists(logo_ud_path):
        # Le logo ENSET est placé en haut à gauche
        c.drawImage(logo_ud_path, 15*mm, y_start - 12*mm, width=17*mm, height=17*mm)

    if os.path.exists(logo_enset_path):
        # Le logo de l'Université de Douala est placé en haut à droite, au-dessus de la photo
        c.drawImage(logo_enset_path, width - 45*mm, y_start - 12*mm, width=19*mm, height=19*mm)

    c.setFont(font_name, 9)
    c.setFillColor(couleur_bleu_ud)
    c.drawCentredString(width/2, y_start, "UNIVERSITÉ DE DOUALA")

    c.setFont(font_name, 7)
    c.drawCentredString(width/2, y_start - 5*mm, "ÉCOLE NORMALE SUPÉRIEURE D'ENSEIGNEMENT TECHNIQUE")


class Writer:

    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas

    def _register_font(self, file_name):
        font_path = os.path.join(store_dir, 'fonts', file_name)
        font_name, _ = os.path.splitext(file_name)
        pdfmetrics.registerFont(TTFont(font_name, font_path))
        return font_name

class PhotoWriter(Writer):

    def __init__(self, canvas):
        super().__init__(canvas)
        self.photo_width = 40 * mm
        self.photo_height = 40 * mm
        self.text_font = self._register_font('times.ttf')
        self.text_size = 10
    
    def write(self, x, y, image_path=None):
        # Position du rectangle (coin inférieur gauche)
        # Coordonnée x (horizontale)
        # Coordonnée y (verticale)
        
        w = self.photo_width
        h = self.photo_height

        # Dessiner un rectangle
        c = self.canvas
        c.rect(x, y, w, h)
        if image_path:
            c.drawImage(image_path, x, y, w, h)
        else:
            # Calculer la position du texte pour le centrer
            text = 'PHOTO 4 x 4'
            text_font, text_size = self.text_font, self.text_size
            text_width = c.stringWidth(text, text_font, text_size)  # Largeur du texte
            text_height = text_size  # Hauteur approximative du texte (égale à la taille de la police)
            text_x = x + (w - text_width) / 2  # Position horizontale (centrée)
            text_y = y + (w - text_height) / 2 + text_size / 2  # Position verticale (centrée)

            # Écrire le texte au centre du rectangle
            c.setFont(text_font, text_size)
            c.drawString(text_x, text_y, text)



class FieldWriter(Writer):

    def __init__(self, canvas, step=8*mm):
        super().__init__(canvas)
        self.color = black
        self.label_font = self._register_font('times.ttf')
        self.value_font = self._register_font('Crimson-Bold.ttf')
        self.label_size = 8
        self.value_size = 9
        self.y = 0 * mm
        self.x_factor = 1.75
        self.y_step = step

    
    def _eval_width(self, label):
        return pdfmetrics.stringWidth(label, 
                                      self.label_font, 
                                      self.label_size)

    def start(self, y):
        self.y = y
        self.canvas.setFillColor(self.color)
    
    def write(self, x, label, value):
        x_label = x
        x_value = x + self._eval_width(label) + 1*mm
        self._write_label(x_label, label)
        self._write_value(x_value, value)
    
    def _write_label(self, x, label):
        c, y = self.canvas, self.y
        c.setFont(self.label_font, self.label_size)
        c.drawString(x, y, label)

    def _write_value(self, x, value):
        c, y = self.canvas, self.y
        c.setFont(self.value_font, self.value_size)
        c.drawString(x, y, value)

    def step(self):
        self.y -= self.y_step
    
    def move(self, y):
        self.y = y

class KeyFieldWriter(FieldWriter):
    
    def __init__(self, canvas):
        super().__init__(canvas)
        self.special_color = Color(0/255, 60/255, 120/255)
    
    def _write_value(self, x, value):
        c, y = self.canvas, self.y
        c.setFillColor(self.special_color)
        c.setFont(self.value_font, self.value_size)
        c.drawString(x, y, value)
        c.setFillColor(self.color)


def generer_fiche_inscription(inscr, nom_fichier):

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
    c.setFont(font_bold_name, 14)
    c.setFillColor(couleur_bleu_ud)
    c.drawCentredString(width/2, height - 54*mm, f"FICHE D'INSCRIPTION AU CONCOURS 2026")
    
    # c.setFont(font_bold_name, 14)
    # c.drawCentredString(width/2, height - 68*mm, "TEST NOTHING")

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
    x_b2 = x_a2 - 25*mm
    x_b3 = x_a2 + 25*mm

    # le systeme d'ecart entre les lignes
    y_a = height - 75*mm
    dy_a = 9*mm
    dy_b = 12*mm


    # NUM DOSSIER PHYSIQUE
    kwriter = KeyFieldWriter(c)
    kwriter.start(y_a)
    kwriter.write(x_b1, "N° DE DOSSIER :", inscr.numero_dossier)
    kwriter.write(x_b2, "N° DE PAIEMENT :", inscr.id)
    y_a = kwriter.y - dy_b
    
    # PHOTO 4 x 4
    pwriter = PhotoWriter(c)
    pwriter.write(x_b3 + 25*mm, y_a - 20*mm)


    # INFORMATIONS PERSONNELLES
    fwriter = FieldWriter(c)
    fwriter.start(y_a)
    fwriter.write(x_a1, "NOMS ET PRÉNOMS :", inscr.nom_complet.upper())
    fwriter.step()
    fwriter.write(x_b1, "NÉ(E) LE :", inscr.date_naissance.strftime('%d/%m/%Y'))
    fwriter.write(x_b2, "A :", inscr.lieu_naissance.upper())
    fwriter.step()
    fwriter.write(x_b1, "SEXE :", inscr.sexe('fr').upper())
    fwriter.write(x_b2, "SITUATION MATRIMONIALE :", inscr.statut_matrimonial('fr').upper())
    fwriter.step()
    
    departement_origine = inscr.departement_origine
    region = departement_origine.region
    pays = region.pays
    fwriter.write(x_b1, "LANGUE :", inscr.langue('fr').upper())
    fwriter.write(x_b2, "NATIONALITÉ :", pays.nationalite('fr').upper())
    fwriter.step()
    fwriter.write(x_b1, "RÉGION D'ORIGINE :", region.nom('fr').upper())
    fwriter.write(x_b2, "DÉPARTEMENT D'ORIGINE :", departement_origine.nom('fr').upper())
    y_a = fwriter.y - dy_b
    
    # INFORMATIONS SUR LE CONCOURS
    classe = inscr.classe
    option_concours = classe.option
    filiere_concours = option_concours.filiere
    fwriter.move(y_a)
    fwriter.write(x_a1, "FILIERE CHOISIE :", f'{filiere_concours.id}-{filiere_concours.nom_fr}'.upper())
    fwriter.step()
    fwriter.write(x_a1, "OPTION CHOISIE :", f"{option_concours.id}-{option_concours.nom_fr}".upper())
    fwriter.step()
    fwriter.write(x_a1, "DIPLOME CANDIDAT :", inscr.diplome.nom_fr.upper())
    fwriter.step()
    fwriter.write(x_a1, "NIVEAU EXAMEN :", classe.niveau('fr').upper())
    fwriter.write(x_a2, "CENTRE EXAMEN:", inscr.centre.nom.upper())
    fwriter.step()
    y_a = fwriter.y - dy_b


    # TELEPHONES + EMAIL
    fwriter.write(x_a1, "TÉLÉPHONE :", inscr.telephone)
    fwriter.write(x_a2, "EMAIL :", inscr.email)
    fwriter.step()
    y_a = fwriter.y - dy_b

    # SIGNATURES
    c.setFillColor(couleur_bleu_ud)
    c.setFont(font_bold_name, 9)
    c.drawString(x_a1, y_a, "SIGNATURE DE L'AGENT :")
    c.drawString(width - 70*mm, y_a, "SIGNATURE DU CANDIDAT :")
    y_a -= dy_b + 10*mm


    # METADONNEES
    create_date = inscr.date_inscription.strftime('%d/%m/%Y')
    footer = f"Fiche créée le {create_date}"
    c.setFillColor(couleur_texte_noir)
    c.setFont(font_name, 8)
    c.drawCentredString(width/2, y_a + 5*mm, footer)
    y_a -= 5*mm

    # GAP POUR RECEPISSE
    c.setDash([5, 4], 0)
    c.line(1*mm, y_a, width - 1*mm, y_a)
    c.setDash([],0) # IMPORTANT POUR RESTAURER LES LIGNES PAR DEFAUT
    y_a -= 10*mm

    # --- 3. EN-TÊTE AVEC LOGOS ET TEXTE ---
    generer_petite_entete(c, A4, y_a)
    y_a -= 12*mm


    # --- 4. TITRE DU FORMULAIRE ---
    c.setFont(font_bold_name, 12)
    c.setFillColor(couleur_texte_noir)
    c.drawCentredString(width/2, y_a, f"RECEPISSE D'INSCRIPTION AU CONCOURS 2026")
    y_a -= dy_a + 2*mm

    kwriter.y_step = 7*mm
    kwriter.start(y_a)
    kwriter.write(x_b1, "N° DE DOSSIER :", inscr.numero_dossier)
    kwriter.write(x_b2, "N° DE PAIEMENT :", inscr.id)
    kwriter.step()
    
    fwriter.y_step = 7*mm
    fwriter.start(kwriter.y)
    fwriter.write(x_a1, "NOMS :", inscr.nom_complet.upper())
    fwriter.step()

    fwriter.write(x_b1, "NÉ(E) LE :", inscr.date_naissance.strftime('%d/%m/%Y'))
    fwriter.write(x_b2, "A :", inscr.lieu_naissance.upper())
    fwriter.step()

    fwriter.write(x_b1, "NIVEAU EXAMEN :", classe.niveau('fr').upper())
    fwriter.write(x_b2, "CENTRE EXAMEN:", inscr.centre.nom.upper())
    fwriter.step()

    fwriter.write(x_a1, "OPTION CHOISIE :", f"{option_concours.id}-{option_concours.nom_fr}".upper())
    y_a = fwriter.y - dy_b

    # SIGNATURES
    c.setFillColor(couleur_bleu_ud)
    c.setFont(font_bold_name, 9)
    c.drawString(x_a1, y_a + 4*mm, "SIGNATURE DE L'AGENT :")
    
    # METADONNEES
    create_date = inscr.date_inscription.strftime('%d/%m/%Y')
    footer = f"Recepissé créé le {create_date}"
    c.setFillColor(couleur_texte_noir)
    c.setFont(font_name, 8)
    c.drawCentredString(x_b2 + 25*mm, y_a - 10*mm, footer)

    # PHOTO 4 x 4
    pwriter.write(x_b3 + 25*mm, y_a)

    # Sauvegarder le PDF
    c.save()
    return nom_fichier


