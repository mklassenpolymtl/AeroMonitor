import tkinter as tk

fenetre = tk.Tk() # Création de la fenêtre principale
fenetre.title("AeroMonitor")
fenetre.geometry("900x650")

label_ias = tk.Label(fenetre, text="Vitesse indiquée (kt) :")
label_ias.pack(pady=10)

entree_ias = tk.Entry(fenetre)
entree_ias.pack()

def afficher_ias():
    valeur = entree_ias.get()
    print(valeur)

bouton = tk.Button(
    fenetre,
    text="Afficher IAS",
    command=afficher_ias
)
bouton.pack(pady=10)

fenetre.mainloop()