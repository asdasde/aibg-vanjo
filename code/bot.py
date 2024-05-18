from AbstractBot import AbstractBot
import sys

class Bot(AbstractBot):
    def __init__(self):
        super().__init__()
        self.cells_to_reach = [(1,8), (8, 1)]
        self.cells_to_block = [[(0, 8), (1, 9)], [(8, 0), (9, 1)]]
    def reach_target(self, target):
        shortest_path = self.map.shortest_path(self.player_positions[self.us], target, [self.bases[self.opponent]])
        sys.stderr.write(f"Shortest path from {self.player_positions[self.us]} to {target}: {shortest_path}\n")
        if shortest_path is None:
            self.next_move = 'rest'
            return

        next_cord = shortest_path[1]
        self.next_move = f'move {next_cord[0]} {next_cord[1]}'

    def block_enemy(self):

        to_block = self.cells_to_block[self.us]

        if self.map.cell_is_empty(to_block[0]):
            self.build_factory(target=to_block[0])
        elif self.map.cell_is_empty(to_block[1]):
            self.build_factory(target=to_block[1])
        else:
            self.next_move = 'rest'


    def calculate_next_move(self):
        varticulation = self.map.find_varticulation_points(self.player_positions[self.opponent], self.bases[self.opponent], nodes_to_ignore = [self.bases[self.us]])
        sys.stderr.write(f'Varticulation points are : {varticulation} \n')

        if self.player_positions[self.us] != self.cells_to_reach[self.us]:
            self.reach_target(self.cells_to_reach[self.us])
            return
        self.block_enemy()
