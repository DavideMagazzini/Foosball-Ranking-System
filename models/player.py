class Player:
    def __init__(self, name: str, last_name: str, def_score: int = 1000, atk_score: int = 1000):
        self.name = name
        self.last_name = last_name
        self.def_score = def_score
        self.atk_score = atk_score