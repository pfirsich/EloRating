import functools
import math

NAME = "elo"

K_FACTOR = 32

def expected(R_A, R_B):
    return 1 / (1 + 10 ** ((R_B - R_A) / 400))

@functools.total_ordering
class Rating(object):
    def __init__(self, rating_str=None):
        if rating_str == None:
            self.score = 1200
        else:
            self.score = int(rating_str)

    def __str__(self):
        return str(self.score)

    def delta_str(self, old):
        delta = self.score - old.score
        if delta >= 0:
            return "+{}".format(delta)
        else:
            return str(delta)

    def __eq__(self, other):
        return self.score == other.score

    def __lt__(self, other):
        return self.score < other.score

    def copy(self):
        c = Rating()
        c.score = self.score
        return c

def update_rating(player1, player2, score):
    game_count = score.wins + score.losses
    # Terminology like here: https://de.wikipedia.org/wiki/Elo-Zahl
    E_A = expected(player1.rating.score, player2.rating.score)
    S_A = score.wins
    player1.rating.score += math.floor(K_FACTOR * (S_A - E_A * game_count) + 0.5)
    E_B = 1 - E_A
    S_B = score.losses
    player2.rating.score += math.floor(K_FACTOR * (S_B - E_B * game_count) + 0.5)
