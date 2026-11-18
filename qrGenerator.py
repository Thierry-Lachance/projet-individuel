from Chairlift import Chairlift
import qrcode

def generateQrCodeExporter(chairlift: Chairlift):
    data = (str(chairlift.obtenirLongueurDuTrajet())
        + str(chairlift.obtenirNombreDeChaise())
        + str(chairlift.obtenirVitesse())
        + str(chairlift.obtenirNombreDePersonnesParChaise())
        + str(chairlift.obtenirTempsDebarquement())
        + str(chairlift.obtenirTempsEmbarquement()))
    
    img = qrcode.make(data)
    img.show()