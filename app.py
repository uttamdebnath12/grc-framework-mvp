from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# ---------- DATABASE ----------
def get_db_connection():
    conn = sqlite3.connect("grc.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/init-db")
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER,
            likelihood INTEGER,
            impact INTEGER,
            score INTEGER,
            level TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS controls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            standard TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compliance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            control_id INTEGER,
            regulation TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()
    return "Database initialized"

# ---------- HOME ----------

@app.route("/")
def home():
    conn = get_db_connection()

    total_assets = conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
    total_risks = conn.execute("SELECT COUNT(*) FROM risks").fetchone()[0]

    high_risks = conn.execute(
        "SELECT COUNT(*) FROM risks WHERE level='High'"
    ).fetchone()[0]

    medium_risks = conn.execute(
        "SELECT COUNT(*) FROM risks WHERE level='Medium'"
    ).fetchone()[0]

    low_risks = conn.execute(
        "SELECT COUNT(*) FROM risks WHERE level='Low'"
    ).fetchone()[0]

    conn.close()


    return render_template(
        "index.html",
        total_assets=total_assets,
        total_risks=total_risks,
        high_risks=high_risks,
        medium_risks=medium_risks,
        low_risks=low_risks
    )


# ---------- ADD ASSET ----------
@app.route("/add-asset/<name>/<type>")
def add_asset(name, type):
    conn = get_db_connection()
    conn.execute("INSERT INTO assets (name, type) VALUES (?, ?)", (name, type))
    conn.commit()
    conn.close()
    return f"Asset added → {name} ({type})"

# ---------- ADD RISK ----------
@app.route("/add-risk/<int:asset_id>/<int:likelihood>/<int:impact>")
def add_risk(asset_id, likelihood, impact):
    score = likelihood * impact
    level = "Low" if score <= 2 else "Medium" if score <= 4 else "High"

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO risks (asset_id, likelihood, impact, score, level) VALUES (?, ?, ?, ?, ?)",
        (asset_id, likelihood, impact, score, level)
    )
    conn.commit()
    conn.close()
    return f"Risk saved → Asset {asset_id}, Score {score}, Level {level}"

# ---------- VIEW RISKS ----------
@app.route("/risks")
def view_risks():
    conn = get_db_connection()
    risks = conn.execute("""
        SELECT risks.id, assets.name, risks.score, risks.level
        FROM risks JOIN assets ON risks.asset_id = assets.id
    """).fetchall()
    conn.close()

    return render_template("risks.html", risks=risks)

# ---------- ADD CONTROL ----------
@app.route("/add-control/<name>/<standard>")
def add_control(name, standard):
    conn = get_db_connection()
    conn.execute("INSERT INTO controls (name, standard) VALUES (?, ?)", (name, standard))
    conn.commit()
    conn.close()
    return f"Control added → {name} ({standard})"

# ---------- ADD COMPLIANCE ----------
@app.route("/add-compliance/<int:control_id>/<regulation>/<status>")
def add_compliance(control_id, regulation, status):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO compliance (control_id, regulation, status) VALUES (?, ?, ?)",
        (control_id, regulation, status)
    )
    conn.commit()
    conn.close()

    return f"Compliance added → Control {control_id}, {regulation}, {status}"

@app.route("/delete-risk/<int:risk_id>")
def delete_risk(risk_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM risks WHERE id = ?", (risk_id,))
    conn.commit()
    conn.close()
    return f"Risk {risk_id} deleted successfully"

# ---------- MAP CONTROL TO REGULATION ----------
@app.route("/map-control/<int:control_id>/<regulation>")
def map_control(control_id, regulation):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO compliance (control_id, regulation, status) VALUES (?, ?, ?)",
        (control_id, regulation, "Compliant")
    )
    conn.commit()
    conn.close()
    return f"Control {control_id} mapped to {regulation}"

# ---------- VIEW COMPLIANCE ----------
@app.route("/compliance")
def view_compliance():
    conn = get_db_connection()
    compliance = conn.execute("""
        SELECT controls.name, controls.standard, compliance.regulation, compliance.status
        FROM compliance JOIN controls ON compliance.control_id = controls.id
    """).fetchall()
    conn.close()

    return render_template("compliance.html", compliance=compliance)

if __name__ == "__main__":
    app.run(debug=True)


