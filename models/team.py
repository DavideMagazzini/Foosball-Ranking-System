from models.player import Player
from dataclasses import dataclass, field

@dataclass
class Team:
    defender: Player
    attacker: Player
    color: str