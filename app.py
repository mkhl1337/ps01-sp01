from flask import Flask, request, jsonify
import sqlite3
import hashlib

app = Flask(__name__)
DB = "bdbib.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS utilisateur (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            nom          TEXT NOT NULL,
            prenom       TEXT NOT NULL,
            email        TEXT UNIQUE NOT NULL,
            mot_de_passe TEXT NOT NULL,
            role         TEXT DEFAULT 'user'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS livre (
            id_livre            INTEGER PRIMARY KEY AUTOINCREMENT,
            titre               TEXT NOT NULL,
            auteur              TEXT NOT NULL,
            categorie           TEXT DEFAULT 'Non définie',
            annee_publication   TEXT DEFAULT '—',
            quantite_disponible INTEGER DEFAULT 1,
            statut              TEXT DEFAULT 'disponible'
        )
    """)

    cur.execute("SELECT COUNT(*) FROM utilisateur")
    if cur.fetchone()[0] == 0:
        mdp = hashlib.sha256("admin123".encode()).hexdigest()
        cur.execute(
            "INSERT INTO utilisateur (nom, prenom, email, mot_de_passe, role) VALUES (?,?,?,?,?)",
            ("Admin", "Système", "admin@biblio.com", mdp, "admin")
        )

    conn.commit()
    conn.close()


# ─── LOGIN ─────────────────────────────────────────────────────────

@app.route("/login", methods=["POST"])
def login():
    data  = request.get_json()
    email = data.get("email", "").strip()
    mdp   = data.get("mot_de_passe", "")

    if not email or not mdp:
        return jsonify({"success": False, "message": "Champs manquants"}), 400

    mdp_hash = hashlib.sha256(mdp.encode()).hexdigest()
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "SELECT id, nom, prenom, role FROM utilisateur WHERE email=? AND mot_de_passe=?",
        (email, mdp_hash)
    )
    row = cur.fetchone()
    conn.close()

    if row:
        return jsonify({
            "success": True,
            "utilisateur": {
                "id":     row["id"],
                "nom":    row["nom"],
                "prenom": row["prenom"],
                "role":   row["role"]
            }
        })
    else:
        return jsonify({"success": False, "message": "Email ou mot de passe incorrect"}), 401


# ─── LIVRES : LIRE TOUS ────────────────────────────────────────────

@app.route("/livres", methods=["GET"])
def get_livres():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM livre")
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


# ─── LIVRES : RECHERCHER ───────────────────────────────────────────

@app.route("/livres/recherche", methods=["GET"])
def rechercher_livres():
    terme = request.args.get("q", "").strip()
    conn  = get_db()
    cur   = conn.cursor()
    cur.execute("""
        SELECT * FROM livre
        WHERE titre  LIKE ?
        OR    auteur LIKE ?
        OR    CAST(id_livre AS TEXT) = ?
    """, (f"%{terme}%", f"%{terme}%", terme))
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


# ─── LIVRES : AJOUTER ─────────────────────────────────────────────

@app.route("/livres", methods=["POST"])
def ajouter_livre():
    data = request.get_json()

    titre  = data.get("titre", "").strip()
    auteur = data.get("auteur", "").strip()

    if not titre or not auteur:
        return jsonify({"success": False, "message": "Titre et auteur obligatoires"}), 400

    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO livre (titre, auteur, categorie, annee_publication, quantite_disponible, statut)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        titre,
        auteur,
        data.get("categorie", "Non définie"),
        data.get("annee_publication", "—"),
        data.get("quantite_disponible", 1),
        data.get("statut", "disponible"),
    ))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return jsonify({"success": True, "id_livre": new_id}), 201


# ─── LIVRES : MODIFIER ────────────────────────────────────────────

@app.route("/livres/<int:id_livre>", methods=["PUT"])
def modifier_livre(id_livre):
    data = request.get_json()

    titre  = data.get("titre", "").strip()
    auteur = data.get("auteur", "").strip()

    if not titre or not auteur:
        return jsonify({"success": False, "message": "Titre et auteur obligatoires"}), 400

    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        UPDATE livre
        SET titre=?, auteur=?, categorie=?, annee_publication=?, quantite_disponible=?, statut=?
        WHERE id_livre=?
    """, (
        titre,
        auteur,
        data.get("categorie", "Non définie"),
        data.get("annee_publication", "—"),
        data.get("quantite_disponible", 1),
        data.get("statut", "disponible"),
        id_livre,
    ))
    conn.commit()
    conn.close()

    return jsonify({"success": True})


# ─── LIVRES : SUPPRIMER ───────────────────────────────────────────

@app.route("/livres/<int:id_livre>", methods=["DELETE"])
def supprimer_livre(id_livre):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("DELETE FROM livre WHERE id_livre=?", (id_livre,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


# ─── POINT D'ENTRÉE ───────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
