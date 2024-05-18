import json
import sys

import networkx as nx


class Map:
    def __init__(self, board: list):
        self.board = board
        self.rows = len(self.board)
        self.cols = len(self.board[0]) if self.rows > 0 else 0
        self.graph = self._create_graph()

    def _create_graph(self):
        graph = nx.DiGraph()
        for r in range(self.rows):
            for c in range(self.cols):
                node = (r, c)
                graph.add_node(node, value=self.board[r][c])
                self._add_straight_line_edges(graph, r, c)
        return graph

    def _add_straight_line_edges(self, graph, r, c):
        if self.board[r][c] not in ['E', '1', '2', 'A', 'B']:
            return
        for col in range(c + 1, self.cols):
            if self.board[r][col] in ['E', 'A', 'B']:
                distance = col - c
                graph.add_edge((r, c), (r, col), weight=distance)
            else:
                break

        for col in range(c - 1, -1, -1):
            if self.board[r][col] in ['E', 'A', 'B']:
                distance = c - col
                graph.add_edge((r, c), (r, col), weight=distance)
            else:
                break

        for row in range(r + 1, self.rows):
            if self.board[row][c] in ['E', 'A', 'B']:
                distance = row - r
                graph.add_edge((r, c), (row, c), weight=distance)
            else:
                break

        for row in range(r - 1, -1, -1):
            if self.board[row][c] in ['E', 'A', 'B']:
                distance = r - row
                graph.add_edge((r, c), (row, c), weight=distance)
            else:
                break


    def get_adjecent_edges_from(self, nodes : list):
        adjacent_edges = []
        for node in nodes:
            adjacent_edges.extend(self.graph.edges(node))
        return list(set(adjacent_edges))

    def shortest_path(self, source, target, list_to_delete = None):

        try:
            list_to_delete = [] if list_to_delete is None else list_to_delete
            deleted_edges = self.get_adjecent_edges_from(list_to_delete)
            self.graph.remove_nodes_from(list_to_delete)
            shortest_path = nx.shortest_path(self.graph, source = source, target = target)
            self.graph.add_nodes_from(list_to_delete)
            self.graph.add_edges_from(deleted_edges)
            return shortest_path
        except nx.exception.NetworkXNoPath:
            return None

    def get_player_position(self, player : int) -> tuple:
        for r in range(len(self.board)):
            for c in range(len(self.board[0])):
                if self.board[r][c] == str(player):
                    return r, c
        return -1, -1

    def cell_is_empty(self, cell : tuple) -> bool:
        return self.board[cell[0]][cell[1]] == 'E'

    def print_board(self):
        max_width = max(len(cell) for row in self.board for cell in row)
        for r in range(self.rows):
            for c in range(self.cols):
                sys.stderr.write(f"{self.board[r][c]:<{max_width + 2}}")
            sys.stderr.write("\n")

    def check_varticulation(self, point : tuple, point1 : tuple, point2 : tuple, nodes_to_ignore = None) -> bool:

        edges = self.graph.edges(point, data=True)
        self.graph.remove_node(point)

        varticulation = False

        if self.shortest_path(point1, point2, nodes_to_ignore) == None:
            varticulation = True

        self.graph.add_node(point)
        self.graph.add_edges_from(edges)
        return varticulation

    def find_varticulation_points(self, point1 : tuple, point2 : tuple, nodes_to_ignore = None) -> list:

        sys.stderr.write(f'graph nodes : {self.graph.nodes} \n')
        sys.stderr.write(f'num nodes : {len(self.graph.nodes)} \n')

        sys.stderr.write(f"Shortest path from {point1} to {point2} : {self.shortest_path(point1, point2, nodes_to_ignore)} \n")

        if point1 == point2:
            return []

        varticulation_points = []
        for r in range(len(self.board)):
            for c in range(len(self.board[0])):
                if self.board[r][c] == 'E' and self.check_varticulation((r, c), point1, point2, nodes_to_ignore):
                    varticulation_points.append((r, c))
        return varticulation_points
    def __repr__(self):
        nodes_repr = "\n".join([f"Node {node}: {data['value']}" for node, data in self.graph.nodes(data=True)])
        edges_repr = "\n".join(
            [f"Edge from {u} to {v}, weight={d['weight']}" for u, v, d in self.graph.edges(data=True)])
        return f"Graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges:\n" \
               f"Nodes:\n{nodes_repr}\n\nEdges:\n{edges_repr}"