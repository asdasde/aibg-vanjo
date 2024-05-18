import json

class Player:
    def __init__(self, player_json: dict):
        self.name = player_json['name']
        self.energy = player_json['energy']
        self.xp = player_json['xp']
        self.coins = player_json['coins']
        self.position = player_json['position']
        self.increased_backpack_duration = player_json['increased_backpack_duration']
        self.daze_turns = player_json['daze_turns']
        self.frozen_turns = player_json['frozen_turns']
        self.backpack_capacity = player_json['backpack_capacity']
        self.raw_minerals = player_json['raw_minerals']
        self.processed_minerals = player_json['processed_minerals']
        self.raw_diamonds = player_json['raw_diamonds']
        self.processed_diamonds = player_json['processed_diamonds']

