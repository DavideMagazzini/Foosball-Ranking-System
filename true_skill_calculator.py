from trueskill import Rating, rate_1vs1, rate, TrueSkill
from models.player import Player
from models.game import Game
from models.score import Score
from models.team import Team
from math import sqrt
from scipy.stats import norm

def calculate_skill_after_game(game: Game) -> list[Score, Score, Score, Score]:
    """
    Calculate the new skill ratings for players after a game.

    Parameters
    ----------
    game : Game object containing players information and scores.

    Returns
    -------
    List of new scores.

    """
    red_def_player = game.redDefPlayer
    red_atk_player = game.redAtkPlayer
    blue_def_player = game.blueDefPlayer
    blue_atk_player = game.blueAtkPlayer

    # Calculate the new ratings for the players
    red_def_rating = Rating(mu=red_def_player.def_score.mu, sigma=red_def_player.def_score.sigma)
    red_atk_rating = Rating(mu=red_atk_player.atk_score.mu, sigma=red_atk_player.atk_score.sigma)
    blue_def_rating = Rating(mu=blue_def_player.def_score.mu, sigma=blue_def_player.def_score.sigma)
    blue_atk_rating = Rating(mu=blue_atk_player.atk_score.mu, sigma=blue_atk_player.atk_score.sigma)

    redTeamRatings = [red_def_rating, red_atk_rating]
    blueTeamRatings = [blue_def_rating, blue_atk_rating]

    if game.winnerTeamColor == 'red':
        newRedTeamRatings, newBlueTeamRatings = rate([redTeamRatings, blueTeamRatings])
    else:
        newBlueTeamRatings, newRedTeamRatings = rate([blueTeamRatings, redTeamRatings])

    # Update the players' scores with the new ratings
    red_def_score = Score(mu=newRedTeamRatings[0].mu, sigma=newRedTeamRatings[0].sigma)
    red_atk_score = Score(mu=newRedTeamRatings[1].mu, sigma=newRedTeamRatings[1].sigma)
    blue_def_score = Score(mu=newBlueTeamRatings[0].mu, sigma=newBlueTeamRatings[0].sigma)
    blue_atk_score = Score(mu=newBlueTeamRatings[1].mu, sigma=newBlueTeamRatings[1].sigma)
    
    # Return the updated players
    return [
        red_def_score,
        red_atk_score,
        blue_def_score,
        blue_atk_score
    ]        


def calculate_win_rate(team1: Team, team2: Team) -> float:
    """
    Calculate the win rate of team1 against team2.

    Parameters
    ----------
    team1 : Team 1.
    team2 : Team 2.

    Returns
    -------
    Win rate of team1 against team2 as a float between 0 and 1.

    """
    team1_ratings = [Rating(mu=team1.defender.def_score.mu, sigma=team1.defender.def_score.sigma),
                     Rating(mu=team1.attacker.atk_score.mu, sigma=team1.attacker.atk_score.sigma)]
    team2_ratings = [Rating(mu=team2.defender.def_score.mu, sigma=team2.defender.def_score.sigma),
                     Rating(mu=team2.attacker.atk_score.mu, sigma=team2.attacker.atk_score.sigma)]
    
    # Calculate the win probability using the TrueSkill formula
    delta_mu = sum([r.mu for r in team1_ratings]) - sum([r.mu for r in team2_ratings])
    sum_sigma = sum([r.sigma ** 2 for r in team1_ratings + team2_ratings])
    size = len(team1_ratings) + len(team2_ratings)

    beta = 1000 / 6  # Default beta value in TrueSkill
    denom = sqrt(size * (beta ** 2) + sum_sigma)
    
    win_rate = norm.cdf(delta_mu / denom)
    
    return win_rate

