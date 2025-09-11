from flask import Flask, render_template, jsonify, request
from database.DatabaseWrapper import DatabaseWrapper
import true_skill_calculator
from models.player import Player
from models.game import Game
from models.stats import Stats
from models.team import Team
from bson import json_util, ObjectId
import json
from dataclasses import asdict
from datetime import datetime, timezone

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

    #TODO: the player has to be loaded from the database otherwise if someone else added
    # a game in the database before refreshing the page, the player given to this function
    # is not updated by that game

    # Update the game's players to avoid using old players docs
    game.redDefPlayer = db_wrap.getPlayerById(player_id=game.redDefPlayer._id)
    game.redAtkPlayer = db_wrap.getPlayerById(player_id=game.redAtkPlayer._id)
    game.blueDefPlayer = db_wrap.getPlayerById(player_id=game.blueDefPlayer._id)
    game.blueAtkPlayer = db_wrap.getPlayerById(player_id=game.blueAtkPlayer._id)


    # Add the game to the database
    db_wrap.addGame(game)


    # Calculate the new skill ratings for players after the game
    new_scores = true_skill_calculator.calculate_skill_after_game(game)

    # Update the players' scores in the database
    db_wrap.updatePlayerScore(game.redDefPlayer, new_scores[0], isDefScore=True)
    db_wrap.updatePlayerScore(game.redAtkPlayer, new_scores[1], isDefScore=False)
    db_wrap.updatePlayerScore(game.blueDefPlayer, new_scores[2], isDefScore=True)
    db_wrap.updatePlayerScore(game.blueAtkPlayer, new_scores[3], isDefScore=False)


    # Calculate the new stats for each player
    new_stats = calculate_stats_after_game(game=game)

    # Update players stats
    db_wrap.updatePlayerStats(playerId=game.redDefPlayer._id, new_stats=new_stats[0])
    db_wrap.updatePlayerStats(playerId=game.redAtkPlayer._id, new_stats=new_stats[1])
    db_wrap.updatePlayerStats(playerId=game.blueDefPlayer._id, new_stats=new_stats[2])
    db_wrap.updatePlayerStats(playerId=game.blueAtkPlayer._id, new_stats=new_stats[3])


    # Update players achievements
    # update_player_achievements(player_id=game.redDefPlayer._id)
    # update_player_achievements(player_id=game.redAtkPlayer._id)
    # update_player_achievements(player_id=game.blueDefPlayer._id)
    # update_player_achievements(player_id=game.blueAtkPlayer._id)




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
    
    return json.loads(json_util.dumps(asdict(player)))


def calculate_stats_after_game(game: Game) -> list[Stats]:
    """
    Calculate the new stats for each player after a game.

    Parameters
    ----------
    game: Game
        The game through which compute the new stats

    Returns
    -------
    list of Stats:
        List of the new stats for the players, ordered in the same way as in the Game object
    """
    new_stats = [game.redDefPlayer.stats, game.redAtkPlayer.stats,
                 game.blueDefPlayer.stats, game.blueAtkPlayer.stats]

    # Increase games_played
    for stat in new_stats:
        stat.games_played += 1

    # Update win streaks
    if game.winnerTeamColor == 'red':
        new_stats[0].def_win_streak += 1
        new_stats[1].atk_win_streak += 1
        new_stats[2].def_win_streak = 0
        new_stats[3].atk_win_streak = 0
    elif game.winnerTeamColor == 'blue':
        new_stats[0].def_win_streak = 0
        new_stats[1].atk_win_streak = 0
        new_stats[2].def_win_streak += 1
        new_stats[3].atk_win_streak += 1

    return new_stats


def update_player_achievements(player_id: str | ObjectId):
    """
    Update the player achievements based on their stats, scores and other variables.
    If the achievement progress was never made on that achievement, a new document is created.

    Parameters
    ----------
    player_id: str | ObjectId
        The ID of the player whose achievements need to be updated.
    """
    
    if not isinstance(player_id, ObjectId):
        player_id = ObjectId(player_id)
    
    # Get all achievements from the database
    all_achievements = db_wrap.getAllAchievements()

    # Get the updated player from the database
    player = db_wrap.getPlayerById(player_id=player_id)

    # For all the achievements, look for the document related to the player
    # Update the progress
    # Check if the progress has met the achievement requirement, if so unlock it
    for achievement in all_achievements:
        player_achievement = db_wrap.player_achievements.find_one({
            "player_id": player_id,
            "achievement_id": achievement['_id']
        })
        
        if not player_achievement:
            # If the player has never started progress on this achievement, create a new document
            player_achievement = {
                "player_id": player_id,
                "achievement_id": achievement['_id'],
                "progress": 0,  
                "unlocked": False,
                "unlocked_date": ''
            }
            db_wrap.player_achievements.insert_one(player_achievement)
        
        # Update the progress on that
        if achievement['criteria']['type'] == 'games_played':
            player_achievement['progress'] = player.stats.games_played

        elif achievement['criteria']['type'] == 'def_win_streak':
            player_achievement['progress'] = player.stats.def_win_streak

        elif achievement['criteria']['type'] == 'atk_win_streak':
            player_achievement['progress'] = player.stats.atk_win_streak

        # Unlock the player achievement if the requirements are met
        # TODO: Add a field in criteria to decide the operation (>=, <=, ==, something else)
        if player_achievement['progress'] >= achievement['criteria']['value']: 
            player_achievement['unlocked'] = True
            player_achievement['unlocked_date'] = datetime.now(timezone.utc)
        
        


if __name__ == "__main__":
    player1 = Player(name="Player1", last_name="One")
    player2 = Player(name="Player2", last_name="Two")
    player3 = Player(name="Player3", last_name="Three")
    player4 = Player(name="Player4", last_name="Four")
    game = Game(redDefPlayer=player1, redAtkPlayer=player2, blueDefPlayer=player3, blueAtkPlayer=player4, winnerTeamColor="red")

    app.run(debug=True)
