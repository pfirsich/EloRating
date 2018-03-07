import cmd
import argparse

import database as db

def addplayer(tag):
    player = db.addplayer(tag)
    print("Added player '{}' (id: {})\nCurrent (starting) rating: {}".format(player.tag, player.id, player.rating))

def report(tag1, tag2, score):
    player1, player2 = db.get_player_by_tag(tag1), db.get_player_by_tag(tag2)
    rating1, rating2 = player1.rating.copy(), player2.rating.copy()
    print("Rating before the match:\n{}: {}\n{}: {}".format(player1.tag, rating1, player2.tag, rating2))
    db.report(player1, player2, score)
    print("Rating after the match:\n{}: {} ({})\n{}: {} ({})".format(\
        player1.tag, player1.rating, player1.rating.delta_str(rating1),\
        player2.tag, player2.rating, player2.rating.delta_str(rating2)))

def standings():
    placement = 1
    for player in db.standings():
        print("{}. {}: {}".format(placement, player.tag, player.rating))
        placement += 1

class Shell(cmd.Cmd):
    intro = "Commands: addplayer, report, standings, write, quit"
    prompt = "> "

    def do_addplayer(self, arg):
        addplayer(arg.strip())

    def do_report(self, arg):
        tag1, tag2, score = arg.split()
        report(tag1, tag2, score)

    def do_standings(self, arg):
        standings()

    def do_write(self, arg):
        db.write()

    def do_quit(self, arg):
        return True

def command_addplayer(args):
    db.read()
    addplayer(args.tag.strip())
    db.write()

def command_report(args):
    db.read()
    report(args.tag1.strip(), args.tag2.strip(), args.score)
    db.write()

def command_standings(args):
    db.read()
    standings()
    db.write()

def command_shell(args):
    db.read()
    Shell().cmdloop()
    db.write()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=command_shell)
    subparsers = parser.add_subparsers()

    parser_addplayer = subparsers.add_parser("addplayer", help="Add a new player")
    parser_addplayer.add_argument("tag", help="The tag of the player")
    parser_addplayer.set_defaults(func=command_addplayer)

    parser_report = subparsers.add_parser("report", help="report a match: 'tag1 tag2 score'")
    parser_report.add_argument("tag1", help="Tag of the first player")
    parser_report.add_argument("tag2", help="Tag of the second player")
    parser_report.add_argument("score", help="Score, e.g. '3-0' or '1-2'")
    parser_report.set_defaults(func=command_report)

    parser_standings = subparsers.add_parser("standings", help="List the current standings")
    parser_standings.set_defaults(func=command_standings)

    parser_shell = subparsers.add_parser("shell", help="Start an interactive shell")
    parser_shell.set_defaults(func=command_shell)

    args = parser.parse_args()
    args.func(args)
