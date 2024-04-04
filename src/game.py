class Hexplode:
    def __init__(self, size=5):
        self.size = size
        self.board = [
            [{"count": 0, "player": None} for _ in range(size)]
            for _ in range(size)
        ]
        self.players = ["Player 1", "Player 2"]
        self.current_player = 0

    def display_board(self):
        for row in self.board:
            print(" ".join([str(cell["count"]) for cell in row]))
        print()

    def valid_move(self, x, y, player):
        return (
            0 <= x < self.size
            and 0 <= y < self.size
            and (
                self.board[x][y]["player"] is None
                or self.board[x][y]["player"] == player
            )
        )

    def explode(self, x, y):
        directions = [
            (0, 1),
            (1, 0),
            (-1, 0),
            (0, -1),
        ]  # Simulating a 4-directional explosion for simplicity
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                self.board[nx][ny]["count"] += 1
                self.board[nx][ny]["player"] = self.players[
                    self.current_player
                ]
                if self.board[nx][ny]["count"] > len(directions):
                    self.explode(nx, ny)

    def make_move(self, x, y):
        if self.valid_move(x, y, self.players[self.current_player]):
            self.board[x][y]["count"] += 1
            self.board[x][y]["player"] = self.players[self.current_player]
            if (
                self.board[x][y]["count"] > 4
            ):  # Assuming a simple explosion condition
                self.explode(x, y)
            self.current_player = (self.current_player + 1) % 2
        else:
            print("Invalid move!")

    def play(self):
        while True:
            self.display_board()
            x, y = map(
                int,
                input(
                    f"{self.players[self.current_player]}'s turn (enter x y): "
                ).split(),
            )
            self.make_move(x, y)


# To play, just create a Hexplode instance and call play
game = Hexplode()
game.play()
