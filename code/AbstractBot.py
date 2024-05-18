import sys
import json
from Player import Player
from Map import Map
from abc import ABC, abstractmethod

class AbstractBot(ABC):
    def __init__(self):
        self.name = 'asdasde'
        self.turn = None
        self.state_json = None

        self.players = None

        self.player_positions = None

        self.map = None
        self.next_move = None

    def parse_line(self, line : str):
        self.state_json = json.loads(line)
        self.turn = self.state_json['turn']
        self.map = Map(self.state_json['board'])
        self.map.print_board()
        self.players = [Player(self.state_json['player1']), Player(self.state_json['player2'])]
        self.player_positions = [self.map.get_player_position(1), self.map.get_player_position(2)]
        sys.stderr.write(str(self.map.shortest_path((0, 0), (8, 8))) + '\n')

    def build_factory(self, target):
        self.next_move = f'build {target[0]} {target[1]}'

    @abstractmethod
    def calculate_next_move(self):
        pass

    def play_move(self):
        sys.stderr.write(f'I played : {self.next_move}\n')
        print(self.next_move, flush = True)