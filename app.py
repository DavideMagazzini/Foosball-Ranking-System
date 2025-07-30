from flask import Flask, render_template, jsonify
from database.DatabaseWrapper import DatabaseWrapper
from models.player import Player
app = Flask(__name__)

db_wrap = DatabaseWrapper()

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/esegui-azione', methods=['POST'])
def esegui_azione():
    # Il tuo codice Python viene eseguito qui
    print("Pulsante premuto! Eseguo la funzione Python tramite JavaScript.")
    db_wrap.addPlayer(Player('Prima', 'Prova'))
    
    messaggio_di_successo = {"status": "OK", "messaggio": "Azione eseguita con successo!"}
    return jsonify(messaggio_di_successo)

if __name__ == "__main__":
    app.run(debug=True)