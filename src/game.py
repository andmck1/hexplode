class Hexplode:
    def __init__(self, size=4):
        self.size = size
        self.board = self.initialize_board()
        self.players = ["Player 1", "Player 2"]
        self.current_player = 0

    def initialize_board(self):
        board = []
        max_width = 2 * self.size - 1
        for i in range(max_width):
            width = self.size + min(i, max_width - i - 1)
            row = [{"count": 0, "player": None} for _ in range(width)]
            board.append(row)
        return board

    def display_board(self):
        max_width = len(max(self.board, key=len))
        for i, row in enumerate(self.board):
            offset = " " * (max_width - len(row))
            print(offset + " ".join(str(cell["count"]) for cell in row))
        print()

    def get_neighbors(self, x, y):
        """
        board:
             0 0 0 0
            0 0 0 0 0
           0 0 0 0 0 0
          0 0 1 1 0 0 0
           0 1 1 1 0 0
            0 1 1 0 0
             0 0 0 0

        if (3,1) then neighbours are
        (2,0) = (+1, -1)
        (2,1) = (+1,  0)
        (3,0) = ( 0, -1)
        (3,2) = ( 0, +1)
        (4,0) = (+1, -1)
        (4,1) = (+1,  0)


        if (4,2) then neighbours are
        (3,2), (3,3), (4,1), (4,3), (5,1), (5,2)

        stored board:
        0 0 0 0
        0 0 0 0 0
        0 0 0 0 0 0
        0 0 1 1 0 0 0
        0 1 1 1 0 0
        0 1 1 0 0
        0 0 0 0

        -1/1 = up/down or left/right

        if row is even then check:
            up, up right, left, down, down left, right
        if row is odd:
            up, up left, left, right, down right, down
        """
        neighbors = []

        # if x even, select
        if x % 2 == 0:
            directions = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]
        else:
            directions = [(-1, 0), (-1, -1), (0, -1), (0, 1), (1, 1), (1, 0)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(self.board) and 0 <= ny < len(self.board[nx]):
                neighbors.append((nx, ny))
        return neighbors

    def explode(self, x, y):
        neighbors = self.get_neighbors(x, y)
        for nx, ny in neighbors:
            self.board[nx][ny]["count"] += 1
            self.board[nx][ny]["player"] = self.players[self.current_player]
            if self.board[nx][ny]["count"] > len(neighbors):
                self.explode(nx, ny)

    def valid_move(self, x, y, player):
        return (
            0 <= x < len(self.board)
            and 0 <= y < len(self.board[x])
            and (
                self.board[x][y]["player"] is None
                or self.board[x][y]["player"] == player
            )
        )

    def make_move(self, x, y):
        if self.valid_move(x, y, self.players[self.current_player]):
            self.board[x][y]["count"] += 1
            self.board[x][y]["player"] = self.players[self.current_player]
            if self.board[x][y]["count"] > len(self.get_neighbors(x, y)):
                self.explode(x, y)
            self.current_player = (self.current_player + 1) % 2
        else:
            print("Invalid move!")

    def play(self):
        while True:
            self.display_board()
            try:
                x, y = map(
                    int,
                    input(
                        f"{self.players[self.current_player]}'s turn "
                        "(enter x y): "
                    ).split(),
                )
                self.make_move(x, y)
            except ValueError:
                print("Please enter valid coordinates.")


# To play, just create a Hexplode instance and call play
game = Hexplode()
game.play()
