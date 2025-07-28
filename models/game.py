import datetime
from models.player import Player


class Game:
    def __init__(self, id: str, date: datetime, redDefPlayer: Player, redAtkPlayer: Player,
                 blueDefPlayer: Player, blueAtkPlayer: Player, winnerTeamColor: str):

        if winnerTeamColor not in ['red', 'blue']: raise ValueError('winnerTeamColor has to be between red and blue')

        self.id = id
        self.date = date
        self.redDefPlayer = redDefPlayer
        self.redAtkPlayer = redAtkPlayer
        self.blueDefPlayer = blueDefPlayer
        self.blueAtkPlayer = blueAtkPlayer
        self.winnerTeamColor = winnerTeamColor