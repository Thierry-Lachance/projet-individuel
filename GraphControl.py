
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk



class GraphControl(tk.Frame):

    def __init__(self,parent,modele,achalandage=None):
        super().__init__(parent)
        self.modele = modele
        self.achalandage = achalandage
        self.mode_achalandage = False
        self.creation_image()

#fonction pour créer une image
    def creation_image(self):
        self.figure = Figure(figsize=(6, 3.5), facecolor="black")
        
        self.axe = self.figure.add_subplot(111, facecolor="black")
        
        #transforme matplotlib image en image utilisable par tkinter
        self.canevas = FigureCanvasTkAgg(self.figure, master=self)
        #extrait image avec get_tk_widget et place l'image avec .pack
        self.canevas.get_tk_widget().pack(fill="both", expand=True)


#fonction pour que l'image puisse changer lors de la modification des parametres
    def mise_a_jour_image(self,titrey="Personnes par heure"):
        if self.mode_achalandage:
            self.afficher_achalandage()
            return
        
        donnee = self.modele.obtenirDonneesGraphique(11,0,10)

        #Création dictionnaire des noms d'axe des x possible et accesseur de paramètre ajouté
        parametre_obs = self.modele.obtenirParametreObserve()

        #Création attribut du titre de l'axe des x
        titrex_dic ={"vitesse":["Vitesse"], "nombreDeChaise":["Nombre de chaise"], "longueurDuTrajet":["Longueur du trajet"],
                  "tempsEmbarquement":["Temps embarquement"], "tempsDebarquement":["Temps debarquement"], "nombreDePersonnesParChaise":["Personnes par chaise"], "none":["Vide"]}
        #Création attribut du titre de graphique
        titre_dic ={"vitesse":["Débit selon la vitesse"], "nombreDeChaise":["Débit selon les chaises"], "longueurDuTrajet":["Débit selon la longueur"],
                    "tempsEmbarquement":["Débit selon l'embarquement"],"tempsDebarquement":["Débit selon débarquement"],"nombreDePersonnesParChaise":["Débit selon la capacité par chaise"],
                    "none":["Aucun paramètre sélectionné"]}      

        #Créer les titres concrets qui vont être mis dans le graphique
        
        titrex = titrex_dic[parametre_obs][0]
        titre = titre_dic[parametre_obs][0]

        #Ajouter les bons axes au graphique
        self.axe.clear()
        self.axe.set(title=titre,
                xlabel=titrex, 
                ylabel=titrey)
        self.axe.yaxis.label.set_color('white')
        self.axe.xaxis.label.set_color('white')
        self.axe.title.set_color('white')
        self.axe.tick_params(color='w', labelcolor='w')
        

        #Cas où aucun paramètre n'est selectionné
        if donnee is None or donnee.size == 0:
            self.axe.text(0.5,0.5,"Aucune données", transform=self.axe.transAxes,
                ha="center", va="center")
        
        else:
            x,y = donnee.T
            self.axe.plot(x, y, label=titre)
            self.axe.legend()

        self.axe.grid(alpha=0.3)
        self.canevas.draw_idle()

    def afficher_achalandage(self):
        self.mode_achalandage = True
        heures = list(range(24))

        if self.achalandage is None:
            arrivees = [0] * 24
        else:
            arrivees = self.achalandage.obtenir_achalandage()

        capacite = self.modele.calculerNombreDePersonnesParHeure()
        file_attente = []
        restante = 0

        for nombre_arrivants in arrivees:
            restante = max(0, restante + nombre_arrivants - capacite)
            file_attente.append(restante)

        self.axe.clear()

        self.axe.bar(
            heures,
            file_attente,
            width=0.8,
            color="tab:red",
            label=f"File d'attente (capacité : {capacite} personnes/heure)",
        )

        self.axe.set(
            title="File d'attente selon l'heure",
            xlabel="Heure",
            ylabel="Personnes en attente",
        )
        self.axe.set_xticks(heures)
        self.axe.set_xticklabels([f"{heure}:00" for heure in heures], rotation=45)
        self.axe.yaxis.label.set_color("white")
        self.axe.xaxis.label.set_color("white")
        self.axe.title.set_color("white")
        self.axe.tick_params(color="w", labelcolor="w")
        self.axe.grid(axis="y", alpha=0.3)
        self.axe.legend()
        self.canevas.draw_idle()

    def afficher_parametres(self):
        self.mode_achalandage = False
        self.mise_a_jour_image()

    
