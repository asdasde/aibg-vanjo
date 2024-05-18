import json


class Map:
    def __init__(self, map_json: dict):
        self.board = map_json['board']
        self.rows = len(self.board)
        self.cols = len(self.board[0]) if self.rows > 0 else 0
        self.graph = self._create_graph()

    def _create_graph(self):
        graph = {}
        for r in range(self.rows):
            for c in range(self.cols):
                node = (r, c)
                graph[node] = self._get_adjacent_nodes(r, c)
        return graph

    def _get_adjacent_nodes(self, r, c):
        adjacent_nodes = []
        if r > 0:  # Up
            adjacent_nodes.append((r - 1, c))
        if r < self.rows - 1:  # Down
            adjacent_nodes.append((r + 1, c))
        if c > 0:  # Left
            adjacent_nodes.append((r, c - 1))
        if c < self.cols - 1:  # Right
            adjacent_nodes.append((r, c + 1))
        return adjacent_nodes

    def __repr__(self):
        return json.dumps(self.graph, indent=2)
