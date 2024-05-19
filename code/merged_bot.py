from AbstractBot import AbstractBot
import sys
import re
from resource import Resource
class Bot(AbstractBot):
    def __init__(self):
        super().__init__()
        self.cells_to_reach = [(1,8), (8, 1)]
        self.cells_to_block = [[(0, 8), (1, 9)], [(9, 1), (8, 0)]]
        self.over = False
        self.turn_on_base_leave = None

    def parse_line(self, line : str):
        super().parse_line(line)
        if self.turn_on_base_leave is None:
            self.turn_on_base_leave = self.us

    def manhattan_distance_of_path(self, path):
        return sum(abs(path[i][0] - path[i + 1][0]) + abs(path[i][1] - path[i + 1][1]) for i in range(len(path) - 1))

    def reach_target(self, target):
        shortest_path = self.map.shortest_path(self.player_positions[self.us], [target], [self.bases[self.opponent]])
        sys.stderr.write(f"Shortest path from {self.player_positions[self.us]} to {target}: {shortest_path}\n")
        if shortest_path is None:
            self.rest()
            return

        next_cord = shortest_path[1]
        if self.players[self.us].energy <= self.manhattan_distance_of_path(
                [self.map.get_player_position(self.us + 1), next_cord]) * min(8, 1 + self.players[
            self.us].backpack_capacity):
            self.rest()
            return

        self.move(next_cord)
    def find_best_resource(self, resource_tiles):
        if not resource_tiles:
            return -1

        player = self.players[self.us]
        raw_minerals = int(player.raw_minerals)
        raw_diamonds = int(player.raw_diamonds)
        processed_minerals = int(player.processed_minerals)
        processed_diamonds = int(player.processed_diamonds)
        xp_if_going_to_base = (raw_minerals + processed_minerals) * 10 + (raw_diamonds + processed_diamonds) * 25
        best_resource = resource_tiles[0]
        total_xp = (best_resource.calculate_available_xp(8 - player.backpack_capacity) + xp_if_going_to_base)
        mine_moves = best_resource.mines_left(8 - player.backpack_capacity)
        move_total = (best_resource.shortest_path() + 1 + mine_moves) * 2 + (int(self.turn) - self.turn_on_base_leave)
        best_xp_per_turn = total_xp / move_total
        while move_total > 250 - self.turn and best_resource.left > 1:
            best_resource.left -= 1
            total_xp = (best_resource.calculate_available_xp(8 - player.backpack_capacity) + xp_if_going_to_base)
            mine_moves = best_resource.mines_left(8 - player.backpack_capacity)
            move_total = (best_resource.shortest_path() + 1 + mine_moves) * 2 + (
                        int(self.turn) - self.turn_on_base_leave)
            best_xp_per_turn = total_xp / move_total
        if move_total > 250 - self.turn and best_resource.left == 1:
            best_resource = None
            best_xp_per_turn = -1
        for resource in resource_tiles:
            total_xp = (resource.calculate_available_xp(8 - player.backpack_capacity) + xp_if_going_to_base)
            move_total = (resource.shortest_path() + 1 + resource.mines_left(8 - player.backpack_capacity)) * 2 + (
                        int(self.turn) - self.turn_on_base_leave)
            resource_xp_per_turn = total_xp / move_total
            while move_total - (int(self.turn) - self.turn_on_base_leave) > 250 - self.turn and resource.left > 1:
                resource.left -= 1
                total_xp = (resource.calculate_available_xp(8 - player.backpack_capacity) + xp_if_going_to_base)
                move_total = (resource.shortest_path() + 1 + resource.mines_left(8 - player.backpack_capacity)) * 2 + (
                            int(self.turn) - self.turn_on_base_leave)
                resource_xp_per_turn = total_xp / move_total
            if resource.left == 1:
                if move_total - (int(self.turn) - self.turn_on_base_leave) > 250 - self.turn:
                    continue
            if resource_xp_per_turn > best_xp_per_turn:
                print(
                    f"resource {str(resource)} has {total_xp} xp, {move_total} moves, {resource_xp_per_turn} xp per turn",
                    file=sys.stderr)
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
        if best_xp_per_turn == 0:
            best_resource = None


        shortest_path_to_base = (self.path_len(
            self.map.shortest_path(self.map.get_player_position(self.us + 1), self.bases[self.us])) - 1) * 2 + (int(self.turn) - self.turn_on_base_leave)
        xp_per_turn_if_going_to_base = xp_if_going_to_base / (shortest_path_to_base + 1)
        if xp_per_turn_if_going_to_base > best_xp_per_turn:
            return None
        return best_resource

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
                    manhattan_distance_min = 1000
                    new_resource = Resource(row, col, regex_match.group(1), int(regex_match.group(2)),
                                            int(regex_match.group(3)))


                    for dx, dy in self.map.directions:
                        nx = row + dx
                        ny = col + dy
                        if self.map.check_bounds((nx, ny)) and self.map.board[nx][ny] in ['E', 'A' if self.us == 0 else 'B', '1' if self.us == 0 else '2']:

                            path_to_resource = self.map.shortest_path(source = my_position,
                                                                      target = (nx, ny),
                                                                      list_to_delete = [self.bases[self.opponent], self.player_positions[self.opponent]])
                            if path_to_resource is None:
                                continue

                            if new_resource.left == 0 and (len(path_to_resource) - 1) * 2 < new_resource.cooldown:
                                continue

                            if self.map.board[row + dx][col + dy] == str(self.us + 1):
                                path_to_base = self.map.shortest_path((row + dx, col + dy), self.bases[self.us],
                                                                      list_to_delete = [self.bases[self.opponent], self.player_positions[self.opponent]])
                            else:
                                path_to_base = self.map.shortest_path(self.bases[self.us], (row + dx, col + dy),
                                                                      list_to_delete = [self.bases[self.opponent], self.player_positions[self.opponent]])


                            if path_to_base is None:
                                continue


                            path = len(path_to_resource) + len(path_to_base) - 2

                            manhattan_distance_path = (self.manhattan_distance_of_path(path_to_resource)
                                                          + min(8, 1 + new_resource.mines_left() * new_resource.left)
                                                          * self.manhattan_distance_of_path(path_to_base))


                            if path < shortest_path or (path == shortest_path and manhattan_distance_path < manhattan_distance_min):
                                position_to_collect = (nx, ny)
                                shortest_path = path
                                shortest_path_to_resource = len(path_to_resource) - 1
                                shortest_path_to_base = len(path_to_base) - 1
                                manhattan_distance_min = manhattan_distance_path

                    if shortest_path >= 1000:
                        continue
                    new_resource.shortest_path_to_resource = shortest_path_to_resource
                    new_resource.shortest_path_to_base = shortest_path_to_base
                    new_resource.position_to_collect = position_to_collect
                    new_resource.manhattan_distance_min = manhattan_distance_min
                    resource_tiles.append(new_resource)
        return resource_tiles

    def xp_greedy(self):
        self.next_move = 'rest'
        resource_tiles = self.find_all_resource_tiles()
        best_resource = self.find_best_resource(resource_tiles)
        if best_resource is not None and best_resource != -1:
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
            if raw_minerals + processed_minerals + raw_diamonds + processed_diamonds == 0:
                self.next_move = 'rest'
                return
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
        if best_resource is None:
            self.reach_target(self.bases[self.us])


    def block_enemy(self):

        to_block = self.cells_to_block[self.us]

        if not self.map.cell_is_empty(to_block[0]):
            if not self.map.cell_is_empty(to_block[1]):
                self.over = True
                self.next_move = 'rest'
            else:
                self.build_factory(to_block[1])
            return
        if not self.map.cell_is_empty(to_block[1]):
            self.build_factory(target=to_block[0])
        elif self.map.inline(self.player_positions[self.opponent], self.bases[self.opponent], 0):
            self.build_factory(target=to_block[0])
        else:
            self.build_factory(target=to_block[1])


    def path_len(self, path):
        if path is None:
            return 101
        return len(path)
    def find_best_varticulation_point(self):

        varticulation_points = self.map.find_varticulation_points(self.player_positions[self.opponent],
                                                           self.bases[self.opponent],
                                                           nodes_to_ignore=[self.bases[self.us], self.player_positions[self.us]])

        sys.stderr.write("Found verticulation points: {}\n".format(varticulation_points))

        if len(varticulation_points) == 0:
            return None, None, None

        good_values = ['1', 'A', 'E'] if self.us == 0 else ['2', 'B', 'E']

        best_varticulation_point = None
        best_varticulation_base = None
        best_varticulation_move_diff = 0

        for varticulation_point in varticulation_points:
            adjecent = self.map.get_adjecent_nodes_with_value(varticulation_point, good_values)
            shortest = self.map.shortest_path(source=self.player_positions[self.us],
                                   target= adjecent,
                                   list_to_delete=[self.bases[self.opponent], self.player_positions[self.opponent]])

            opponent_shortest = self.map.shortest_path(source = self.player_positions[self.opponent],
                                                       target = varticulation_point,
                                                       list_to_delete = [self.bases[self.us], self.player_positions[self.us]])
            if shortest is None:
                continue

            if self.path_len(shortest) - self.path_len(opponent_shortest) < best_varticulation_move_diff:
                best_varticulation_point = varticulation_point
                best_varticulation_base = shortest[-1]
                best_varticulation_move_diff = self.path_len(shortest) - self.path_len(opponent_shortest)

            sys.stderr.write("  - - - - - - - - - - \n")
            sys.stderr.write(f" Varticulation point: {varticulation_point}\n")
            sys.stderr.write(f" Available good noodes: {adjecent}\n")
            sys.stderr.write(f" shorthest path : {shortest}\n ")
            sys.stderr.write(f" opponent shortest path : {opponent_shortest}\n ")
            sys.stderr.write("  - - - - - - - - - - \n")


        return best_varticulation_point, best_varticulation_base, best_varticulation_move_diff

    def master_plan(self):
        myPos = self.player_positions[self.us]
        opPos = self.player_positions[self.opponent]
        if myPos == self.cells_to_reach[self.us]:
            self.block_enemy()
        else:
            if self.map.inline(myPos, opPos, 0) and self.map.inline(myPos, self.bases[self.opponent], 0):
                self.rest()
            elif self.map.inline(myPos, opPos, 1) and self.map.inline(myPos, self.bases[self.opponent], 1):
                self.rest()
            else:
                self.move(self.cells_to_reach[self.us])

    def calculate_next_move(self):
        if self.map.board[self.cells_to_block[self.us][self.us][0]][self.cells_to_block[self.us][self.us][1]][0] == 'F':
            self.xp_greedy()
            sys.stderr.write("  veridict : xp \n")
            return
        if self.over:
            sys.stderr.write('veridict : over\n')
            self.rest()
            return

        if self.players[self.us].xp <= self.players[self.opponent].xp or (self.player_positions[self.opponent] == self.bases[self.opponent] and self.players[self.opponent].backpack_capacity > 0):
            sys.stderr.write('veridict : play greedy because less xp or opponent in base\n')

            self.xp_greedy()
            sys.stderr.write("gubimo \n")
            return

        best_varticulation_point, best_varticulation_base, best_varticulation_diff = self.find_best_varticulation_point()
        sys.stderr.write(f'Best varticulation point is : {best_varticulation_point} \n')

        if best_varticulation_point is not None:
            if self.player_positions[self.us] != best_varticulation_base:

                sys.stderr.write('veridict : reach best articulation point\n')
                self.reach_target(best_varticulation_base)
            else:
                sys.stderr.write('veridict : build factory at articulation point\n')

                self.build_factory(target=best_varticulation_point)
                self.over = True
        else:
            shortest_to_base_adj = self.map.shortest_path(source = self.player_positions[self.opponent],
                                                           target = self.cells_to_block[self.us],
                                                           list_to_delete = [self.player_positions[self.us], self.player_positions[self.us]])
            if shortest_to_base_adj is None:
                self.over = True
                sys.stderr.write('veridict : over2\n')
                self.rest()

            else:
                myPos = self.player_positions[self.us]
                rx, ry = self.cells_to_reach[self.us]
                if self.map.board[rx][ry][0] in ['M', 'D']:
                    self.xp_greedy()
                    return
                r_adj = self.map.get_adjecent_nodes_with_value((rx, ry), ['E', '1' if self.us == 0 else '2'])

                if self.map.board[rx][ry][0] == 'F':

                    if myPos in r_adj:
                        self.attack((rx, ry))


                    else:
                        shortest_adj = self.map.shortest_path(source = myPos,
                                                              target = r_adj,
                                                              list_to_delete = [self.player_positions[self.opponent], self.bases[self.opponent]])
                        if shortest_adj is None:
                            sys.stderr.write('veridict : greedy because no shortest adj\n')
                            self.xp_greedy()
                        else:
                            self.move(shortest_adj[1])

                else:
                    target_point = shortest_to_base_adj[-1]
                    our_shortest_to_target = self.map.shortest_path(source = self.player_positions[self.us],
                                                                    target= [target_point, self.cells_to_reach[self.us]],
                                                                    list_to_delete = [self.bases[self.opponent], self.player_positions[self.opponent]])

                    if our_shortest_to_target is None:
                        sys.stderr.write('veridict : play greedy bcs no path to target points\n')

                        self.xp_greedy() # promeniti logiku da ide sto blize moze u zavisnosti od ranca
                    else:

                        if self.path_len(our_shortest_to_target) == 2:
                            target_point_path = self.map.shortest_path(source = self.player_positions[self.us],
                                                                    target= [target_point],
                                                                    list_to_delete = [self.bases[self.opponent], self.player_positions[self.opponent]])

                            if self.path_len(target_point_path) == 2:
                                sys.stderr.write('veridict : move to target\n')

                                self.move(target_point)

                                return

                        listD = self.map.get_adjecent_nodes_with_value(self.player_positions[self.opponent], ['D'])
                        listM = self.map.get_adjecent_nodes_with_value(self.player_positions[self.opponent], ['M'])
                        backpack = self.players[self.opponent].backpack_capacity
                        sum1 = 0
                        for x, y in listM:
                            sum1 += int(self.map.board[x][y][2])
                        sum2 = 0
                        for x, y in listD:
                            sum2 += int(self.map.board[x][y][2])
                        num1 = min(int((8 - backpack) / 2), sum1)
                        num2 = min(int((8 - backpack) / 5), sum2)
                        num = max(num1, num2)
                        if num1 > 0 and num2 > 0:
                            num = min(num1, num2)
                        if backpack <= 3:
                            if num1 != 0 or num2 != 0:
                                num = min(num, 2)
                            else:
                                num = 3
                        if self.path_len(our_shortest_to_target) + num < self.path_len(shortest_to_base_adj) or self.players[self.us].xp - self.players[self.opponent].xp > 5 * backpack:
                            finalPoint = our_shortest_to_target[-1]
                            if self.player_positions[self.us] == finalPoint:
                                sys.stderr.write('veridict : master plan\n')

                                self.master_plan()
                            else:
                                sys.stderr.write('veridict : move to target master plan\n')

                                self.reach_target(finalPoint)
                        else:
                            sys.stderr.write('veridict : play greeedy not big difference\n')

                            self.xp_greedy()