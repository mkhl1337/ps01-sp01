import customtkinter as ctk
import json
import os
from tkinter import messagebox

JSON_FILE = "livres.json"
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg_main":    "#0f1117",
    "bg_card":    "#1a1d2e",
    "bg_input":   "#252840",
    "accent":     "#6c63ff",
    "accent2":    "#ff6584",
    "text":       "#e8e8f0",
    "text_dim":   "#8888aa",
    "success":    "#4ecca3",
    "danger":     "#ff4757",
    "border":     "#2e3150",
}


def charger_livres() -> list:
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def sauvegarder_livres(livres: list) -> None:
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(livres, f, ensure_ascii=False, indent=2)


def prochain_id(livres: list) -> int:
    if not livres:
        return 1
    return max(l["id_livre"] for l in livres) + 1


class BibliothequeApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title(" Bibliothèque")
        self.geometry("1200x750")
        self.resizable(True, True)
        self.configure(fg_color=COLORS["bg_main"])

        self.livres: list = charger_livres()
        self.id_selectionne: int | None = None

        self._build_ui()
        self._rafraichir_liste()

    def _build_ui(self):
        titre = ctk.CTkLabel(
            self,
            text="  Bibliothèque Intelligente",
            font=ctk.CTkFont(family="Georgia", size=28, weight="bold"),
            text_color=COLORS["accent"],
        )
        titre.pack(pady=(20, 5))

        sous_titre = ctk.CTkLabel(
            self,
            text="Gestion de livres",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_dim"],
        )
        sous_titre.pack(pady=(0, 20))

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self._build_formulaire(main_frame)
        self._build_liste(main_frame)

    def _build_formulaire(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=16)
        card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        ctk.CTkLabel(
            card,
            text="  Formulaire",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"],
        ).pack(pady=(20, 15))

        champs = [
            ("titre",               "Titre du livre :"),
            ("auteur",              "Auteur :"),
            ("categorie",           "Catégorie :"),
            ("annee_publication",   "Année de publication :"),
            ("quantite_disponible", "Quantité disponible :"),
        ]

        self.inputs = {}

        for nom, label in champs:
            ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_dim"],
                anchor="w",
            ).pack(padx=25, fill="x")

            entry = ctk.CTkEntry(
                card,
                fg_color=COLORS["bg_input"],
                border_color=COLORS["border"],
                text_color=COLORS["text"],
                height=38,
                corner_radius=8,
            )
            entry.pack(padx=25, pady=(2, 10), fill="x")

            self.inputs[nom] = entry

        ctk.CTkLabel(
            card,
            text="Statut",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"],
            anchor="w",
        ).pack(padx=25, fill="x")

        self.statut_var = ctk.StringVar(value="disponible")
        self.option_statut = ctk.CTkOptionMenu(
            card,
            values=["disponible", "emprunté", "réservé"],
            variable=self.statut_var,
            fg_color=COLORS["bg_input"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent2"],
            text_color=COLORS["text"],
            height=38,
        )
        self.option_statut.pack(padx=25, pady=(2, 20), fill="x")

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(padx=25, fill="x", pady=(0, 20))

        ctk.CTkButton(
            btn_frame,
            text="➕  Ajouter",
            fg_color=COLORS["success"],
            hover_color="#3ab893",
            text_color="#000",
            corner_radius=10,
            height=40,
            command=self._ajouter_livre,
        ).pack(side="left", expand=True, padx=(0, 5))

        ctk.CTkButton(
            btn_frame,
            text="💾  Modifier",
            fg_color=COLORS["accent"],
            hover_color="#574fd6",
            corner_radius=10,
            height=40,
            command=self._modifier_livre,
        ).pack(side="left", expand=True, padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🗑  Supprimer",
            fg_color=COLORS["danger"],
            hover_color="#cc2233",
            corner_radius=10,
            height=40,
            command=self._supprimer_livre,
        ).pack(side="left", expand=True, padx=(5, 0))

        ctk.CTkButton(
            card,
            text="✖  Vider le formulaire",
            fg_color="transparent",
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_dim"],
            hover_color=COLORS["bg_input"],
            corner_radius=8,
            height=34,
            command=self._vider_formulaire,
        ).pack(padx=25, fill="x", pady=(0, 20))

        ctk.CTkLabel(
            card,
            text="🔍  Recherche",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text"],
        ).pack(padx=25, anchor="w")

        self.input_recherche = ctk.CTkEntry(
            card,
            placeholder_text="Titre, auteur ou ID…",
            fg_color=COLORS["bg_input"],
            border_color=COLORS["accent"],
            text_color=COLORS["text"],
            height=38,
        )
        self.input_recherche.pack(padx=25, pady=(5, 8), fill="x")

        ctk.CTkButton(
            card,
            text="Rechercher",
            fg_color=COLORS["accent"],
            hover_color="#574fd6",
            corner_radius=8,
            height=36,
            command=self._rechercher,
        ).pack(padx=25, fill="x", pady=(0, 20))

    def _build_liste(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=16)
        card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text="  Liste des Livres",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        self.label_count = ctk.CTkLabel(
            header,
            text="0 livre(s)",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"],
        )
        self.label_count.pack(side="right")

        self.scroll_frame = ctk.CTkScrollableFrame(
            card,
            fg_color="transparent",
            scrollbar_button_color=COLORS["accent"],
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 15))

    def _lire_inputs(self) -> dict:
        return {
            "titre":               self.inputs["titre"].get().strip(),
            "auteur":              self.inputs["auteur"].get().strip(),
            "categorie":           self.inputs["categorie"].get().strip(),
            "annee_publication":   self.inputs["annee_publication"].get().strip(),
            "quantite_disponible": self.inputs["quantite_disponible"].get().strip(),
            "statut":              self.statut_var.get(),
        }

    def _ajouter_livre(self):
        data = self._lire_inputs()

        if not data["titre"] or not data["auteur"]:
            messagebox.showerror("Erreur", "Le titre et l'auteur sont obligatoires !")
            return

        nouveau_livre = {
            "id_livre":            prochain_id(self.livres),
            "titre":               data["titre"],
            "auteur":              data["auteur"],
            "categorie":           data["categorie"] or "Non définie",
            "annee_publication":   data["annee_publication"] or "—",
            "quantite_disponible": data["quantite_disponible"] or "1",
            "statut":              data["statut"],
        }

        self.livres.append(nouveau_livre)
        sauvegarder_livres(self.livres)
        self._vider_formulaire()
        self._rafraichir_liste()
        messagebox.showinfo("Succès", f"✅ « {nouveau_livre['titre']} » ajouté !")

    def _modifier_livre(self):
        if self.id_selectionne is None:
            messagebox.showwarning("Attention", "Sélectionnez d'abord un livre dans la liste.")
            return

        data = self._lire_inputs()
        if not data["titre"] or not data["auteur"]:
            messagebox.showerror("Erreur", "Titre et auteur obligatoires !")
            return

        for livre in self.livres:
            if livre["id_livre"] == self.id_selectionne:
                livre.update({
                    "titre":               data["titre"],
                    "auteur":              data["auteur"],
                    "categorie":           data["categorie"],
                    "annee_publication":   data["annee_publication"],
                    "quantite_disponible": data["quantite_disponible"],
                    "statut":              data["statut"],
                })
                break

        sauvegarder_livres(self.livres)
        self._vider_formulaire()
        self._rafraichir_liste()
        messagebox.showinfo("Succès", "✅ Livre modifié avec succès !")

    def _supprimer_livre(self):
        if self.id_selectionne is None:
            messagebox.showwarning("Attention", "Sélectionnez d'abord un livre.")
            return

        if not messagebox.askyesno("Confirmer", "Supprimer ce livre définitivement ?"):
            return

        self.livres = [l for l in self.livres if l["id_livre"] != self.id_selectionne]
        sauvegarder_livres(self.livres)
        self._vider_formulaire()
        self._rafraichir_liste()

    def _rechercher(self):
        terme = self.input_recherche.get().strip().lower()
        if not terme:
            self._rafraichir_liste()
            return

        resultats = [
            l for l in self.livres
            if terme in l["titre"].lower()
            or terme in l["auteur"].lower()
            or terme == str(l["id_livre"])
        ]
        self._rafraichir_liste(resultats)

    def _rafraichir_liste(self, livres: list = None):
        source = livres if livres is not None else self.livres

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.label_count.configure(text=f"{len(source)} livre(s)")

        if not source:
            ctk.CTkLabel(
                self.scroll_frame,
                text="Aucun livre trouvé",
                text_color=COLORS["text_dim"],
                font=ctk.CTkFont(size=14),
            ).pack(pady=40)
            return

        for livre in source:
            self._creer_carte_livre(livre)

    def _creer_carte_livre(self, livre: dict):
        couleur_statut = {
            "disponible": COLORS["success"],
            "emprunté":   COLORS["accent2"],
            "réservé":    "#ffa502",
        }.get(livre["statut"], COLORS["text_dim"])

        carte = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=COLORS["bg_input"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        carte.pack(fill="x", padx=5, pady=5)

        ligne1 = ctk.CTkFrame(carte, fg_color="transparent")
        ligne1.pack(fill="x", padx=15, pady=(12, 2))

        ctk.CTkLabel(
            ligne1,
            text=f"#{livre['id_livre']}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["accent"],
            width=30,
        ).pack(side="left")

        ctk.CTkLabel(
            ligne1,
            text=livre["titre"],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left", padx=8)

        ctk.CTkLabel(
            ligne1,
            text=f"  {livre['statut']}  ",
            font=ctk.CTkFont(size=10),
            text_color="#000",
            fg_color=couleur_statut,
            corner_radius=6,
        ).pack(side="right")

        ctk.CTkLabel(
            carte,
            text=f" {livre['auteur']}   |    {livre['categorie']}   |    {livre['annee_publication']}   |    {livre['quantite_disponible']}",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_dim"],
        ).pack(anchor="w", padx=15, pady=(0, 12))

        carte.bind("<Button-1>", lambda e, l=livre: self._charger_dans_formulaire(l))
        for child in carte.winfo_children():
            child.bind("<Button-1>", lambda e, l=livre: self._charger_dans_formulaire(l))
            for sub in child.winfo_children():
                sub.bind("<Button-1>", lambda e, l=livre: self._charger_dans_formulaire(l))

    def _charger_dans_formulaire(self, livre: dict):
        self.id_selectionne = livre["id_livre"]
        self._vider_formulaire(reset_id=False)

        self.inputs["titre"].insert(0, livre["titre"])
        self.inputs["auteur"].insert(0, livre["auteur"])
        self.inputs["categorie"].insert(0, livre["categorie"])
        self.inputs["annee_publication"].insert(0, livre["annee_publication"])
        self.inputs["quantite_disponible"].insert(0, livre["quantite_disponible"])
        self.statut_var.set(livre["statut"])

    def _vider_formulaire(self, reset_id=True):
        for entry in self.inputs.values():
            entry.delete(0, "end")
        self.statut_var.set("disponible")
        if reset_id:
            self.id_selectionne = None


if __name__ == "__main__":
    app = BibliothequeApp()
    app.mainloop()
