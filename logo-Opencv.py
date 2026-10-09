import cv2
import numpy as np

# Créer un canevas blanc
canevas = np.full((420, 480, 3), 255, dtype=np.uint8)

# OpenCV utilise les couleurs dans l'ordre BGR
rouge = (0, 0, 255)
vert = (0, 255, 0)
bleu = (255, 0, 0)
blanc = (255, 255, 255)
noir = (0, 0, 0)


def dess_anneau(image, centre, couleur, debut, fin):

    # Dessiner un disque avec une ouverture c est pour cela on utilise ellipse al la place de cercle
    cv2.ellipse(
        image,
        centre,
        (75, 75),
        0,
        debut,
        fin,
        couleur,
        cv2.FILLED,
        cv2.LINE_AA
    )

    # # Dessiner un cercle blanc au centre pour former l'anneau
    cv2.circle(
        image,
        centre,
        30,#Rayon du cercle blanc
        blanc,
        cv2.FILLED,
        cv2.LINE_AA
    )


# Anneau rouge : ouverture vers le bas
dess_anneau(canevas, (240, 95), rouge, 120, 420)
#dess_anneau(canevas, cord centre, couleur, debut d angle , fin d angle)
# Anneau vert : ouverture vers le haut à droite
dess_anneau(canevas, (155, 245), vert, 0, 300)

# Anneau bleu : ouverture vers le haut
dess_anneau(canevas, (325, 245), bleu, 300, 600)

# Ajouter le texte, centré sous le dessin
texte = "OpenCV"
police = cv2.FONT_HERSHEY_SIMPLEX
taille = 2.4
epaisseur = 5

(largeur, hauteur), _ = cv2.getTextSize(
    texte, police, taille, epaisseur
)

x = (canevas.shape[1] - largeur) // 2

cv2.putText(
    canevas,
    texte,
    (x, 390),
    police,
    taille,
    noir,
    epaisseur,
    cv2.LINE_AA
)

# Afficher le résultat
cv2.imwrite("Logo-OpenCV.png",canevas)
cv2.imshow("Logo-OpenCV", canevas)
cv2.waitKey(0)
cv2.destroyAllWindows()
