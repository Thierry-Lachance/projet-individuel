from Chairlift import Chairlift
import qrcode

def generateQrCode(chairlift: Chairlift):
    data = chairlift.obtenirLongueurDuTrajet 
    + chairlift.obtenirNombreDeChaise 
    + chairlift.obtenirVitesse 
    + chairlift.obtenirNombreDePersonnesParChaise 
    + chairlift.obtenirTempsDebarquement 
    + chairlift.obtenirTempsEmbarquement
    img = qrcode.make(data)
    img.save('MyQRCode1.png')