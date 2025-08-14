from flask import Flask, render_template, jsonify, request
from database.DatabaseWrapper import DatabaseWrapper
from models.player import Player
from models.game import Game
from bson import json_util, ObjectId
import json

app = Flask(__name__)

db_wrap = DatabaseWrapper()

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/add-player', methods=['POST'])
def add_player():
    """
    Endpoint to add a new player to the database.
    Expects JSON data with 'playerName' and 'playerLastName'.
    """
    data = request.get_json()
    name = data.get('playerName')
    last_name = data.get('playerLastName')

    db_wrap.addPlayer(Player(name=name, last_name=last_name))
    
    messaggio_di_successo = {"status": "OK", "message": "Player addedd successfully"}
    return jsonify(messaggio_di_successo)

@app.route('/get-players', methods=['GET'])
def get_players():
    """
    Endpoint to retrieve all players from the database.
    Returns a JSON list of players names and last names.
    """
    print("Fetching all players from the database...")
    players = db_wrap.getAllPlayers()
    if not players:
        return jsonify({"status": "OK", "players": []})
    
    return json.loads(json_util.dumps(players))

@app.route('/get-players-ranks', methods=['GET'])
def get_players_ranks():
    """
    Endpoint to retrieve all players scores from the database.
    Returns a JSON list of players names, last names and ranks.
    """
    print("Fetching all players from the database...")
    players = db_wrap.getAllPlayers()
    if not players:
        return jsonify({"status": "OK", "players": []})
    
    return jsonify([{'name': player['name'], 
                    'last_name': player['last_name'], 
                    'def_rank': player['def_score']['rank'],
                    'atk_rank': player['atk_score']['rank']} for player in players])

@app.route('/add-game', methods=['POST'])
def add_game():
    """
    Add the game to the database

    """
    data = request.get_json()
    game = Game(redDefPlayer=Player(_id=ObjectId(data['redDefPlayer']['_id']['$oid']),
                                    name=data['redDefPlayer']['name'], 
                                    last_name=data['redDefPlayer']['last_name'],
                                    def_score=data['redDefPlayer']['def_score'],
                                    atk_score=data['redDefPlayer']['atk_score']),
                redAtkPlayer=Player(_id=ObjectId(data['redAtkPlayer']['_id']['$oid']),
                                    name=data['redAtkPlayer']['name'], 
                                    last_name=data['redAtkPlayer']['last_name'],
                                    def_score=data['redAtkPlayer']['def_score'],
                                    atk_score=data['redAtkPlayer']['atk_score']),
                blueDefPlayer=Player(_id=ObjectId(data['blueDefPlayer']['_id']['$oid']),
                                    name=data['blueDefPlayer']['name'],
                                    last_name=data['blueDefPlayer']['last_name'],
                                    def_score=data['blueDefPlayer']['def_score'],
                                    atk_score=data['blueDefPlayer']['atk_score']),
                blueAtkPlayer=Player(_id=ObjectId(data['blueAtkPlayer']['_id']['$oid']),
                                    name=data['blueAtkPlayer']['name'], 
                                    last_name=data['blueAtkPlayer']['last_name'],
                                    def_score=data['blueAtkPlayer']['def_score'],
                                    atk_score=data['blueAtkPlayer']['atk_score']),
                winnerTeamColor=data['winnerTeamColor'])
    print(game)
    db_wrap.addGame(game)
    return jsonify({"status": "OK", "message": "Game added successfully"})


if __name__ == "__main__":
    app.run(debug=True)
