from database.DatabaseWrapper import DatabaseWrapper
from models.game import Game
from models.player import Player
import datetime
from dataclasses import asdict

db_wrapper = DatabaseWrapper()
# player = Player('s', 's', 's')
game = Game('158', datetime.datetime.now(), Player('12','Gesu','Bambino'), Player('a','Coso','aa'), Player('a','mrm','amaialaa'), Player('2a','23','cosi'),'blue')
db_wrapper.addGame(game)
print(asdict(game))

print(db_wrapper.getPlayerById(''))