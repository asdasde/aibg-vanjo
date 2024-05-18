from AbstractBot import AbstractBot
import sys

class Bot(AbstractBot):
    def __init__(self):
        super().__init__()
        self.cells_to_reach = [(1,8), (8, 1)]
        self.cells_to_block = [[(0, 8), (1, 9)], [(8, 0), (9, 1)]]


    def calculate_next_move(self):
        self.next_move = 'rest'