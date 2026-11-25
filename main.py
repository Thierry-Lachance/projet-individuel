from Achalandage import Achalandage
from Sliders import Sliders
from Chairlift import Chairlift
from GraphControl import GraphControl

import customtkinter as ctk
from queue import Empty, Queue
from tkinter import messagebox

from web.webServer import ServeurWeb

class MainApp(ctk.CTk) :

    def __init__(self) :
        # Initialiser la fenêtre principale
        super().__init__()
        self._qr_en_attente: Queue[str] = Queue()
        self.title("Gestionnaire de remonte-pente mécanique")
        self.geometry("1400x800")

        # Initialiser, en privé, le Chairlift courant
        self.__chairlift = Chairlift()

        # Initialiser, en privé, l'achalandage courant
        self.__achalandage = Achalandage()

        # Initialiser la frame des sliders et autres boutons
        self.grid_rowconfigure(0, weight=1)
        self.sliders = Sliders(self, self.__chairlift, self.__achalandage,  self.mettre_a_jour)
        self.sliders.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=12, pady=12)

        # Initialiser la frame du Graphique
        self.graph = GraphControl(self, self.__chairlift, self.__achalandage)
        self.graph.grid(row=0, column=1, columnspan=2, sticky="nsew", padx=12, pady=12)

        # Affichage du label du nombre de personnes par heure avec les paramètres courants.
        self.label_nb_personne = ctk.CTkLabel(self, bg_color="white", text="Nombre de personnes par heure : " + str(self.__chairlift.calculerNombreDePersonnesParHeure()), text_color="black")
        self.label_nb_personne.grid(row=1, column=1, columnspan=2, sticky="nsew", padx=10, pady=(0,12))
        # Bouton de deselection
        self.bouton_deselection = ctk.CTkButton(self, text="Deselectionner", command=self._rafraichissement)
        self.bouton_deselection.grid(row=2, column=1, sticky="nsew", padx=12, pady=(3,12))
        # Bouton qui affiche le graph de l'achalandage
        self.bouton_achalandage = ctk.CTkButton(self, text="Afficher l'achalandage", command=self.graph.afficher_achalandage)
        self.bouton_achalandage.grid(row=2, column=2, sticky="nsew", padx=12, pady=(3,12))

        # Modifier le poids des différentes colonnes
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        #Configurer les rows du grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)

        # Appeler mettre à jour qui met à jour l'image/le graph
        self.mettre_a_jour()
        self.after(100, self._appliquer_qr_en_attente)

    def recevoir_qr(self, donnees: str) -> None:
        self._qr_en_attente.put(donnees)

    def _appliquer_qr_en_attente(self) -> None:
        donnees = None
        try:
            while True:
                donnees = self._qr_en_attente.get_nowait()
        except Empty:
            pass

        if donnees is not None:
            try:
                self.sliders.appliquer_donnees_qr(donnees)
            except ValueError as erreur:
                messagebox.showerror("Code QR invalide", str(erreur))

        self.after(100, self._appliquer_qr_en_attente)

    # Mettre à jour le graphique 
    def mettre_a_jour(self):
        self.graph.mise_a_jour_image()
        
        self.label_nb_personne.configure(text="Nombre de personnes par heure : " + str(self.__chairlift.calculerNombreDePersonnesParHeure()))

    # Commande du bouton de rafraichissement qui recalcule et déselectionne
    def _rafraichissement(self) :
        self.sliders.reset_radio_var()
        self.graph.afficher_parametres()
        
        self.label_nb_personne.configure(text="Nombre de personnes par heure : " + str(self.__chairlift.calculerNombreDePersonnesParHeure()))

#Loop du MainApp et choix de l'apparence du ctk
if __name__ == "__main__" :
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    application = MainApp()
    serveur_web = ServeurWeb(application.recevoir_qr)
    serveur_web.demarrer()
    try:
        application.mainloop()
    finally:
        serveur_web.arreter()
