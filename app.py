from flask import Flask, render_template, jsonify, request
from database.DatabaseWrapper import DatabaseWrapper
import true_skill_calculator
from models.player import Player
from models.game import Game
from models.score import Score
from models.team import Team
from bson import json_util, ObjectId
import json

app = Flask(__name__)

db_wrap = DatabaseWrapper()

@app.route("/")
def home():
    """
    Render the home page.
    Returns the rendered HTML template.
    """
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
    
    messaggio_di_successo = {"status": "OK", "message": "Player added successfully"}
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
    Add the game to the database, and update player scores.
    Returns a success message.
    """
    data = json_util.loads(request.data)
    game = Game(**data)

    # Add the game to the database
    db_wrap.addGame(game)

    # Calculate the new skill ratings for players after the game
    new_scores = true_skill_calculator.calculate_skill_after_game(game)

    # Update the players' scores in the database
    db_wrap.updatePlayerScore(game.redDefPlayer, new_scores[0], isDefScore=True)
    db_wrap.updatePlayerScore(game.redAtkPlayer, new_scores[1], isDefScore=False)
    db_wrap.updatePlayerScore(game.blueDefPlayer, new_scores[2], isDefScore=True)
    db_wrap.updatePlayerScore(game.blueAtkPlayer, new_scores[3], isDefScore=False)
    print("Game added and players' scores updated successfully.")

    # Return a success message
    return jsonify({"status": "OK", "message": "Game added successfully"})

@app.route('/get-games', methods=['GET'])
def get_games():
    """
    Endpoint to retrieve all games from the database.
    Returns a JSON list of games with player names and scores.
    """
    print("Fetching all games from the database...")
    games = db_wrap.getAllGames()
    if not games:
        return jsonify({"status": "OK", "games": []})
    
    return json.loads(json_util.dumps(games))

# # @app.route('/get-player-score/<player_id>', methods=['GET'])
# @app.route('?player_id=<player_id>', methods=['GET'])
# def get_player_score(player_id):
#     """
#     Endpoint to retrieve all games from the database.
#     Returns a JSON list of games with player names and scores.
#     """
#     print("Prova delle cose" + player_id)
 
    
#     # Return a success message
#     return jsonify({"status": "OK", "message": "Game added successfully"})


@app.route('/game-win-rate', methods=['POST'])
def game_win_rate():
    """
    Calculate the win rate of team1 against team2.
    Returns the win rate as a float [0, 1].
    """
    data = request.get_json()
    team1 = Team(**data['team1'])
    team2 = Team(**data['team2'])

    win_rate = true_skill_calculator.calculate_win_rate(team1, team2)
    return jsonify({'win_rate': win_rate})


@app.route('/player-profile/<player_id>', methods=['GET'])
def player_profile(player_id):
    """
    Endpoint to retrieve a player's profile by their ID.
    Returns a JSON object with the player's details and scores.
    """
    player = db_wrap.getPlayerById(player_id)
    if not player:
        return jsonify({"status": "Error", "message": "Player not found"})
    
    return json.loads(json_util.dumps(player))


if __name__ == "__main__":
    player1 = Player(name="Player1", last_name="One")
    player2 = Player(name="Player2", last_name="Two")
    player3 = Player(name="Player3", last_name="Three")
    player4 = Player(name="Player4", last_name="Four")
    game = Game(redDefPlayer=player1, redAtkPlayer=player2, blueDefPlayer=player3, blueAtkPlayer=player4, winnerTeamColor="red")

    app.run(debug=True)
