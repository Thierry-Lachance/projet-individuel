from Chairlift import Chairlift
import cv2
import numpy as np
import qrcode
import socket

#package tout les parametres d'une remonte mecanique dans un code qr et l'affiche
def generer_code_qr_exporter(remonte_mecanique: Chairlift):
    donnees = (str(remonte_mecanique.obtenirLongueurDuTrajet()) + "/"
        + str(remonte_mecanique.obtenirNombreDeChaise()) + "/"
        + str(remonte_mecanique.obtenirVitesse()) + "/"
        + str(remonte_mecanique.obtenirNombreDePersonnesParChaise()) + "/"
        + str(remonte_mecanique.obtenirTempsDebarquement()) + "/"
        + str(remonte_mecanique.obtenirTempsEmbarquement()) + ">")
    
    image = qrcode.make(donnees)
    image.show()#affiche le code qr dans une fenetre

#detecte un code qr a partir du tableau numpy et retourne les donnees
def decoderQrDepuisCadre(cadre: np.ndarray, detecteur=None) -> str | None:
    if detecteur is None:#si pas de dectecteur on en cree un
        detecteur = cv2.QRCodeDetector()
    donnees, _, _ = detecteur.detectAndDecode(cadre)
    return donnees or None
#decode un code qr depuis une image
def decoderQrDepuisImage(image_jpeg: bytes) -> str | None:
    cadre = cv2.imdecode(np.frombuffer(image_jpeg, dtype=np.uint8), cv2.IMREAD_COLOR)#convertie l'image en tableau numpy
    if cadre is None:#safety
        return None
    return decoderQrDepuisCadre(cadre)

#parse les donnees du code qr, les verifie et les retourne sous forme de tuple
def analyserDonneesQr(donnees: str) -> tuple[int, int, float, int, int, int]:
    donnees = donnees.strip()#enleve les espaces avant et apres le code qr
    if not donnees.endswith(">"):
        raise ValueError("Le code QR ne respecte pas le format d'export.")

    champs = [champ.strip() for champ in donnees[:-1].split("/")]#divise les donnees en champs
    if len(champs) != 6:
        raise ValueError("Le code QR doit contenir six valeurs.")

    try:
        longueur = int(champs[0])
        nombre_chaises = int(champs[1])
        vitesse = float(champs[2])
        capacite = int(champs[3])
        temps_debarquement = int(champs[4])
        temps_embarquement = int(champs[5])
    except ValueError as erreur:
        raise ValueError("Le code QR contient une valeur numérique invalide.") from erreur

    if not 0 <= longueur <= 3000:
        raise ValueError("La longueur doit être comprise entre 0 et 3000 m.")
    if not 0 <= nombre_chaises <= 100:
        raise ValueError("Le nombre de chaises doit être compris entre 0 et 100.")
    if not 0 <= vitesse <= 8 or round(vitesse, 1) != vitesse:
        raise ValueError("La vitesse doit être comprise entre 0 et 8 m/s, par pas de 0,1.")
    if not 0 <= capacite <= 8:
        raise ValueError("La capacité doit être comprise entre 0 et 8 personnes.")
    if not 0 <= temps_debarquement <= 30:
        raise ValueError("Le temps de débarquement doit être compris entre 0 et 30 s.")
    if not 0 <= temps_embarquement <= 30:
        raise ValueError("Le temps d'embarquement doit être compris entre 0 et 30 s.")

    return (
        longueur,
        nombre_chaises,
        vitesse,
        capacite,
        temps_debarquement,
        temps_embarquement,
    )

#genere un code qr pour ouvrir le lien de la cam
def ouvrir_camera_distante():
    donnees = "https://" + obtenir_adresse_ip() + ":8443/"
    print(donnees)
        
    image = qrcode.make(donnees)
    image.show()#affiche le code qr dans une fenetre
    
#obtient l'addresse ip de l'ordi
def obtenir_adresse_ip():
    return socket.gethostbyname(socket.gethostname())
