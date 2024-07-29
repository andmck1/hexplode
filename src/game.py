import numpy as np
import pandas as pd
import networkx as nx


class HexCellNode(nx.Graph):
    default_cell_dict = {"count": 0, "player": None}

    def init_node_attr(self):
        return self.default_cell_dict.copy()

    node_attr_dict_factory = init_node_attr


class Hexplode:
    def __init__(self, size=2):
        self.size = size
        self.board_graph = self.initialise_board_graph()
        self.players = ["Player 1", "Player 2"]
        self.current_player = 0

    @staticmethod
    def hexagonal_coordinates(n):
        """
        Generate all coordinates for a hexagonal board with side length n.
        """
        for x in range(-n + 1, n):
            for y in range(max(-n + 1, -x - n + 1), min(n, -x + n)):
                z = -x - y
                yield (x, y, z)

    @staticmethod
    def hexagonal_neighbours(x, y, z, size):
        """Yield the neighbours of a given hexagon cell in cube coordinates."""
        # Six possible directions for a hex cell
        directions = [
            (+1, -1, 0),
            (+1, 0, -1),
            (0, +1, -1),
            (-1, +1, 0),
            (-1, 0, +1),
            (0, -1, +1),
        ]
        for dx, dy, dz in directions:
            neighbour = (x + dx, y + dy, z + dz)
            if size not in tuple(map(abs, neighbour)):
                yield neighbour

    @staticmethod
    def cubic_to_pixel(x, y, z):
        return (x - y, -x - y)

    @staticmethod
    def pixel_to_array(x, y, n):
        x_n = 2 * n - 1
        y_n = 4 * n - 3

        # could simplify here
        x_n_mid = int((x_n - 1) / 2)
        y_n_mid = int((y_n - 1) / 2)

        # for the array we're reflecting the y axis and and using rows and
        # columns => row ~ -y_pixel; col ~ x_pixel
        column = x + y_n_mid
        row = -y + x_n_mid

        return row, column

    def create_hexagonal_board(self):
        """Create a DataFrame representing the edges of a hexagonal board."""
        size = self.size
        coords = list(self.hexagonal_coordinates(size))
        edges = []
        seen = set()

        for x, y, z in coords:
            for node_x, node_y, node_z in self.hexagonal_neighbours(
                x, y, z, size
            ):
                if (node_x, node_y, node_z) in coords:
                    edge = tuple(sorted([(x, y, z), (node_x, node_y, node_z)]))
                    if edge not in seen:
                        seen.add(edge)
                        edges.append(edge)

        # Creating DataFrame from edges list
        edge_df = pd.DataFrame(edges, columns=["source", "target"])
        return edge_df

    def initialise_board_graph(self):
        df_edges = self.create_hexagonal_board()
        g = nx.from_pandas_edgelist(df_edges, create_using=HexCellNode)
        return g

    def create_board(self):
        g = self.board_graph
        size = self.size
        cubic_nodes = g.nodes()
        node_data = list(g.nodes(data=True))
        pixel_nodes = list(map(lambda x: self.cubic_to_pixel(*x), cubic_nodes))
        array_nodes = list(
            map(lambda x: self.pixel_to_array(*x, size), pixel_nodes)
        )

        board = np.full((size * 2 - 1, size * 4 - 3), fill_value=None)
        for i, (x, y) in enumerate(array_nodes):
            board[x, y] = node_data[i][1]["count"]
        return board

    def explode(self, node):
        g = self.board_graph
        neighbours = g[node]
        for neighbour_node in neighbours:
            g.nodes(data=True)[neighbour_node]["count"] += 1
            g.nodes(data=True)[neighbour_node]["player"] = self.players[
                self.current_player
            ]
            neighbour_node_neighbours = g.nodes[neighbour_node]
            if g.nodes(data=True)[neighbour_node]["count"] > len(
                neighbour_node_neighbours
            ):
                self.explode(neighbour_node)

    def valid_move(self, node, player):
        g = self.board_graph
        is_valid_node = node in g.nodes()
        if not is_valid_node:
            return 0
        node_player = g.nodes(data=True)[node]["player"]
        is_valid_player = (node_player is None) or (node_player == player)
        if not is_valid_player:
            return 0
        return 1

    def make_move(self, node):
        player = self.players[self.current_player]
        g = self.board_graph
        if self.valid_move(node, player):
            g.nodes(data=True)[node]["count"] += 1
            g.nodes(data=True)[node]["player"] = player
            neighbours = g[node]
            if g.nodes(data=True)[node]["count"] > len(neighbours):
                g.nodes(data=True)[node]["count"] = 1
                self.explode(node)
            self.current_player = (self.current_player + 1) % 2
        else:
            print("Invalid move: ", node, " for Player: ", player)

    def display_board(self):
        board_arr = self.create_board()
        board_str = ""
        for row in board_arr:
            for val in row:
                if val is not None:
                    board_str += str(val)
                else:
                    board_str += " "
            board_str += "\n"
        return board_str
