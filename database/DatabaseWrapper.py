from pymongo import MongoClient
import datetime
from models.game import Game
from models.player import Player
from models.score import Score
from dataclasses import asdict

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
            'def_score': {'mu': player.def_score.mu,
                          'sigma': player.def_score.sigma,
                          'rank': player.def_score.rank},
            'atk_score': {'mu': player.atk_score.mu,
                          'sigma': player.atk_score.sigma,
                          'rank': player.atk_score.rank}
        }

        # Insert the player
        result = self.players.insert_one(new_entry)

    def updatePlayerScore(self, player: Player, new_score: Score, isDefScore: bool = True):
        filter = {
            '_id': player.id
        }
        
        if isDefScore:
            new_score = {
                '$set': {'def_score.mu': new_score.mu,
                         'def_score.sigma': new_score.sigma,
                         'def_score.rank': new_score.rank}
            }
        else:
            new_score = {
                '$set': {'atk_score.mu': new_score.mu,
                         'atk_score.sigma': new_score.sigma,
                         'atk_score.rank': new_score.rank}
            }

        res = self.players.find_one_and_update(filter=filter, update=new_score)

        return res


    def addGame(self, game: Game):
        new_entry = {
            'gameID': game.id,
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
        
        new_entry = asdict(game)
        

        # Insert the game
        result = self.games.insert_one(new_entry)

    
    def getGameById(self, game_id: str) -> Game:
        pass

    def getPlayerById(self, player_id: str) -> Player:
        return self.players.find({'name': 'Davide'})


if __name__ == '__main__':
    
    player1 = Player('1', 'asda', 'asdn')
    player2 = Player('123123', 'Coso', 'Dei cosis', 100, 20)
    player3 = Player('fgh', 'Maremma', 'Maiala', 2100, 20)
    player4 = Player('kasn', 'Puttana', 'Troia', 1002, 2011)

    game = Game('12', datetime.datetime.now(), player1, player3, player2, player4, 'red')
    db_wrapper = DatabaseWrapper()

    print(db_wrapper.getPlayerById('s'))

