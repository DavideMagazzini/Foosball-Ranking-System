from pymongo import MongoClient
import datetime
from models.game import Game
from models.player import Player

class DatabaseWrapper():
    def __init__(self):
        uri = "mongodb+srv://wolfreverse:4jge5145s6iQ9p0j@frscluster.jsuqmkw.mongodb.net/?retryWrites=true&w=majority&appName=Frscluster"
        self.client = MongoClient(uri)

        # Access the database
        self.db = self.client["Frs_db"]

        # Get the collections
        self.players = self.db['Players']
        self.games = self.db['Games']


    def addPlayer(self, player: Player):
        new_entry = {
            'name': player.name,
            'last_name': player.last_name,
            'def_score': player.def_score,
            'atk_score': player.atk_score
        }

        # Insert the player
        result = self.players.insert_one(new_entry)

    def updatePlayerScore(self, player: Player, new_score: int, isDefScore: bool = True):
        filter = {
            'name': player.name,
            'last_name': player.last_name
        }
        
        if isDefScore:
            new_score = {
                '$set': {'def_score': new_score}
            }
        else:
            new_score = {
                '$set': {'atk_score': new_score}
            }

        res = self.players.find_one_and_update(filter=filter, update=new_score)

        return res


    def addGame(self, game: Game):
        new_entry = {
            'gameID': game.gameID,
            'date': game.date,
            'redDefPlayer': {'name': game.redDefPlayer.name,
                             'last_name': game.redDefPlayer.last_name,
                             'def_score': game.redDefPlayer.def_score,
                             'atk_score': game.redDefPlayer.atk_score},
            'redAtkPlayer': {'name': game.redAtkPlayer.name,
                             'last_name': game.redAtkPlayer.last_name,
                             'def_score': game.redAtkPlayer.def_score,
                             'atk_score': game.redAtkPlayer.atk_score},
            'blueDefPlayer': {'name': game.blueDefPlayer.name,
                              'last_name': game.blueDefPlayer.last_name,
                              'def_score': game.blueDefPlayer.def_score,
                              'atk_score': game.blueDefPlayer.atk_score},
            'blueAtkPlayer': {'name': game.blueAtkPlayer.name,
                              'last_name': game.blueAtkPlayer.last_name,
                              'def_score': game.blueAtkPlayer.def_score,
                              'atk_score': game.blueAtkPlayer.atk_score},
            'winnerTeamColor': game.winnerTeamColor
            }
        

        # Insert the game
        result = self.games.insert_one(new_entry)

    
    def getGameById(self, game_id: str) -> Game:
        pass

    def getPlayerById(self, player_id: str) -> Player:
        pass


    
player1 = Player('asda', 'asdn')
player2 = Player('Coso', 'Dei cosis', 100, 20)
player3 = Player('Maremma', 'Maiala', 2100, 20)
player4 = Player('Puttana', 'Troia', 1002, 2011)

game = Game('12', datetime.datetime.now(), player1, player3, player2, player4, 'red')
db_wrapper = DatabaseWrapper()
db_wrapper.addGame(game=game)