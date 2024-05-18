import sys
import json
from Player import Player
from Map import Map

class Bot:
    def __init__(self):
        self.name = 'asdasde'
        self.turn = None
        self.state_json = None

        self.players = None

        self.player1_position = None
        self.player2_position = None

        self.map = None
        self.next_move = None


    def parse_line(self, line : str):
        self.state_json = json.loads(line)

        self.turn = self.state_json['turn']

        self.players = [Player(self.state_json['player1']), Player(self.state_json['player2'])]

        self.map = Map(self.state_json['board'])
        self.map.print_board()

        self.player1_position = self.map.get_player_position(1)
        self.player2_position = self.map.get_player_position(2)

        sys.stderr.write(str(self.map.shortest_path((0, 0), (8, 8))) + '\n')

    def reach_target(self, target):
        shortest_path = self.map.shortest_path(self.player1_position, (1, 8))

        if shortest_path is None:
            self.next_move = 'rest'
            return

        next_cord = shortest_path[1]
        self.next_move = f'move {next_cord[0]} {next_cord[1]}'


    def build_factory(self, target):
        self.next_move = f'build {target[0]} {target[1]}'

    def block_enemy(self):
        if self.map.cell_is_empty((0, 8)):
            self.build_factory(target=(0, 8))
        elif self.map.cell_is_empty((1, 9)):
            self.build_factory(target=(1, 9))
        else:
            self.next_move = 'rest'

    def calculate_next_move(self):
        if self.player1_position != (1, 8):
            self.reach_target((1, 8))
            return
        self.block_enemy()




    def play_move(self):
        sys.stderr.write(f'I played : {self.next_move}\n')
        print(self.next_move, flush = True)