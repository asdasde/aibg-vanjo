from AbstractBot import AbstractBot


class Bot(AbstractBot):

    def reach_target(self, target):
        shortest_path = self.map.shortest_path(self.player_positions[self.turn % 2], (1, 8))

        if shortest_path is None:
            self.next_move = 'rest'
            return

        next_cord = shortest_path[1]
        self.next_move = f'move {next_cord[0]} {next_cord[1]}'

    def block_enemy(self):
        if self.map.cell_is_empty((0, 8)):
            self.build_factory(target=(0, 8))
        elif self.map.cell_is_empty((1, 9)):
            self.build_factory(target=(1, 9))
        else:
            self.next_move = 'rest'

    def calculate_next_move(self):
        if self.player_positions[self.turn % 2] != (1, 8):
            self.reach_target((1, 8))
            return
        self.block_enemy()
