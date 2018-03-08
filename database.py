import json
import time

import elo as rating

players = []
matches = []

class DBError(Exception):
    pass

class UnknownPlayerTagError(DBError):
    def __init__(self, tag):
        super().__init__("Unknown player tag '{}'".format(tag))
        self.tag = tag

class UnknownPlayerIdError(DBError):
    def __init__(self, player_id):
        super().__init__("Unknown player id {}".format(player_id))
        self.player_id = player_id

class PlayerTagAlreadyExists(DBError):
    def __init__(self, tag):
        super().__init__("Player tag '{}' already exists".format(tag))
        self.tag = tag

class RatingSystemMismatchError(DBError):
    def __init__(self, file, expected):
        super().__init__("Rating system '{}' could not be loaded. Expected: '{}'".format(file, expected))
        self.file_rating_system = file
        self.expected_rating_system = expected

# Not sure if this belongs here
class MalformedScoreStringError(DBError):
    def __init__(self, score_str):
        super().__init__("Malformed score string '{}'".format(score_str))
        self.score_str = score_str

# Only supports "win-loss", e.g. "3-0", "1-2" => no draws! (like "1-1-1")
class Score(object):
    def __init__(self, score_str):
        m = re.match(r"([0-9]+)-([0-9]+)", score_str)
        if m:
            self.wins = int(m.group(1))
            self.losses = int(m.group(2))
        else:
            raise MalformedScoreStringError(score_str)

    def game_count(self):
        return self.wins + self.losses

    def __str__(self):
        return "{}-{}".format(self.wins, self.losses)

class Player(object):
    def __init__(self, player_id, tag, rating):
        self.id = player_id
        self.tag = tag
        self.rating = rating

class Match(object):
    def __init__(self, player1, player2, score, timestamp=None):
        self.player1 = player1
        self.player2 = player2
        self.score = score
        if timestamp == None:
            timestamp = int(time.time())
        self.timestamp = timestamp

def read():
    with open("database.json", "r") as dbFile:
        jsonData = json.load(dbFile)

    if jsonData["rating_system"] != rating.NAME:
        raise RatingSystemMismatchError(jsonData["rating_system"], rating.NAME)

    players.clear()
    for player in jsonData["players"]:
        players.append(Player(player["id"], player["tag"], rating.Rating(player["rating"])))

    matches.clear()
    for match in jsonData["matches"]:
        player1, player2 = get_player_by_id(match["player1"]), get_player_by_id(match["player2"])
        matches.append(Match(player1, player2, Score(match["score"]), match["timestamp"]))

def write():
    data = {'players': [], 'matches': [], 'rating_system': rating.NAME}

    for player in players:
        data["players"].append({'id': player.id, 'tag': player.tag, 'rating': str(player.rating)})

    for match in matches:
        data["matches"].append({'player1': match.player1.id, 'player2': match.player2.id, 'score': str(match.score), 'timestamp': match.timestamp})

    with open("database.json", "w") as dbFile:
        json.dump(data, dbFile, indent=4)

def addplayer(tag):
    try:
        player = get_player_by_tag(tag)
        raise PlayerTagAlreadyExists(tag)
    except UnknownPlayerTagError as err:
        pass

    next_id = 0
    for player in players:
        next_id = max(next_id, player.id)
    next_id += 1

    player = Player(next_id, tag, rating.Rating())
    players.append(player)
    return player

def report(player1, player2, score_str):
    score = Score(score_str)
    matches.append(Match(player1, player2, score))
    rating.update_rating(player1, player2, score)

def standings():
    return sorted(players, key=lambda player: player.rating, reverse=True)

def get_player_by_id(player_id):
    # TODO: Maybe sort the player list by id and use a binary search here
    for player in players:
        if player.id == player_id:
            return player
    else:
        raise UnknownPlayerIdError(player_id)

def get_player_by_tag(tag):
    # TODO: add acceleration structures to speed this up (a dictionary)
    for player in players:
        if player.tag.lower() == tag.lower():
            return player
    else:
        raise UnknownPlayerTagError(tag)
