from datetime import datetime
from models.player import Player
from dataclasses import dataclass, field

@dataclass
class Game:
    redDefPlayer: Player
    redAtkPlayer: Player
    blueDefPlayer: Player
    blueAtkPlayer: Player
    winnerTeamColor: str
    date: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.winnerTeamColor not in ['red', 'blue']: raise ValueError('winnerTeamColor has to be between red and blue')