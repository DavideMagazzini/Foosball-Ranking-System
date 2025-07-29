import datetime
from models.player import Player
from dataclasses import dataclass

@dataclass
class Game:
    id: str
    date: datetime
    redDefPlayer: Player
    redAtkPlayer: Player
    blueDefPlayer: Player
    blueAtkPlayer: Player
    winnerTeamColor: str

    def __post_init__(self):
        if self.winnerTeamColor not in ['red', 'blue']: raise ValueError('winnerTeamColor has to be between red and blue')