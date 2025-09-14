from datetime import datetime, timezone
from models.player import Player
from dataclasses import dataclass, field
from bson import ObjectId

@dataclass
class Game:
    redDefPlayer: Player | dict
    redAtkPlayer: Player | dict
    blueDefPlayer: Player | dict
    blueAtkPlayer: Player | dict
    winnerTeamColor: str
    date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    _id: ObjectId | str = None  # Optional, set when loaded from DB

    
    def __post_init__(self):
        if self.winnerTeamColor not in ['red', 'blue']: raise ValueError('winnerTeamColor has to be between red and blue')
        if isinstance(self.redDefPlayer, dict):
            self.redDefPlayer = Player(**self.redDefPlayer)
        if isinstance(self.redAtkPlayer, dict):
            self.redAtkPlayer = Player(**self.redAtkPlayer)
        if isinstance(self.blueDefPlayer, dict):
            self.blueDefPlayer = Player(**self.blueDefPlayer)
        if isinstance(self.blueAtkPlayer, dict):
            self.blueAtkPlayer = Player(**self.blueAtkPlayer)


