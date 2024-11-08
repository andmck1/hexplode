import numpy as np
import pandas as pd
import networkx as nx
from rich.text import Text


PLAYER_STYLES = {None: "none", "Player 1": "red", "Player 2": "blue"}


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
        self.winner = None

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
    def pixel_to_cubic(x_pixel, y_pixel):
        x_cubic = int((x_pixel - y_pixel) / 2)
        y_cubic = int((-x_pixel - y_pixel) / 2)
        z_cubic = y_pixel

        return (x_cubic, y_cubic, z_cubic)

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

    @staticmethod
    def array_to_pixel(row, column, n):
        x_n = 2 * n - 1
        y_n = 4 * n - 3

        # could simplify here
        x_n_mid = int((x_n - 1) / 2)
        y_n_mid = int((y_n - 1) / 2)

        x = column - y_n_mid
        y = -row + x_n_mid

        return x, y

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
        player = np.full((size * 2 - 1, size * 4 - 3), fill_value=None)
        for i, (x, y) in enumerate(array_nodes):
            board[x, y] = node_data[i][1]["count"]
            player[x, y] = node_data[i][1]["player"]
        return board, player

    def explode(self, node, exploded_nodes=[]):
        exploded_nodes.append(node)
        g = self.board_graph
        g.nodes(data=True)[node]["count"] = 1
        neighbours = g[node]
        for neighbour_node in neighbours:
            if neighbour_node not in exploded_nodes:
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
                self.explode(node)
            self.current_player = (self.current_player + 1) % 2
        else:
            print("Invalid move: ", node, " for Player: ", player)
        self.winner = self.check_win()

    def check_win(self) -> str | None:
        player_counts = {"Player 1": 0, "Player 2": 0, None: 0}
        node_data = list(self.board_graph.nodes(data=True))
        n_nodes = len(node_data)
        for node in node_data:
            player_to_count = node[1]["player"]
            player_counts[player_to_count] += 1
        if player_counts["Player 1"] == n_nodes:
            return "Player 1"
        elif player_counts["Player 2"] == n_nodes:
            return "Player 2"
        else:
            return None

    def display_board(self) -> Text:
        board_arr, player_arr = self.create_board()
        board_rich_text = Text("")
        for i in range(len(board_arr)):
            for j in range(len(board_arr[i])):
                n_counters = board_arr[i][j]
                player = player_arr[i][j]
                if n_counters is not None:
                    player_style = PLAYER_STYLES[player]
                    board_rich_text.append(str(n_counters), style=player_style)
                else:
                    board_rich_text += " "
            board_rich_text += "\n"
        return board_rich_text
