from pymongo import MongoClient
from pymongo.results import InsertOneResult
import datetime
from models.game import Game
from models.player import Player
from models.score import Score
from dataclasses import asdict
from bson import ObjectId

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
        new_entry = asdict(player)

        # Insert the player
        result = self.players.insert_one(new_entry)
        return result

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


    def addGame(self, game: Game) -> InsertOneResult:
        new_entry = asdict(game)
        
        # Insert the game
        result = self.games.insert_one(new_entry)
        return result

    
    def getGameById(self, game_id: str | ObjectId) -> Game:
        return self.games.find_one({'_id': game_id})

    def getPlayerById(self, player_id: str | ObjectId) -> Player:
        """
        Retrieves a player from the database by its unique identifier.

        Args:
            player_id (str | ObjectId): The unique identifier of the player to retrieve.

        Returns:
            Player: The player class corresponding to the given ID, or None if not found.
        """
        return self.players.find_one({'_id': player_id})
    
    def getAllPlayers(self):
        """
        Retrieves all player records from the database.

        Returns:
            pymongo.cursor.Cursor: A cursor to iterate over all player documents.
        """
        return self.players.find({})



if __name__ == '__main__':
    
    player1 = Player('1', 'asda', 'asdn')
    player2 = Player('123123', 'Coso', 'Dei cosis', 100, 20)
    player3 = Player('fgh', 'Maremma', 'Maiala', 2100, 20)
    player4 = Player('kasn', 'Puttana', 'Troia', 1002, 2011)

    game = Game('12', datetime.datetime.now(), player1, player3, player2, player4, 'red')
    db_wrapper = DatabaseWrapper()

    print(db_wrapper.getPlayerById('s'))

