from dataclasses import dataclass, field

@dataclass
class Score():
    mu: float = 25
    sigma: float = 25/3
    rank: float = field(init=False)
    

    def __post_init__(self):
        self.rank = self.mu - 3*self.sigma