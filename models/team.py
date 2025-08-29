from models.player import Player
from dataclasses import dataclass, field

@dataclass
class Team:
    defender: Player | dict
    attacker: Player | dict
    color: str

    def __post_init__(self):
        if self.color not in ['red', 'blue']:
            raise ValueError("Team color must be 'red' or 'blue'")
        if isinstance(self.defender, dict):
            self.defender = Player(**self.defender)
        if isinstance(self.attacker, dict):
            self.attacker = Player(**self.attacker)