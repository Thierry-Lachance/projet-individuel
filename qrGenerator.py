from Chairlift import Chairlift
import cv2
import qrcode
import socket

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
    return data

def prendrePhoto():
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        raise RuntimeError("probleme cam")


    ret, frame = cam.read()

    if ret:
        cv2.imwrite("photo.jpg", frame)
        print("cool phto")
    else:
        print("pas cool photo")
    cam.release()

def importerQrCode():
    prendrePhoto()

def ouvrirRemoteCam():
    data = "https://" + obtenirIp() + ":8443/"
    print(data)
        
    img = qrcode.make(data)
    img.show()

def obtenirIp():
    return socket.gethostbyname(socket.gethostname())
