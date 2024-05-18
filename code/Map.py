import json
import sys

import networkx as nx


class Map:
    def __init__(self, board: list):
        self.board = board
        self.rows = len(self.board)
        self.cols = len(self.board[0]) if self.rows > 0 else 0
        self.graph = self._create_graph()

        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

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

    def get_adjecent_nodes_with_value(self, node : tuple, list_of_values : list):
        nodes = []
        for dx, dy in self.directions:
            nx = node[0] + dx
            ny = node[1] + dy
            if 0 <= nx < self.rows and 0 <= ny < self.cols and self.board[nx][ny] in list_of_values:
                nodes.append((nx, ny))
        return nodes
    def get_adjecent_edges_from(self, nodes : list):
        adjacent_edges = []
        for node in nodes:
            adjacent_edges.extend(self.graph.edges(node))
        return list(set(adjacent_edges))

    def shortest_path(self, source, target, list_to_delete = None):

        if not isinstance(target, list):
            target = [target]

        list_to_delete = [] if list_to_delete is None else list_to_delete

        queue = [source]
        from_node = []
        for i in range(10):
            cur = []
            for j in range(10):
                cur.append((-1, -1))
            from_node.append(cur)
        while len(queue) > 0:
            current_node = queue.pop(0)
            if current_node in target:
                res = []
                while current_node != source:
                    res.append(current_node)
                    current_node = from_node[current_node[0]][current_node[1]]
                res.append(source)
                return list(reversed(res))
            for neighbor in self.graph.neighbors(current_node):
                has_blocker = False
                for x in list_to_delete:
                    if neighbor[0] == x[0] and current_node[0] == x[0] and (neighbor[1] <= x[1] <= current_node[1] or current_node[1] <= x[1] <= neighbor[1]):
                        has_blocker = True
                    if neighbor[1] == x[1] and current_node[1] == x[1] and (neighbor[0] <= x[0] <= current_node[0] or current_node[0] <= x[0] <= neighbor[0]):
                        has_blocker = True

                if has_blocker:
                    continue

                if from_node[neighbor[0]][neighbor[1]] != (-1, -1):
                    continue
                queue.append(neighbor)
                from_node[neighbor[0]][neighbor[1]] = current_node
        return None
        

    def get_player_position(self, player : int) -> tuple:
        for r in range(len(self.board)):
            for c in range(len(self.board[0])):
                if self.board[r][c] == str(player):
                    return r, c
        return -1, -1

    def cell_is_empty(self, cell : tuple) -> bool:
        return self.board[cell[0]][cell[1]] == 'E'

    def check_varticulation(self, point1 : tuple, point2 : tuple, nodes_to_ignore = None) -> bool:
        if (1,9) in nodes_to_ignore:
            sys.stderr.write(f" varticulation {point1} to {point2} ignoring {nodes_to_ignore} shorthest path {self.shortest_path(point1, [point2], nodes_to_ignore)}\n")

        return self.shortest_path(point1, [point2], nodes_to_ignore) is None

    def find_varticulation_points(self, point1 : tuple, point2 : tuple, nodes_to_ignore = None) -> list:
        sys.stderr.write(f" varticulation {point1} to {point2} ignoring {nodes_to_ignore}\n")
        sys.stderr.write(f" varticulation Shortest path from {point1} to {point2} : {self.shortest_path(point1, [point2], nodes_to_ignore)} \n")

        if point1 == point2 or self.shortest_path(point1, [point2], nodes_to_ignore) is None:
            return []

        varticulation_points = []
        for r in range(len(self.board)):
            for c in range(len(self.board[0])):
                if self.cell_is_empty((r, c)) and self.check_varticulation(point1, point2, nodes_to_ignore + [(r, c)]):
                    varticulation_points.append((r, c))
        return varticulation_points

    def inline(self, point1 : tuple, point2 : tuple, direction) -> bool:
        if direction == 2:
            return self.inline(point1, point2, 0) or self.inline(point1, point2, 1)
        return point1[direction] == point2[direction]
    def print_board(self):
        max_width = max(len(cell) for row in self.board for cell in row)
        for r in range(self.rows):
            for c in range(self.cols):
                sys.stderr.write(f"{self.board[r][c]:<{max_width + 2}}")
            sys.stderr.write("\n")

    def print_graph_stats(self):
        sys.stderr.write(f'graph nodes : {self.graph.nodes} \n')
        sys.stderr.write(f'num nodes : {len(self.graph.nodes)} \n')

        sys.stderr.write(f'num edges: {len(self.graph.edges)} \n')
      #  sys.stderr.write(f'edges: {self.graph.edges} \n')


    def __repr__(self):
        nodes_repr = "\n".join([f"Node {node}: {data['value']}" for node, data in self.graph.nodes(data=True)])
        edges_repr = "\n".join(
            [f"Edge from {u} to {v}, weight={d['weight']}" for u, v, d in self.graph.edges(data=True)])
        return f"Graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges:\n" \
               f"Nodes:\n{nodes_repr}\n\nEdges:\n{edges_repr}"