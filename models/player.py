from models.score import Score
from dataclasses import dataclass, field

@dataclass
class Player:
    name: str
    last_name: str 
    def_score: Score | dict = field(default_factory=Score) 
    atk_score: Score | dict = field(default_factory=Score) 
    prev_def_score: Score = field(default_factory=Score)
    prev_atk_score: Score = field(default_factory=Score)
    _id: str = None  # Optional, set when loaded from DB

    def __post_init__(self):
        if not self.name or not self.last_name:
            raise ValueError("Player must have a name and last name")
        
        if isinstance(self.def_score, dict):
            self.def_score = Score(**self.def_score)
        if isinstance(self.atk_score, dict):
            self.atk_score = Score(**self.atk_score)

