import sys
import json
from Player import Player
from Map import Map

class Bot:
    def __init__(self):
        self.name = 'asdasde'
        self.turn = None
        self.state_json = None
        self.player1 = None
        self.player2 = None
        self.map = None
        self.next_move = None


    def parse_line(self, line : str):
        self.state_json = json.loads(line)

        self.turn = self.state_json['turn']
        self.player1 = Player(self.state_json['player1'])
        self.player2 = Player(self.state_json['player2'])
        self.map = Map(self.state_json['board'])
        sys.stderr.write(self.map.__str__() + '\n')

    def calculate_next_move(self):
        self.next_move = 'rest'

    def play_move(self):
        print(self.next_move, flush = True)