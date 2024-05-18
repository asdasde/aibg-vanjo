from AbstractBot import AbstractBot
import sys

class Bot(AbstractBot):
    def __init__(self):
        super().__init__()
        self.cells_to_reach = [(1,8), (8, 1)]
        self.cells_to_block = [[(0, 8), (1, 9)], [(9, 1), (8, 0)]]
        self.over = False

    def reach_target(self, target):
        shortest_path = self.map.shortest_path(self.player_positions[self.us], [target], [self.bases[self.opponent]])
        sys.stderr.write(f"Shortest path from {self.player_positions[self.us]} to {target}: {shortest_path}\n")
        if shortest_path is None:
            self.next_move = 'rest'
            return

        next_cord = shortest_path[1]
        self.next_move = f'move {next_cord[0]} {next_cord[1]}'



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
        if self.over:
            self.rest()
            return

        if self.players[self.us].xp < self.players[self.opponent].xp or self.player_positions[self.opponent] == self.bases[self.opponent]:
            self.rest()
            return
            sys.stderr.write("gubimo \n")

        best_varticulation_point, best_varticulation_base, best_varticulation_diff = self.find_best_varticulation_point()
        sys.stderr.write(f'Best varticulation point is : {best_varticulation_point} \n')

        if best_varticulation_point is not None:
            if self.player_positions[self.us] != best_varticulation_base:
                self.reach_target(best_varticulation_base)
            else:
                self.build_factory(target=best_varticulation_point)
                self.over = True
        else:
            shortest_to_base_adj = self.map.shortest_path(source = self.player_positions[self.opponent],
                                                           target = self.cells_to_block[self.us],
                                                           list_to_delete = [self.player_positions[self.us], self.player_positions[self.us]])
            if shortest_to_base_adj is None:
                self.rest()
            else:
                target_point = shortest_to_base_adj[-1]
                our_shortest_to_target = self.map.shortest_path(source = self.player_positions[self.us],
                                                                target= [target_point, self.cells_to_reach[self.us]],
                                                                list_to_delete = [self.bases[self.opponent], self.player_positions[self.opponent]])

                if our_shortest_to_target == None:
                    self.rest()
                    return

                finalPoint = our_shortest_to_target[-1]
                if self.player_positions[self.us] == finalPoint:
                    self.master_plan()
                else:
                    self.reach_target(finalPoint)


#            if self.path_len(our_shortest_to_target) < self.path_len(target_point):
#                finalPoint = our_shortest_to_target[-1]
#                if self.player_positions[self.us] == finalPoint:
#                    self.master_plan()
#                else:
#                    self.reach_target(finalPoint)
#            else:
#
#                sys.stderr.write(" Kao da gubimo al ne gubimo\n")





