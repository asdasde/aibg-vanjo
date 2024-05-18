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

        self.bases = [(9, 0), (0, 9)]

        self.us = None
        self.opponent = None

    def parse_line(self, line : str):
        self.state_json = json.loads(line)
        self.turn = self.state_json['turn']

        self.us = self.turn % 2
        self.opponent = 1 - self.us

        self.map = Map(self.state_json['board'])
        self.map.print_board()
        self.players = [Player(self.state_json['player1']), Player(self.state_json['player2'])]
        self.player_positions = [self.map.get_player_position(1), self.map.get_player_position(2)]
        sys.stderr.write(str(self.map.shortest_path((0, 0), (8, 8))) + '\n')

    def build_factory(self, target):
        self.next_move = f'build {target[0]} {target[1]}'

    def move(self, target):
        self.next_move = f'move {target[0]} {target[1]}'

    def convert(self, diamondcoins=0, mineralcoins=0, diamondenergy=0, mineralenergy=0, diamondxp=0, mineralxp=0):
        self.next_move = f'conv {diamondcoins} diamond {mineralcoins} mineral to coins, {diamondenergy} diamond {mineralenergy} mineral to energy, {diamondxp} diamond {mineralxp} mineral to xp'

    def mine(self, target):
        self.next_move = f'mine {target[0]} {target[1]}'

    def rest(self):
        self.next_move = 'rest'

    def shop(self, item):
        self.next_move = f'shop {item}'

    def attack(self, target):
        self.next_move = f'attack {target[0]} {target[1]}'

    def put_refinement(self, target, mineral, diamond):
        self.next_move = f'refinement-put {target[0]} {target[1]} mineral {mineral} diamond {diamond}'

    def take_refinement(self, target, mineral, diamond):
        self.next_move = f'refinement-take {target[0]} {target[1]} mineral {mineral} diamond {diamond}'

    @abstractmethod
    def calculate_next_move(self):
        pass

    def play_move(self):
        sys.stderr.write(f'I played : {self.next_move}\n')
        print(self.next_move, flush = True)
        sys.stderr.write('-------------------------------\n')