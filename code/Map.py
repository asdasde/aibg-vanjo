import json
import sys

import networkx as nx


class Map:
    def __init__(self, board: list):
        self.board = list(reversed(board))
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
        if self.board[r][c] not in ['E', '1', '2']:
            return
        for col in range(c + 1, self.cols):
            if self.board[r][col] == "E":
                distance = col - c
                graph.add_edge((r, c), (r, col), weight=distance)
            else:
                break

        for col in range(c - 1, -1, -1):
            if self.board[r][col] == "E":
                distance = c - col
                graph.add_edge((r, c), (r, col), weight=distance)
            else:
                break

        for row in range(r + 1, self.rows):
            if self.board[row][c] == "E":
                distance = row - r
                graph.add_edge((r, c), (row, c), weight=distance)
            else:
                break

        for row in range(r - 1, -1, -1):
            if self.board[row][c] == "E":
                distance = r - row
                graph.add_edge((r, c), (row, c), weight=distance)
            else:
                break

    def shortest_path(self, source, target):
        return nx.shortest_path(self.graph, source = source, target = target)

    def print_board(self):
        max_width = max(len(cell) for row in self.board for cell in row)
        for r in range(self.rows):
            for c in range(self.cols):
                sys.stderr.write(f"{self.board[r][c]:<{max_width + 2}}")
            sys.stderr.write("\n")
    def __repr__(self):
        nodes_repr = "\n".join([f"Node {node}: {data['value']}" for node, data in self.graph.nodes(data=True)])
        edges_repr = "\n".join(
            [f"Edge from {u} to {v}, weight={d['weight']}" for u, v, d in self.graph.edges(data=True)])
        return f"Graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges:\n" \
               f"Nodes:\n{nodes_repr}\n\nEdges:\n{edges_repr}"