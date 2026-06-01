import customtkinter as ctk
import requests
from tkinter import messagebox

API_URL = "http://127.0.0.1:5000"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg_main":  "#0f1117",
    "bg_card":  "#1a1d2e",
    "bg_input": "#252840",
    "accent":   "#6c63ff",
    "accent2":  "#ff6584",
    "text":     "#e8e8f0",
    "text_dim": "#8888aa",
    "success":  "#4ecca3",
    "danger":   "#ff4757",
    "border":   "#2e3150",
    "header":   "#12152a",
    "row_even": "#1e2138",
    "row_odd":  "#1a1d2e",
    "row_hover":"#2a2d4a",
}

COLONNES = [
    ("id_livre",            "ID",         50),
    ("titre",               "Titre",     220),
    ("auteur",              "Auteur",    160),
    ("categorie",           "Catégorie", 120),
    ("annee_publication",   "Année",      70),
    ("quantite_disponible", "Qté",        50),
    ("statut",              "Statut",    110),
    ("actions",             "Actions",   130),
]


class MainApp(ctk.CTk):

    def __init__(self, utilisateur: dict):
        super().__init__()
        self.utilisateur    = utilisateur
        self.livres         = []
        self.sort_col       = None
        self.sort_asc       = True
        self.title("📚 Bibliothèque Intelligente")
        self.geometry("1280x750")
        self.configure(fg_color=COLORS["bg_main"])
        self._build_topbar()
        self._build_body()
        self._charger_livres()

    # ── TOPBAR ─────────────────────────────────────────────────────

    def _build_topbar(self):
        bar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=58)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        ctk.CTkLabel(
            bar,
            text="📚  Bibliothèque Intelligente",
            font=ctk.CTkFont(family="Georgia", size=18, weight="bold"),
            text_color=COLORS["accent"],
        ).pack(side="left", padx=25)

        ctk.CTkButton(
            bar, text="⎋  Déconnexion",
            fg_color="transparent", border_color=COLORS["border"],
            border_width=1, text_color=COLORS["text_dim"],
            hover_color=COLORS["bg_input"], width=130, height=32,
            corner_radius=8, command=self._deconnexion,
        ).pack(side="right", padx=20)

        nom = f"{self.utilisateur['prenom']} {self.utilisateur['nom']}"
        ctk.CTkLabel(
            bar, text=f"👤  {nom}  •  {self.utilisateur['role']}",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_dim"],
        ).pack(side="right", padx=10)

    # ── BODY ───────────────────────────────────────────────────────

    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=25, pady=20)

        # Barre outils
        toolbar = ctk.CTkFrame(body, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 12))

        ctk.CTkButton(
            toolbar, text="➕  Ajouter un livre",
            fg_color=COLORS["success"], hover_color="#3ab893",
            text_color="#000", height=38, corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._popup_ajouter,
        ).pack(side="left")

        # Recherche
        self.input_recherche = ctk.CTkEntry(
            toolbar,
            placeholder_text="🔍  Rechercher titre, auteur, ID…",
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            text_color=COLORS["text"], height=38, width=280,
        )
        self.input_recherche.pack(side="right", padx=(10, 0))
        self.input_recherche.bind("<KeyRelease>", lambda e: self._rechercher())

        # Carte tableau
        card = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=14)
        card.pack(fill="both", expand=True)

        # En-têtes colonnes
        self._build_headers(card)

        # Zone scrollable lignes
        self.scroll = ctk.CTkScrollableFrame(
            card, fg_color="transparent",
            scrollbar_button_color=COLORS["accent"],
        )
        self.scroll.pack(fill="both", expand=True, padx=2, pady=(0, 2))

        # Configurer les colonnes du scroll
        for i, (_, _, w) in enumerate(COLONNES):
            self.scroll.columnconfigure(i, minsize=w)

    def _build_headers(self, parent):
        header_frame = ctk.CTkFrame(parent, fg_color=COLORS["header"], corner_radius=0, height=42)
        header_frame.pack(fill="x", padx=2, pady=(2, 0))
        header_frame.pack_propagate(False)

        for i, (col, label, width) in enumerate(COLONNES):
            is_sortable = col != "actions"
            text = label if not is_sortable else label

            btn = ctk.CTkButton(
                header_frame,
                text=text,
                fg_color="transparent",
                hover_color=COLORS["bg_input"] if is_sortable else COLORS["header"],
                text_color=COLORS["accent"] if is_sortable else COLORS["text_dim"],
                font=ctk.CTkFont(size=12, weight="bold"),
                width=width, height=42, corner_radius=0,
                cursor="hand2" if is_sortable else "arrow",
                command=(lambda c=col: self._trier(c)) if is_sortable else None,
            )
            btn.pack(side="left")
            setattr(self, f"header_{col}", btn)

    # ── CHARGEMENT & AFFICHAGE ─────────────────────────────────────

    def _charger_livres(self):
        try:
            r = requests.get(f"{API_URL}/livres", timeout=5)
            self.livres = r.json()
            self._afficher(self.livres)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les livres.\n{e}")

    def _afficher(self, livres: list):
        for w in self.scroll.winfo_children():
            w.destroy()

        if not livres:
            ctk.CTkLabel(
                self.scroll, text="Aucun livre trouvé.",
                text_color=COLORS["text_dim"], font=ctk.CTkFont(size=14),
            ).grid(row=0, column=0, columnspan=len(COLONNES), pady=40)
            return

        for i, livre in enumerate(livres):
            self._ligne(livre, i)

    def _ligne(self, livre: dict, index: int):
        bg = COLORS["row_even"] if index % 2 == 0 else COLORS["row_odd"]

        couleur_statut = {
            "disponible": COLORS["success"],
            "emprunté":   COLORS["accent2"],
            "réservé":    "#ffa502",
        }.get(livre["statut"], COLORS["text_dim"])

        valeurs = [
            str(livre["id_livre"]),
            livre["titre"],
            livre["auteur"],
            livre["categorie"],
            str(livre["annee_publication"]),
            str(livre["quantite_disponible"]),
        ]

        for j, (val, (col, _, width)) in enumerate(zip(valeurs, COLONNES)):
            cell = ctk.CTkLabel(
                self.scroll, text=val,
                fg_color=bg, text_color=COLORS["text"],
                font=ctk.CTkFont(size=12),
                width=width, height=38, anchor="w",
                padx=8, corner_radius=0,
            )
            cell.grid(row=index, column=j, sticky="nsew", padx=1, pady=1)

        # Statut badge
        statut_label = ctk.CTkLabel(
            self.scroll, text=f"  {livre['statut']}  ",
            fg_color=couleur_statut, text_color="#000",
            font=ctk.CTkFont(size=10),
            width=COLONNES[6][2], height=38, corner_radius=6,
        )
        statut_label.grid(row=index, column=6, padx=4, pady=4)

        # Boutons actions
        action_frame = ctk.CTkFrame(self.scroll, fg_color=bg, corner_radius=0)
        action_frame.grid(row=index, column=7, sticky="nsew", padx=1, pady=1)

        ctk.CTkButton(
            action_frame, text="✏️",
            fg_color=COLORS["accent"], hover_color="#574fd6",
            width=44, height=28, corner_radius=6,
            command=lambda l=livre: self._popup_modifier(l),
        ).pack(side="left", padx=(6, 3), pady=5)

        ctk.CTkButton(
            action_frame, text="🗑",
            fg_color=COLORS["danger"], hover_color="#cc2233",
            width=44, height=28, corner_radius=6,
            command=lambda l=livre: self._supprimer(l),
        ).pack(side="left", padx=(3, 6), pady=5)

    # ── TRI ────────────────────────────────────────────────────────

    def _trier(self, col: str):
        if self.sort_col == col:
            self.sort_asc = not self.sort_asc
        else:
            self.sort_col = col
            self.sort_asc = True

        # Remet les labels des headers
        for c, label, _ in COLONNES:
            btn = getattr(self, f"header_{c}", None)
            if btn:
                if c == col:
                    fleche = " ▲" if self.sort_asc else " ▼"
                    btn.configure(text=label + fleche, text_color=COLORS["success"])
                else:
                    btn.configure(text=label, text_color=COLORS["accent"])

        reverse = not self.sort_asc
        try:
            sorted_livres = sorted(
                self.livres,
                key=lambda l: str(l.get(col, "")).lower(),
                reverse=reverse,
            )
        except Exception:
            sorted_livres = self.livres

        self._afficher(sorted_livres)

    # ── RECHERCHE ──────────────────────────────────────────────────

    def _rechercher(self):
        terme = self.input_recherche.get().strip().lower()
        if not terme:
            self._afficher(self.livres)
            return
        resultats = [
            l for l in self.livres
            if terme in l["titre"].lower()
            or terme in l["auteur"].lower()
            or terme == str(l["id_livre"])
        ]
        self._afficher(resultats)

    # ── POPUP AJOUTER ──────────────────────────────────────────────

    def _popup_ajouter(self):
        popup = PopupLivre(self, titre_popup="➕  Ajouter un livre")
        self.wait_window(popup)
        if popup.resultat:
            try:
                r = requests.post(f"{API_URL}/livres", json=popup.resultat, timeout=5)
                if r.json().get("success"):
                    messagebox.showinfo("Succès", "✅ Livre ajouté !")
                    self._charger_livres()
                else:
                    messagebox.showerror("Erreur", r.json().get("message"))
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    # ── POPUP MODIFIER ─────────────────────────────────────────────

    def _popup_modifier(self, livre: dict):
        popup = PopupLivre(self, titre_popup="💾  Modifier le livre", livre=livre)
        self.wait_window(popup)
        if popup.resultat:
            try:
                r = requests.put(f"{API_URL}/livres/{livre['id_livre']}", json=popup.resultat, timeout=5)
                if r.json().get("success"):
                    messagebox.showinfo("Succès", "✅ Livre modifié !")
                    self._charger_livres()
                else:
                    messagebox.showerror("Erreur", r.json().get("message"))
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    # ── SUPPRIMER ──────────────────────────────────────────────────

    def _supprimer(self, livre: dict):
        if not messagebox.askyesno("Confirmer", f"Supprimer « {livre['titre']} » définitivement ?"):
            return
        try:
            r = requests.delete(f"{API_URL}/livres/{livre['id_livre']}", timeout=5)
            if r.json().get("success"):
                self._charger_livres()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    # ── DÉCONNEXION ────────────────────────────────────────────────

    def _deconnexion(self):
        self.destroy()
        from login import LoginWindow
        LoginWindow().mainloop()




class PopupLivre(ctk.CTkToplevel):

    def __init__(self, parent, titre_popup: str, livre: dict = None):
        super().__init__(parent)
        self.title(titre_popup)
        self.geometry("460x640")
        self.resizable(False, True)
        self.configure(fg_color=COLORS["bg_main"])
        self.grab_set()
        self.resultat = None
        self.livre    = livre
        self._build(titre_popup)
        self.after(100, self._centrer)

    def _centrer(self):
        self.update_idletasks()
        px = self.master.winfo_x() + self.master.winfo_width()  // 2 - 220
        py = self.master.winfo_y() + self.master.winfo_height() // 2 - 320
        self.geometry(f"460x640+{px}+{py}")

    def _build(self, titre_popup):
        ctk.CTkLabel(
            self, text=titre_popup,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["accent"],
        ).pack(pady=(25, 20))

        card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=14)
        card.pack(padx=30, fill="x")

        champs = [
            ("titre",               "Titre *"),
            ("auteur",              "Auteur *"),
            ("categorie",           "Catégorie"),
            ("annee_publication",   "Année de publication"),
            ("quantite_disponible", "Quantité disponible"),
        ]

        self.inputs = {}

        for nom, label in champs:
            ctk.CTkLabel(
                card, text=label,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_dim"], anchor="w",
            ).pack(padx=20, pady=(8, 2), fill="x")

            entry = ctk.CTkEntry(
                card,
                fg_color=COLORS["bg_input"],
                border_color=COLORS["border"],
                text_color=COLORS["text"],
                height=38, corner_radius=8,
            )
            entry.pack(padx=20, fill="x")
            self.inputs[nom] = entry

        ctk.CTkLabel(
            card, text="Statut",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"], anchor="w",
        ).pack(padx=20, pady=(8, 2), fill="x")

        self.statut_var = ctk.StringVar(value="disponible")
        ctk.CTkOptionMenu(
            card,
            values=["disponible", "emprunté", "réservé"],
            variable=self.statut_var,
            fg_color=COLORS["bg_input"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent2"],
            text_color=COLORS["text"],
            height=38,
        ).pack(padx=20, pady=(2, 20), fill="x")

        # Pré-remplir si modification
        if self.livre:
            self.inputs["titre"].insert(0, self.livre["titre"])
            self.inputs["auteur"].insert(0, self.livre["auteur"])
            self.inputs["categorie"].insert(0, self.livre["categorie"])
            self.inputs["annee_publication"].insert(0, str(self.livre["annee_publication"]))
            self.inputs["quantite_disponible"].insert(0, str(self.livre["quantite_disponible"]))
            self.statut_var.set(self.livre["statut"])

        # Boutons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(padx=30, fill="x", pady=20)

        ctk.CTkButton(
            btn_frame, text="Annuler",
            fg_color="transparent", border_color=COLORS["border"],
            border_width=1, text_color=COLORS["text_dim"],
            hover_color=COLORS["bg_input"], height=40, corner_radius=10,
            command=self.destroy,
        ).pack(side="left", expand=True, padx=(0, 8))

        label_btn = "Ajouter" if not self.livre else "Enregistrer"
        ctk.CTkButton(
            btn_frame, text=label_btn,
            fg_color=COLORS["accent"], hover_color="#574fd6",
            height=40, corner_radius=10,
            font=ctk.CTkFont(weight="bold"),
            command=self._valider,
        ).pack(side="left", expand=True)

    def _valider(self):
        titre  = self.inputs["titre"].get().strip()
        auteur = self.inputs["auteur"].get().strip()

        if not titre or not auteur:
            messagebox.showerror("Erreur", "Titre et auteur sont obligatoires !", parent=self)
            return

        self.resultat = {
            "titre":               titre,
            "auteur":              auteur,
            "categorie":           self.inputs["categorie"].get().strip() or "Non définie",
            "annee_publication":   self.inputs["annee_publication"].get().strip() or "—",
            "quantite_disponible": self.inputs["quantite_disponible"].get().strip() or "1",
            "statut":              self.statut_var.get(),
        }
        self.destroy()


if __name__ == "__main__":
    utilisateur = {"id": 1, "nom": "Admin", "prenom": "Système", "role": "admin"}
    MainApp(utilisateur).mainloop()
