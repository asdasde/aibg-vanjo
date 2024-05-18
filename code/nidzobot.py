import re
import sys

from AbstractBot import AbstractBot
from resource import Resource

# Dx and dy for 4 directions
dx_list = [0, 1, -1]
dy_list = [1, -1, 0]


class Bot(AbstractBot):

    def __init__(self):
        super().__init__()
        self.turn_on_base_leave = None

    def parse_line(self, line : str):
        super().parse_line(line)
        if self.turn_on_base_leave is None:
            self.turn_on_base_leave = self.us

    def reach_target(self, target):
        shortest_path = self.map.shortest_path(self.map.get_player_position(self.us + 1), target)

        if shortest_path is None:
            self.next_move = 'rest'
            return

        next_cord = shortest_path[1]
        # if you dont have enough energy to move to the next cell, rest
        if self.players[self.us].energy <= self.manhattan_distance_of_path([self.map.get_player_position(self.us + 1), next_cord]) * min(8, 1 + self.players[self.us].backpack_capacity):
            self.next_move = 'rest'
            return
        self.move(next_cord)


    def calculate_next_move(self):
        self.next_move = 'rest'
        resource_tiles = self.find_all_resource_tiles()
        best_resource = self.find_best_resource(resource_tiles)
        if best_resource is not None:
            if best_resource.shortest_path_to_resource == 0:
                if best_resource.mines_left(8 - self.players[self.us].backpack_capacity) > 0:
                    print(f"mining {str(best_resource)}, currently on tile {self.map.get_player_position(self.us + 1)}", file=sys.stderr)
                    self.mine((best_resource.row, best_resource.col))
                    return
            else:
                self.reach_target(best_resource.position_to_collect)
                return

        if self.map.get_player_position(self.us + 1) == self.bases[self.us]:
            my_player = self.players[self.us]
            raw_minerals = int(my_player.raw_minerals)
            raw_diamonds = int(my_player.raw_diamonds)
            processed_minerals = int(my_player.processed_minerals)
            processed_diamonds = int(my_player.processed_diamonds)
            if my_player.energy < 250:
                expected_energy_needed = (1000 - my_player.energy) * (250 - self.turn) / max(self.turn, 1)
                if expected_energy_needed > my_player.energy * 0.92:
                    minerals_to_xp = max(raw_minerals + processed_minerals - 1, 0)
                    diamonds_to_xp = raw_diamonds + processed_diamonds
                    if minerals_to_xp == raw_minerals + processed_minerals and my_player.energy < 100:
                        diamonds_to_xp = max(raw_diamonds + processed_diamonds - 1, 0)
                else:
                    minerals_to_xp = raw_minerals + processed_minerals
                    diamonds_to_xp = raw_diamonds + processed_diamonds
                self.convert(0, 0, raw_diamonds + processed_diamonds - diamonds_to_xp, raw_minerals + processed_minerals - minerals_to_xp, diamonds_to_xp, minerals_to_xp)
            else:
                self.convert(0, 0, 0, 0,
                                              raw_diamonds + processed_diamonds,
                                              raw_minerals + processed_minerals)
            self.turn_on_base_leave = int(self.turn) + 2
            return
        self.reach_target(self.bases[self.us])

    def manhattan_distance_of_path(self, path):
        return sum(abs(path[i][0] - path[i + 1][0]) + abs(path[i][1] - path[i + 1][1]) for i in range(len(path) - 1))

    def find_all_resource_tiles(self):
        resource_tiles = []
        my_position = self.map.get_player_position(self.us + 1)
        tile_re = re.compile(r'([MD])_([0-9])_([0-9]{1,2})')
        for row in range(self.map.rows):
            for col in range(self.map.cols):
                regex_match = tile_re.match(self.map.board[row][col])
                if regex_match:
                    shortest_path = 1000
                    shortest_path_to_resource = 1000
                    shortest_path_to_base = 1000
                    position_to_collect = None
                    manhattan_distance_min = None
                    new_resource = Resource(row, col, regex_match.group(1), int(regex_match.group(2)),
                                            int(regex_match.group(3)))

                    if new_resource.left == 0:
                        continue
                    for dx in dx_list:
                        for dy in dy_list:
                            if not (dx != 0 and dy != 0) and not (dx == 0 and dy == 0) and 0 <= row + dx < self.map.rows and 0 <= col + dy < self.map.cols:
                                if self.map.board[row + dx][col + dy] == 'E' or self.map.board[row + dx][
                                    col + dy] == str('A' if self.us == 0 else 'B') or self.map.board[row + dx][
                                    col + dy] == str(self.us + 1):
                                    path_to_resource = self.map.shortest_path(my_position, (row + dx, col + dy))
                                    if path_to_resource is None:
                                        continue
                                    if self.map.board[row + dx][col + dy] == str(self.us + 1):
                                        path_to_base = self.map.shortest_path((row + dx, col + dy), self.bases[self.us])
                                    else:
                                        path_to_base = self.map.shortest_path(self.bases[self.us], (row + dx, col + dy))
                                    if path_to_base is None:
                                        continue
                                    path = len(path_to_resource) + len(path_to_base) - 2
                                    if path < shortest_path:
                                        position_to_collect = (row + dx, col + dy)
                                        shortest_path = path
                                        shortest_path_to_resource = len(path_to_resource)-1
                                        shortest_path_to_base = len(path_to_base)-1
                                        manhattan_distance_min = self.manhattan_distance_of_path(path_to_resource) + min(8, 1 + new_resource.mines_left() * new_resource.left) * self.manhattan_distance_of_path(path_to_base)

                    if shortest_path >= 1000:
                        continue
                    new_resource.shortest_path_to_resource = shortest_path_to_resource
                    new_resource.shortest_path_to_base = shortest_path_to_base
                    new_resource.position_to_collect = position_to_collect
                    new_resource.manhattan_distance_min = manhattan_distance_min
                    resource_tiles.append(new_resource)
        return resource_tiles

    def find_best_resource(self, resource_tiles):
        if not resource_tiles:
            return None

        player = self.players[self.us]
        raw_minerals = int(player.raw_minerals)
        raw_diamonds = int(player.raw_diamonds)
        processed_minerals = int(player.processed_minerals)
        processed_diamonds = int(player.processed_diamonds)
        xp_if_going_to_base = (raw_minerals + processed_minerals) * 10 + (raw_diamonds + processed_diamonds) * 25
        best_resource = resource_tiles[0]
        total_xp = (best_resource.calculate_available_xp(8 - player.backpack_capacity) + xp_if_going_to_base)
        move_total = (best_resource.shortest_path() + 1 + best_resource.mines_left(8 - player.backpack_capacity)) * 2 + (int(self.turn) - self.turn_on_base_leave)
        best_xp_per_turn = total_xp / move_total
        for resource in resource_tiles:
            total_xp = (resource.calculate_available_xp(8 - player.backpack_capacity) + xp_if_going_to_base)
            move_total = (resource.shortest_path() + 1 + resource.mines_left(8 - player.backpack_capacity)) * 2 + (int(self.turn) - self.turn_on_base_leave)
            resource_xp_per_turn = total_xp / move_total
            if resource_xp_per_turn > best_xp_per_turn:
                print(f"resource {str(resource)} has {total_xp} xp, {move_total} moves, {resource_xp_per_turn} xp per turn", file=sys.stderr)
                best_xp_per_turn = resource_xp_per_turn
                best_resource = resource
            elif resource_xp_per_turn == best_xp_per_turn:
                if resource.manhattan_distance_min < best_resource.manhattan_distance_min:
                    best_resource = resource
                elif resource.manhattan_distance_min == best_resource.manhattan_distance_min:
                    if resource.shortest_path_to_resource < best_resource.shortest_path_to_resource:
                        best_resource = resource
                    elif resource.shortest_path_to_resource == best_resource.shortest_path_to_resource:
                        if resource.shortest_path_to_base < best_resource.shortest_path_to_base:
                            best_resource = resource


        shortest_path_to_base = (len(
            self.map.shortest_path(self.map.get_player_position(self.us + 1), self.bases[self.us])) - 1) * 2 + (int(self.turn) - self.turn_on_base_leave)
        xp_per_turn_if_going_to_base = xp_if_going_to_base / (shortest_path_to_base + 1)
        if xp_per_turn_if_going_to_base > best_xp_per_turn:
            return None
        return best_resource

    # def tiles_which_protect_factory(self, factory_position: tuple) -> list[tuple]:
    #     r, c = factory_position
    #     diagonal_nodes = [(r - 1, c - 1), (r - 1, c + 1), (r + 1, c - 1), (r + 1, c + 1)]
    #     diagonal_nodes = [(r, c) for r, c in diagonal_nodes if 0 <= r < self.map.rows and 0 <= c < self.map.cols]
    #     adjacent_nodes = self.map.get_adjacent_nodes(r, c)
    #     return adjacent_nodes + diagonal_nodes
