import re


class Resource:
    def __init__(self, row, col, type, left, cooldown):
        self.row = row
        self.col = col
        self.type = type
        self.left = left
        self.cooldown = cooldown
        self.value = 25 if self.type == 'D' else 10
        self.weight = 5 if self.type == 'D' else 2
        self.shortest_path_to_resource = 1000
        self.shortest_path_to_base = 1000
        self.position_to_collect = None

    def __str__(self):
        return f'{self.type} at ({self.row}, {self.col})'

    def shortest_path(self):
        return self.shortest_path_to_resource + self.shortest_path_to_base

    def mines_left(self, backpack_weight_left=8):
        return min(backpack_weight_left / self.weight, self.left)

    def calculate_available_xp(self, backpack_weight_left=8):
        return self.value * self.mines_left(backpack_weight_left)