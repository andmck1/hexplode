from textual.app import App, ComposeResult
from rich.panel import Panel
from textual.reactive import reactive, Reactive
from textual.widgets import Static, TextArea
from textual import events
from game import Hexplode


hexplode = Hexplode(size=2)


class PlayerPanel(Static):
    score: Reactive[int] = reactive(0)

    def __init__(self, player_name: str, colour: str, **textual_kwargs):
        super().__init__(**textual_kwargs)
        self.player_name = player_name
        self.colour = colour

    def on_mount(self):
        self.update_panel()

    def increment_score(self):
        self.score += 1
        self.update_panel()

    def update_panel(self):
        self.update(Panel(f"[{self.colour}]{self.player_name}: {self.score}"))


class BoardPanel(Static):
    board = ""

    def on_mount(self):
        self.update_panel()

    def update_panel(self):
        self.update(Panel("Hello There"))


class Board(TextArea):
    def on_key(self, event: events.Key) -> None:
        current_text = self.text.split("\n")
        current_row, current_column = self.cursor_location
        if event.key == "up":
            if current_row - 1 >= 0:
                if (
                    current_text[current_row - 1][current_column]
                    in "0123456789"
                ):
                    self.move_cursor_relative(columns=0, rows=-1)
        if event.key == "down":
            if current_row + 1 < len(current_text):
                if (
                    current_text[current_row + 1][current_column]
                    in "0123456789"
                ):
                    self.move_cursor_relative(columns=0, rows=1)
        if event.key == "left":
            if current_column - 2 >= 0:
                if (
                    current_text[current_row][current_column - 2]
                    in "0123456789"
                ):
                    self.move_cursor_relative(columns=-2, rows=0)
        if event.key == "right":
            if current_column + 2 < len(current_text[current_row]):
                if (
                    current_text[current_row][current_column + 2]
                    in "0123456789"
                ):
                    self.move_cursor_relative(columns=2, rows=0)
        if event.key == "enter":
            self.move_cursor((0, 0))
        event.prevent_default()


class Screen(App):
    CSS_PATH = "css/screen_layout.tcss"

    # board: BoardPanel = BoardPanel(classes="box", id="board")
    player_1: PlayerPanel = PlayerPanel(
        player_name="big man", colour="red", classes="player"
    )
    player_2: PlayerPanel = PlayerPanel(
        player_name="lonk", colour="blue", classes="player"
    )
    board: Board | None = None

    def compose(self) -> ComposeResult:
        self.board = Board("|0|0|0|\n|0|0|0|\n|0|0|0|", read_only=True)
        self.board.cursor_blink = False
        self.board.cursor_location = (0, 1)
        yield self.board
        yield self.player_1
        yield self.player_2

    def on_key(self, event: events.Key) -> None:
        if event.key == "space":
            self.player_1.increment_score()


if __name__ == "__main__":
    app = Screen()
    app.run()
