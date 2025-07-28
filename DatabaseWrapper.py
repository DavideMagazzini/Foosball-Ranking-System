from pymongo import MongoClient

class Player:
    def __init__(self, name: str, last_name: str, def_score: int = 1000, atk_score: int = 1000):
        self.name = name
        self.last_name = last_name
        self.def_score = def_score
        self.atk_score = atk_score

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


    


db_wrapper = DatabaseWrapper()
db_wrapper.updatePlayerScore(player=Player('Davide', 'Magazzini'), new_score=1800, isDefScore=False)