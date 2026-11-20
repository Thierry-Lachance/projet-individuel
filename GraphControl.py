
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
        
        self.axis = self.figure.add_subplot(111, facecolor="black")
        
        #transforme matplotlib image en image utilisable par tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        #extrait image avec get_tk_widget et place l'image avec .pack
        self.canvas.get_tk_widget().pack(fill="both", expand=True)


#fonction pour que l'image puisse changer lors de la modification des parametres
    def mise_a_jour_image(self,titrey="Personnes par heure"):
        if self.mode_achalandage:
            self.afficher_achalandage()
            return
        
        donnee = self.modele.obtenirDonneesGraphique(11,0,10)

        #Création dictionnaire des noms d'axe des x possible et accesseur de paramètre ajouté
        parametre_obs = self.modele.obtenirParametreObserver()

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
        self.axis.clear()
        self.axis.set(title=titre,
                xlabel=titrex, 
                ylabel=titrey)
        self.axis.yaxis.label.set_color('white')
        self.axis.xaxis.label.set_color('white')
        self.axis.title.set_color('white')
        self.axis.tick_params(color='w', labelcolor='w')
        

        #Cas où aucun paramètre n'est selectionné
        if donnee is None or donnee.size == 0:
            self.axis.text(0.5,0.5,"Aucune données", transform=self.axis.transAxes,
                ha="center", va="center")
        
        else:
            x,y = donnee.T
            self.axis.plot(x, y, label=titre)
            self.axis.legend()

        self.axis.grid(alpha=0.3)
        self.canvas.draw_idle()

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

        self.axis.clear()

        self.axis.bar(
            heures,
            file_attente,
            width=0.8,
            color="tab:red",
            label=f"File d'attente (capacité : {capacite} personnes/heure)",
        )

        self.axis.set(
            title="File d'attente selon l'heure",
            xlabel="Heure",
            ylabel="Personnes en attente",
        )
        self.axis.set_xticks(heures)
        self.axis.set_xticklabels([f"{heure}:00" for heure in heures], rotation=45)
        self.axis.yaxis.label.set_color("white")
        self.axis.xaxis.label.set_color("white")
        self.axis.title.set_color("white")
        self.axis.tick_params(color="w", labelcolor="w")
        self.axis.grid(axis="y", alpha=0.3)
        self.axis.legend()
        self.canvas.draw_idle()

    def afficher_parametres(self):
        self.mode_achalandage = False
        self.mise_a_jour_image()

    
