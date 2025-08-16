from dataclasses import dataclass, field

@dataclass
class Score():
    mu: float = 2000
    sigma: float = 1000/3
    rank: float = field(default=None)

    def __post_init__(self):
        if self.rank is None:
            self.rank = self.mu - 3*self.sigma

    def replace(self, newScore: 'Score'):
        self.mu = newScore.mu
        self.sigma = newScore.sigma
        self.rank = newScore.rank
