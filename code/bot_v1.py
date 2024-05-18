

class Bot:
    def __init__(self):
        self.name = 'asdasde'

    def parse_line(self, line : str):
        self.line = line
    def calculate_next_move(self):
        self.next_move = 'rest'

    def play_move(self):
        print(self.next_move, flush = True)