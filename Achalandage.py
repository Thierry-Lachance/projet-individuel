import csv


class Achalandage:
    def __init__(self):
        self.achalandage = [0] * 24  

    def importer_achalandage(self, chemin_fichier):
        try:
            donnees = [0] * 24
            with open(chemin_fichier, newline="", encoding="utf-8") as fichier:
                lecteur = csv.DictReader(fichier)
                champs_requis = {"Hour", "# of client"}
                if not champs_requis.issubset(lecteur.fieldnames or []):
                    raise ValueError("Le fichier doit contenir les colonnes Hour et # of client")

                for ligne in lecteur:
                    heure = ligne["Hour"]
                    nombre_clients = int(ligne["# of client"])
                    heures, minutes = heure.split(":")
                    if int(heures) not in range(24) or int(minutes) != 0:
                        raise ValueError(f"Heure invalide : {heure}")
                    if nombre_clients < 0:
                        raise ValueError(f"Nombre de clients invalide : {nombre_clients}")
                    donnees[int(heures)] = nombre_clients

            self.achalandage = donnees
            return True
        except (OSError, ValueError, KeyError) as erreur:
            print(f"Erreur lors de l'importation de l'achalandage : {erreur}")
            return False

    def obtenir_achalandage(self):
        return self.achalandage
    def obtenir_achalandage_par_heure(self, heure):
        if 0 <= heure < 24:
            return self.achalandage[heure]
        else:
            raise ValueError("L'heure doit être comprise entre 0 et 23.")