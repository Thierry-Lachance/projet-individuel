from Chairlift import Chairlift
import cv2
import qrcode

def generateQrCodeExporter(chairlift: Chairlift):
    data = (str(chairlift.obtenirLongueurDuTrajet()) + "/"
        + str(chairlift.obtenirNombreDeChaise()) + "/"
        + str(chairlift.obtenirVitesse()) + "/"
        + str(chairlift.obtenirNombreDePersonnesParChaise()) + "/"
        + str(chairlift.obtenirTempsDebarquement()) + "/"
        + str(chairlift.obtenirTempsEmbarquement()) + ">")
    
    img = qrcode.make(data)
    img.show()

def decodeQrCode():
    image = cv2.imread("save.png")
    if image is None:
        raise FileNotFoundError("Le fichier save.png est introuvable.")

    data, _, _ = cv2.QRCodeDetector().detectAndDecode(image)
    if not data:
        raise ValueError("Aucune donnée n'a été trouvée dans le code QR.")

    print(data)

