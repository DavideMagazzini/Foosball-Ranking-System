from models.score import Score
from models.stats import Stats
from dataclasses import dataclass, field
from bson import ObjectId
import linecache

@dataclass
class Player:
    name: str
    last_name: str 
    def_score: Score | dict = field(default_factory=Score) 
    atk_score: Score | dict = field(default_factory=Score) 
    prev_def_score: Score = field(default_factory=Score)
    prev_atk_score: Score = field(default_factory=Score)
    stats: Stats | dict = field(default_factory=Stats)
    _id: ObjectId | str = None  # Optional, set when loaded from DB
    avatar: str = field(default=None)

    def __post_init__(self):
        if not self.name or not self.last_name:
            raise ValueError("Player must have a name and last name")
        
        if isinstance(self.def_score, dict):
            self.def_score = Score(**self.def_score)
        if isinstance(self.atk_score, dict):
            self.atk_score = Score(**self.atk_score)
        if isinstance(self.prev_def_score, dict):
            self.prev_def_score = Score(**self.prev_def_score)
        if isinstance(self.prev_atk_score, dict):
            self.prev_atk_score = Score(**self.prev_atk_score)
        if isinstance(self.stats, dict):
            self.stats = Stats(**self.stats)

        if not self.avatar:
            emoji_index = hash(self.name + self.last_name) % 352
            self.avatar = linecache.getline("data/emoji_list.txt", emoji_index + 1).removesuffix('\n')


