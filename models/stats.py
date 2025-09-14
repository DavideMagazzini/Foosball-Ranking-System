from dataclasses import dataclass, field

@dataclass
class Stats():
    games_played: int = 0
    def_win_streak: int = 0
    atk_win_streak: int = 0
    def_loss_streak: int = 0
    atk_loss_streak: int = 0

    def __post_init__(self):
        pass