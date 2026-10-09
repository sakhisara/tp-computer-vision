import cv2
import numpy as np

# Canevas : hauteur = 350, largeur = 700
image = np.full((350, 700, 3), 235, dtype=np.uint8)

# Couleurs au format BGR
violet = (125, 40, 55)
bleu = (170, 125, 0)


def dess_polygone(points, couleur):
    points = np.array(points, dtype=np.int32)
    cv2.fillPoly(image, [points], couleur, lineType=cv2.LINE_AA)


# 1. Trait bleu oblique reliant le A au M
dess_polygone(
    [(28, 230), (151, 154), (147, 170)],
    bleu
)

# 2. Lettre M stylisée
dess_polygone(
    [
        (145, 120),
        (199, 233),
        (247, 134),
        (245, 120),
        (335, 315),
        (311, 315),
        (249, 169),
        (193, 277),
        (145, 170)
    ],
    bleu
)

# 3. Lettre A stylisée, dessinée devant le trait bleu
dess_polygone(
    [
        (5, 289),
        (69, 136),
        (67, 120),
        (157, 315),
        (133, 315),
        (68, 172)
    ],
    violet
)

# 4. Texte principal
cv2.putText(
    image,
    "ensam",
    (325, 245),                  # Position du texte
    cv2.FONT_HERSHEY_SIMPLEX,     # Police
    3.0,                         # Taille
    violet,
    9,                           # Epaisseur
    cv2.LINE_AA
)

# 5. Texte secondaire
cv2.putText(
    image,
    "CASABLANCA",
    (480, 270),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.65,
    bleu,
    1,
    cv2.LINE_AA
)

# Enregistrer et afficher
cv2.imwrite("logo_ensam.png", image)
cv2.imshow("Logo ENSAM Casablanca", image)

cv2.waitKey(0)
cv2.destroyAllWindows()