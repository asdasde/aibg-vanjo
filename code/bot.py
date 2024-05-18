from AbstractBot import AbstractBot


class Bot(AbstractBot):


    def __init__(self):
        super().__init__()
        self.cells_to_reach = [(1,8), (8, 1)]
        self.cells_to_block = [[(0, 8), (1, 9)], [(8, 0), (9, 1)]]
    def reach_target(self, target):
        shortest_path = self.map.shortest_path(self.player_positions[self.turn % 2], target)

        if shortest_path is None:
            self.next_move = 'rest'
            return

        next_cord = shortest_path[1]
        self.next_move = f'move {next_cord[0]} {next_cord[1]}'

    def block_enemy(self):

        to_block = self.cells_to_block[self.turn % 2]

        if self.map.cell_is_empty(to_block[0]):
            self.build_factory(target=to_block[0])
        elif self.map.cell_is_empty(to_block[1]):
            self.build_factory(target=to_block[1])
        else:
            self.next_move = 'rest'

    def calculate_next_move(self):
        if self.player_positions[self.turn % 2] != self.cells_to_reach[self.turn % 2]:
            self.reach_target(self.cells_to_reach[self.turn % 2])
            return
        self.block_enemy()
