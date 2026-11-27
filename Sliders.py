import customtkinter as ctk
import cv2
from PIL import Image
from tkinter import IntVar, filedialog, messagebox
import qrGenerator as qr

# Constante des paddings pour les widgets de chaque paramètre
MARGE_EN_Y = 30
MARGE_EN_X = 10

"""LEGENDE radio var et ordre des curseurs"""
"------------------------------------------"
"Longueur cable :     1"
"Nombre chaise :      2"
"Vitesse :            3"
"Temps embarquement : 4"
"Temps debarquement : 5"
"Capacite chaise :    6"

class Sliders(ctk.CTkFrame) :

    def __init__(self, parent, remonte_mecanique, achalandage, sur_mise_a_jour) :
        # Passage du Ctk parent pendant le constructeur, donc pour qu'il soit dans la MainApp
        super().__init__(parent)

        # Initialiser le Chairlift courant et appeler la création des widgets
        self.remonte_mecanique = remonte_mecanique
        self.achalandage = achalandage
        self._fenetre_scanner_qr: ctk.CTkToplevel | None = None
        self.creer_widgets()
        self.mise_a_jour = sur_mise_a_jour
        

    def creer_widgets(self) :

        # Créer les boutons d'importation et d'exportation, leur passer la commande _quand_importer qui est appelé si les boutons sont cliqués
        self.bouton_importer = ctk.CTkButton(self, text="Importer un CSV", command=self._quand_importer)
        self.bouton_importer.grid(row=6, column=0, padx=MARGE_EN_X, pady=20)
        self.bouton_exporter = ctk.CTkButton(self, text="Exporter un CSV", command=self._quand_exporter)
        self.bouton_exporter.grid(row=6, column=1, padx=MARGE_EN_X, pady=20)
        self.bouton_importerAchalandage = ctk.CTkButton(self, text="Importer l'achalandage", command=self._quand_importerAchalandage)
        self.bouton_importerAchalandage.grid(row=6, column=2, padx=MARGE_EN_X, pady=20)
        self.bouton_importer_code_qr = ctk.CTkButton(self, text="Importer d'un code QR", command=self._quand_importer_code_qr)
        self.bouton_importer_code_qr.grid(row=7, column=0, padx=MARGE_EN_X, pady=20)
        self.bouton_exporter_code_qr = ctk.CTkButton(self, text="Exporter vers un code QR", command=lambda: qr.generer_code_qr_exporter(self.remonte_mecanique))
        self.bouton_exporter_code_qr.grid(row=7, column=1, padx=MARGE_EN_X, pady=20)
        self.bouton_camera_distante = ctk.CTkButton(self, text="Ouvrir la caméra distante", command=lambda: qr.ouvrir_camera_distante())
        self.bouton_camera_distante.grid(row=7, column=2, padx=MARGE_EN_X, pady=20)

        # initialiser la variable pour les "radiobutton", empêche que plusieurs soient cochés
        self.variable_radio = IntVar(value=0)

        # Appeler les fonctions de création de chacun des paramètres du remonte_mecanique
        self.creer_widgets_cable()
        
        self.creer_widgets_chaise()

        self.creer_widgets_vitesse()

        self.creer_widgets_embarque()

        self.creer_widgets_debarque()
        
        self.creer_widgets_capacite()

        # Configurer les colonnes pour qu'ils prennent le frame, lorsqu'elle est étirée
        for i in range(8) :
            self.grid_rowconfigure(i, weight=1)
        
    def _quand_importer_code_qr(self) -> None:
        if self._fenetre_scanner_qr is not None and self._fenetre_scanner_qr.winfo_exists():
            self._fenetre_scanner_qr.focus_force()
            return

        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            camera.release()
            messagebox.showerror(
                "Caméra indisponible",
                "Impossible d'ouvrir la caméra de cet ordinateur.",
                parent=self,
            )
            return

        fenetre = ctk.CTkToplevel(self)
        self._fenetre_scanner_qr = fenetre
        fenetre.title("Importer un code QR")
        fenetre.geometry("700x580")
        fenetre.transient(self.winfo_toplevel())
        fenetre.grab_set()

        etiquette_apercu = ctk.CTkLabel(fenetre, text="Démarrage de la caméra...")
        etiquette_apercu.pack(padx=10, pady=10)
        etiquette_statut = ctk.CTkLabel(
            fenetre, text="Présentez un code QR exporté devant la caméra."
        )
        etiquette_statut.pack(padx=10, pady=5)

        bouton_fermer = ctk.CTkButton(fenetre, text="Annuler")
        bouton_fermer.pack(padx=10, pady=10)

        detecteur = cv2.QRCodeDetector()
        image_apercu = None

        def fermer_scanner() -> None:
            camera.release()
            self._fenetre_scanner_qr = None
            if fenetre.winfo_exists():
                fenetre.destroy()

        def lire_image() -> None:
            nonlocal image_apercu
            if not fenetre.winfo_exists():
                camera.release()
                self._fenetre_scanner_qr = None
                return

            lecture_reussie, cadre = camera.read()
            if not lecture_reussie:
                camera.release()
                etiquette_statut.configure(text="Impossible de lire la caméra.")
                bouton_fermer.configure(text="Fermer")
                return

            cadre_apercu = cv2.cvtColor(cadre, cv2.COLOR_BGR2RGB)
            cadre_apercu = cv2.resize(cadre_apercu, (640, 480))
            image = Image.fromarray(cadre_apercu)
            image_apercu = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=(640, 480),
            )
            etiquette_apercu.configure(image=image_apercu, text="")

            donnees = qr.decoderQrDepuisCadre(cadre, detecteur)
            if donnees:
                try:
                    qr.analyserDonneesQr(donnees)
                except ValueError as erreur:
                    etiquette_statut.configure(text=f"Code QR invalide : {erreur}")
                else:
                    camera.release()
                    try:
                        self.appliquer_donnees_qr(donnees)
                    except ValueError as erreur:
                        etiquette_statut.configure(text=str(erreur))
                    else:
                        etiquette_statut.configure(
                            text=f"Code QR détecté : {donnees}"
                        )
                    bouton_fermer.configure(text="Fermer")
                    return

            fenetre.after(60, lire_image)

        bouton_fermer.configure(command=fermer_scanner)
        fenetre.protocol("WM_DELETE_WINDOW", fermer_scanner)
        fenetre.after(0, lire_image)

        
    # Les suivantes sont appelées pour créer curseurs, texte et boutons, etc. de chacun des paramètres.
    # Le fonctionnement de celles-ci est identique dépendant des paramètres, l'explication est donc seulement fait une fois.
    def creer_widgets_cable(self) :
        # Création du texte lié au paramètre spécifique
        ctk.CTkLabel(self, text="Longueur du câble").grid(row=0, column=0, sticky="w", padx=MARGE_EN_X, pady=MARGE_EN_Y)

        # Création du curseur, sa commande est relié à _quand_curseur_<paramètre>
        self.curseur_cable = ctk.CTkSlider(self, from_=0, to=3000, number_of_steps=3000)
        self.curseur_cable.set(0)
        self.curseur_cable.configure(command=self._quand_curseur_cable)
        self.curseur_cable.grid(row=0, column=1, sticky="ew", padx=MARGE_EN_X, pady=MARGE_EN_Y)

        # Première création du texte affichant la valeur du curseur
        self.text_cable = ctk.CTkLabel(self, text="0" + " m")
        self.text_cable.grid(row=0, column=2, sticky="ew", padx=MARGE_EN_X, pady=MARGE_EN_Y)

        # Création du radio button permettant de choisir le paramètre observé et d'en sélectionner un seul, on leur passe tous la variable variable_radio qui permet de suivre lequel est choisi.
        self.case_cable = ctk.CTkRadioButton(self, text="", command=self._actualiser_curseur, variable=self.variable_radio, value=1)
        self.case_cable.grid(row=0, column=3, sticky="e")

    def creer_widgets_chaise(self) :
        ctk.CTkLabel(self, text="Nombre de chaises").grid(row=1, column=0, sticky="w", padx=MARGE_EN_X, pady=MARGE_EN_Y)
        
        self.curseur_chaise = ctk.CTkSlider(self, from_=0, to=100, number_of_steps=100)
        self.curseur_chaise.set(0)
        self.curseur_chaise.configure(command=self._quand_curseur_chaise)
        self.curseur_chaise.grid(row=1, column=1, sticky="ew", padx=MARGE_EN_X, pady=MARGE_EN_Y)
        
        self.text_chaise = ctk.CTkLabel(self, text="0")
        self.text_chaise.grid(row=1, column=2, sticky="ew", padx=MARGE_EN_X, pady=MARGE_EN_Y)
        
        self.case_chaise = ctk.CTkRadioButton(self, text="", command=self._actualiser_curseur, variable=self.variable_radio, value=2)
        self.case_chaise.grid(row=1, column=3, sticky="e")

    def creer_widgets_vitesse(self) :
        ctk.CTkLabel(self, text="Vitesse").grid(row=2, column=0, sticky="w", padx=MARGE_EN_X, pady=MARGE_EN_Y)
        
        self.curseur_vitesse = ctk.CTkSlider(self, from_=0.0, to=8, number_of_steps=(8*10))
        self.curseur_vitesse.set(0.0)
        self.curseur_vitesse.configure(command=self._quand_curseur_vitesse)
        self.curseur_vitesse.grid(row=2, column=1, sticky="ew", padx=MARGE_EN_X, pady=MARGE_EN_Y)
        
        self.text_vitesse = ctk.CTkLabel(self, text="0" + " m/s")
        self.text_vitesse.grid(row=2, column=2, sticky="ew", padx=MARGE_EN_X, pady=MARGE_EN_Y)
        
        self.case_vitesse = ctk.CTkRadioButton(self, text="", command=self._actualiser_curseur, variable=self.variable_radio, value=3)
        self.case_vitesse.grid(row=2, column=3, sticky="e")

    def creer_widgets_embarque(self) :
        ctk.CTkLabel(self, text="Temps d'embarquement").grid(row=3, column=0, sticky="w", padx=MARGE_EN_X, pady=MARGE_EN_Y)
        
        self.curseur_embarque = ctk.CTkSlider(self, from_=0, to=30, number_of_steps=30)
        self.curseur_embarque.set(0)
        self.curseur_embarque.configure(command=self._quand_curseur_embarque)
        self.curseur_embarque.grid(row=3, column=1, sticky="ew", padx=MARGE_EN_X, pady=MARGE_EN_Y)
        
        self.text_embarque = ctk.CTkLabel(self, text="0" + " s")
        self.text_embarque.grid(row=3, column=2, sticky="ew", padx=MARGE_EN_X, pady=MARGE_EN_Y)
        
        self.case_embarque = ctk.CTkRadioButton(self, text="", command=self._actualiser_curseur, variable=self.variable_radio, value=4)
        self.case_embarque.grid(row=3, column=3, sticky="e")

    def creer_widgets_debarque(self) :
        ctk.CTkLabel(self, text="Temps de débarquement").grid(row=4, column=0, sticky="w", padx=MARGE_EN_X, pady=MARGE_EN_Y)
        
        self.curseur_debarque = ctk.CTkSlider(self, from_=0, to=30, number_of_steps=30)
        self.curseur_debarque.set(0)
        self.curseur_debarque.configure(command=self._quand_curseur_debarque)
        self.curseur_debarque.grid(row=4, column=1, sticky="ew", padx=MARGE_EN_X, pady=MARGE_EN_Y)
        
        self.text_debarque = ctk.CTkLabel(self, text="0" + " s")
        self.text_debarque.grid(row=4, column=2, sticky="ew", padx=MARGE_EN_X, pady=MARGE_EN_Y)
        
        self.case_debarque = ctk.CTkRadioButton(self, text="", command=self._actualiser_curseur, variable=self.variable_radio, value=5)
        self.case_debarque.grid(row=4, column=3, sticky="e")

    def creer_widgets_capacite(self) :
        ctk.CTkLabel(self, text="Capacité des chaises").grid(row=5, column=0, sticky="w",  padx=MARGE_EN_X, pady=MARGE_EN_Y)
        
        self.curseur_capacite = ctk.CTkSlider(self, from_=0, to=8, number_of_steps=8)
        self.curseur_capacite.set(0)
        self.curseur_capacite.configure(command=self._quand_curseur_capacite)
        self.curseur_capacite.grid(row=5, column=1, sticky="ew", padx=MARGE_EN_X, pady=MARGE_EN_Y)
        
        self.text_capacite = ctk.CTkLabel(self, text="0")
        self.text_capacite.grid(row=5, column=2, sticky="ew", padx=MARGE_EN_X, pady=MARGE_EN_Y)
        
        self.case_capacite = ctk.CTkRadioButton(self, text="", command=self._actualiser_curseur, variable=self.variable_radio, value=6)
        self.case_capacite.grid(row=5, column=3, sticky="e")


    # Les suivantes sont appelés lorsque leurs curseurs respectifs changent de valeurs
    # Le fonctionnement de celles-ci est identique dépendant des paramètres, l'explication est donc seulement fait une fois.
    def _quand_curseur_cable(self, valeur) :
        if not self.remonte_mecanique.definirLongueurDuTrajet(valeur) :
            print("erreur de limite")
        self.text_cable.configure(
            text=str(self.remonte_mecanique.obtenirLongueurDuTrajet()) + " m"
        )
        self.mise_a_jour()
    
    def _quand_curseur_chaise(self, valeur) :
        if not self.remonte_mecanique.definirNombreDeChaise(valeur) :
            print("erreur de limite??")
        self.text_chaise.configure(
            text=str(self.remonte_mecanique.obtenirNombreDeChaise())
        )
        self.mise_a_jour()
    
    def _quand_curseur_vitesse(self, valeur) :
        if not self.remonte_mecanique.definirVitesse(valeur) :
            print("erreur de limite??")
        self.text_vitesse.configure(
            text=str(self.remonte_mecanique.obtenirVitesse()) + " m/s"
        )
        self.mise_a_jour()
    
    def _quand_curseur_embarque(self, valeur) :
        if not self.remonte_mecanique.definirTempsEmbarquement(valeur) :
            print("erreur de limite??")
        self.text_embarque.configure(
            text=str(self.remonte_mecanique.obtenirTempsEmbarquement()) + " s"
        )
        self.mise_a_jour()
    
    def _quand_curseur_debarque(self, valeur) :
        if not self.remonte_mecanique.definirTempsDebarquement(valeur) :
            print("erreur de limite??")
        self.text_debarque.configure(
            text=str(self.remonte_mecanique.obtenirTempsDebarquement()) + " s"
        )
        self.mise_a_jour()
    
    def _quand_curseur_capacite(self, valeur) :
        if not self.remonte_mecanique.definirNombreDePersonnesParChaise(valeur) :
            print("erreur de limite??")
        self.text_capacite.configure(
            text=str(self.remonte_mecanique.obtenirNombreDePersonnesParChaise())
        )
        self.mise_a_jour()
    
    
    def _actualiser_curseur(self):
        # Aller chercher la valeur de variable_radio pour déterminer ce qui est sélectionné
        selection = self.variable_radio.get()
    
        if selection == 0 :
            print("Aucun paramètre observé")
    
        """LONGUEUR CABLE"""
        # Encore une fois c'est pareil pour chacun des paramètres
        # On rend le curseur inutilisable si la case est sélectionnée
        self.curseur_cable.configure(state="disabled" if selection == 1 else "normal")

        # appeler le setter du paramètre observé quand la case est choisie
        resultat1 =  self.remonte_mecanique.definirParametreObserve("longueurDuTrajet") if selection == 1 else True

        # Vérifier la sélection et mettre à jour le graph
        if selection == 1  and resultat1 :
            print("Graph longeur cable dans la bonne place")
            self.mise_a_jour()
        if not resultat1 : 
            print("Erreur dans le setter 1")
    
        """NOMBRE DE CHAISES"""
        self.curseur_chaise.configure(state="disabled" if selection == 2 else "normal")
    
        resultat2 = self.remonte_mecanique.definirParametreObserve("nombreDeChaise") if selection == 2 else True
        if selection == 2 and resultat2 :
            print("Graph nombre chaise dans la bonne place")
            self.mise_a_jour()
        if not resultat2 :
            print("Erreur dans le setter 2")
    
        """VITESSE"""
        self.curseur_vitesse.configure(state="disabled" if selection == 3 else "normal")
    
        resultat3 = self.remonte_mecanique.definirParametreObserve("vitesse") if selection == 3 else True
        if selection == 3 and resultat3:
            print("Graph vitesse dans la bonne place")
            self.mise_a_jour()
        if not resultat3 :
            print("Erreur dans le setter 3")
    
        """TEMPS EMBARQUEMENT"""
        self.curseur_embarque.configure(state="disabled" if selection == 4 else "normal")
        resultat4 = self.remonte_mecanique.definirParametreObserve("tempsEmbarquement") if selection == 4 else True
        if selection == 4 and  resultat4:
            print("Graph temps embarquement dans la bonne place")
            self.mise_a_jour()
        if not resultat4 :
            print("Erreur dans le setter 4")
    
        """TEMPS DEBARQUEMENT"""
        self.curseur_debarque.configure(state="disabled" if selection == 5 else "normal")
        resultat5 = self.remonte_mecanique.definirParametreObserve("tempsDebarquement") if selection == 5 else True
        if selection == 5 and resultat5 :
            print("Graph temps debarquement dans la bonne place")
            self.mise_a_jour()
        if not resultat5 :
            print("Erreur dans le setter 5")
    
        """CAPACITÉ CHAISE"""
        self.curseur_capacite.configure(state="disabled" if selection == 6 else "normal")
        resultat6 = self.remonte_mecanique.definirParametreObserve("nombreDePersonnesParChaise") if selection == 6 else True
        if selection == 6 and resultat6 :
            print("Graph capacité dans la bonne place")
            self.mise_a_jour()
        if not resultat6 :
            print("Erreur dans le setter 6")
    
    
    # Fonctions appelées lors de l'appui des boutons d'import et d'export
    def _quand_importer(self) :
        chemin = filedialog.askopenfilename(defaultextension=".csv",
        filetypes=[("Fichiers CSV", "*.csv")])
        if chemin:
            self.remonte_mecanique.importerDepuisCSV(chemin)
        self.appliquer_valeurs_curseurs()
        print("Bouton importer")

    def _quand_importerAchalandage(self) :
        chemin = filedialog.askopenfilename(defaultextension=".csv",
        filetypes=[("Fichiers CSV", "*.csv")])
        if chemin:
            if not self.achalandage.importer_achalandage(chemin):
                messagebox.showerror(
                    "Erreur d'importation",
                    "Impossible d'importer l'achalandage depuis ce fichier CSV.",
                )
        self.mise_a_jour()

    def _quand_exporter(self) :
        chemin = filedialog.asksaveasfilename(defaultextension=".csv",
        filetypes=[("Fichiers CSV", "*.csv")])
        if chemin:
            self.remonte_mecanique.exporterVersCSV(chemin)

    
    def reinitialiser_variable_radio(self) :
        self.variable_radio.set(0)
        self._actualiser_curseur()
        self.remonte_mecanique.definirParametreObserve("none")
        self.mise_a_jour()

    # Modifier les valeurs de des curseurs pour qu'ils correspondent bien à celles importées
    def appliquer_valeurs_curseurs(self) :
        self.curseur_cable.set(self.remonte_mecanique.obtenirLongueurDuTrajet())
        self.text_cable.configure(text=str(self.remonte_mecanique.obtenirLongueurDuTrajet()) + " m")

        self.curseur_capacite.set(self.remonte_mecanique.obtenirNombreDePersonnesParChaise())
        self.text_capacite.configure(text=str(self.remonte_mecanique.obtenirNombreDePersonnesParChaise()))

        self.curseur_chaise.set(self.remonte_mecanique.obtenirNombreDeChaise())
        self.text_chaise.configure(text=str(self.remonte_mecanique.obtenirNombreDeChaise()))

        self.curseur_debarque.set(self.remonte_mecanique.obtenirTempsDebarquement())
        self.text_debarque.configure(text=str(self.remonte_mecanique.obtenirTempsDebarquement()) + " s")

        self.curseur_embarque.set(self.remonte_mecanique.obtenirTempsEmbarquement())
        self.text_embarque.configure(text=str(self.remonte_mecanique.obtenirTempsEmbarquement()) + " s")
        
        self.curseur_vitesse.set(self.remonte_mecanique.obtenirVitesse())
        self.text_vitesse.configure(text=str(self.remonte_mecanique.obtenirVitesse()) + " m/s")

    def appliquer_donnees_qr(self, donnees: str) -> None:
        (
            longueur,
            nombre_chaises,
            vitesse,
            capacite,
            temps_debarquement,
            temps_embarquement,
        ) = qr.analyserDonneesQr(donnees)

        self.reinitialiser_variable_radio()
        valeurs_appliquees = (
            self.remonte_mecanique.definirLongueurDuTrajet(longueur),
            self.remonte_mecanique.definirNombreDeChaise(nombre_chaises),
            self.remonte_mecanique.definirVitesse(vitesse),
            self.remonte_mecanique.definirNombreDePersonnesParChaise(capacite),
            self.remonte_mecanique.definirTempsDebarquement(temps_debarquement),
            self.remonte_mecanique.definirTempsEmbarquement(temps_embarquement),
        )
        if not all(valeurs_appliquees):
            raise ValueError("Les valeurs du code QR n'ont pas pu être appliquées.")

        self.appliquer_valeurs_curseurs()
        self.mise_a_jour()
        
