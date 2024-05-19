from AbstractBot import AbstractBot

class DazeBot(AbstractBot):

    def calculate_next_move(self):
        self.shop('daze')