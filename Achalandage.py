import csv


class Achalandage:
    def __init__(self):
        self.achalandage = [0] * 24  #cree les 24h d'achalandage avec 0 client par defaut

    def importer_achalandage(self, chemin_fichier):
        try:
            donnees = [0] * 24
            with open(chemin_fichier, newline="", encoding="utf-8") as fichier:
                lecteur = csv.DictReader(fichier)
                champs_requis = {"Hour", "# of client"}# champs obligatoires pour le bon fonctionnement du programme
                if not champs_requis.issubset(lecteur.fieldnames or []):#verifie si les champs requis sont presents dans le fichier csv
                    raise ValueError("Le fichier doit contenir les colonnes Hour et # of client")

                for ligne in lecteur:
                    heure = ligne["Hour"]#capture l'heure de la ligne
                    nombre_clients = int(ligne["# of client"]) #capture le nombre de clients de la ligne
                    heures, minutes = heure.split(":") #split en heures et minutes
                    if int(heures) not in range(24) or int(minutes) != 0:#verifie si l'heure est valide (0-23) et si les minutes sont 0
                        raise ValueError(f"Heure invalide : {heure}")
                    if nombre_clients < 0:#verifie si le nombre de clients est positif
                        raise ValueError(f"Nombre de clients invalide : {nombre_clients}")
                    donnees[int(heures)] = nombre_clients#ajoute au tableau

            self.achalandage = donnees
            return True
        except (OSError, ValueError, KeyError) as erreur:
            print(f"Erreur lors de l'importation de l'achalandage : {erreur}")
            return False
        
    #getter de l'achalandage
    def obtenir_achalandage(self):
        return self.achalandage
    # getter de l'achalandage par heure
    def obtenir_achalandage_par_heure(self, heure):
        if 0 <= heure < 24:
            return self.achalandage[heure]
        else:
            raise ValueError("L'heure doit être comprise entre 0 et 23.")