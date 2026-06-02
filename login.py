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
    "text":     "#e8e8f0",
    "text_dim": "#8888aa",
    "danger":   "#ff4757",
    "border":   "#2e3150",
}


class LoginWindow(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Bibliothèque — Connexion")
        self.geometry("460x580")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_main"])
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="📚", font=ctk.CTkFont(size=54)).pack(pady=(45, 0))

        ctk.CTkLabel(
            self,
            text="Bibliothèque Intelligente",
            font=ctk.CTkFont(family="Georgia", size=22, weight="bold"),
            text_color=COLORS["accent"],
        ).pack(pady=(8, 2))

        ctk.CTkLabel(
            self,
            text="Connectez-vous pour continuer",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_dim"],
        ).pack(pady=(0, 28))

        card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=16)
        card.pack(padx=40, fill="x")

        ctk.CTkLabel(
            card, text="Adresse e-mail",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"], anchor="w",
        ).pack(padx=30, pady=(25, 3), fill="x")

        self.entry_email = ctk.CTkEntry(
            card,
            placeholder_text="exemple@email.com",
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            height=44, corner_radius=10,
        )
        self.entry_email.pack(padx=30, fill="x")

        ctk.CTkLabel(
            card, text="Mot de passe",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"], anchor="w",
        ).pack(padx=30, pady=(16, 3), fill="x")

        self.entry_mdp = ctk.CTkEntry(
            card,
            placeholder_text="••••••••",
            show="•",
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            height=44, corner_radius=10,
        )
        self.entry_mdp.pack(padx=30, fill="x")

        self.btn_cnx = ctk.CTkButton(
            card,
            text="Se connecter",
            fg_color=COLORS["accent"],
            hover_color="#574fd6",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=46, corner_radius=10,
            command=self._connexion,
        )
        self.btn_cnx.pack(padx=30, pady=(22, 28), fill="x")

        self.label_erreur = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["danger"],
        )
        self.label_erreur.pack(pady=(14, 0))

        ctk.CTkLabel(
            self,
            text="Compte démo :  admin@biblio.com  /  admin123",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_dim"],
        ).pack(pady=(18, 0))

        self.entry_email.bind("<Return>", lambda e: self.entry_mdp.focus())
        self.entry_mdp.bind("<Return>",  lambda e: self._connexion())

    def _valider_champs(self):
        email = self.entry_email.get().strip()
        mdp   = self.entry_mdp.get()
        if not email and not mdp:
            return "⚠  Veuillez remplir tous les champs."
        if not email:
            return "⚠  L'adresse e-mail est obligatoire."
        if "@" not in email or "." not in email:
            return "⚠  Format d'e-mail invalide."
        if not mdp:
            return "⚠  Le mot de passe est obligatoire."
        if len(mdp) < 4:
            return "⚠  Le mot de passe est trop court."
        return None

    def _connexion(self):
        self.label_erreur.configure(text="")

        erreur = self._valider_champs()
        if erreur:
            self.label_erreur.configure(text=erreur)
            return

        email = self.entry_email.get().strip()
        mdp   = self.entry_mdp.get()

        self.btn_cnx.configure(text="Connexion…", state="disabled")

        erreur_msg  = None
        utilisateur = None

        try:
            reponse = requests.post(
                f"{API_URL}/login",
                json={"email": email, "mot_de_passe": mdp},
                timeout=5,
            )
            data = reponse.json()

            if data.get("success"):
                utilisateur = data["utilisateur"]
            else:
                erreur_msg = f"❌  {data.get('message', 'Erreur inconnue')}"

        except requests.exceptions.ConnectionError:
            erreur_msg = "❌  Impossible de joindre le serveur Flask."
        except Exception as ex:
            erreur_msg = f"❌  Erreur : {ex}"

        if utilisateur:
            self.destroy()
            from front import MainApp
            MainApp(utilisateur).mainloop()
        else:
            self.label_erreur.configure(text=erreur_msg)
            self.entry_mdp.delete(0, "end")
            self.btn_cnx.configure(text="Se connecter", state="normal")


if __name__ == "__main__":
    LoginWindow().mainloop()
