from models.score import Score
from dataclasses import dataclass, field

@dataclass
class Player:
    id: str
    name: str
    last_name: str
    def_score: Score = field(default_factory=Score)
    atk_score: Score = field(default_factory=Score)

