from rich.panel import Panel
from rich.text import Text
from rich.containers import Lines

from textual import on, work, log
from textual.app import App, ComposeResult, RenderResult
from textual.events import Key
from textual.message import Message
from textual.reactive import reactive, Reactive
from textual.widgets import Static, Label
from textual.screen import Screen

from game import Hexplode


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


class WinnerScreen(Screen[bool]):
    def __init__(self, winner):
        super().__init__()
        self.winner = winner

    def compose(self) -> ComposeResult:
        message = self.winner + Text(" wins! Play again? yn")
        yield Label(message, id="winner_label")

    @on(Key)
    def on_key(self, event: Key) -> None:
        if event.key == "n":
            self.dismiss(False)
        elif event.key == "y":
            self.dismiss(True)


class Board(Static, can_focus=True):
    cursor_column: int
    cursor_row: int
    text: reactive[Text] = reactive(Text(""))
    hexplode: Hexplode

    class Win(Message):
        def __init__(self, winner: str) -> None:
            self.winner = winner
            super().__init__()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reset()

    def on_key(self, event: Key) -> None:
        lines = self.get_lines()
        cursor_row = self.cursor_row
        cursor_column = self.cursor_column
        current_line = lines[cursor_row]
        current_text = current_line[cursor_column]

        if event.key in ["left", "right", "up", "down"]:
            move_row = cursor_row
            move_column = cursor_column
            if event.key == "left":
                move_column = max(0, cursor_column - 2)
            elif event.key == "right":
                move_column = min(len(current_line) - 1, cursor_column + 2)
            elif event.key == "up":
                move_row = max(0, cursor_row - 1)
                move_column = max(0, cursor_column - 1)
            elif event.key == "down":
                move_row = min(len(lines) - 1, cursor_row + 1)
                move_column = min(len(current_line) - 1, cursor_column + 1)
            target_text = str(lines[move_row][move_column])
            if target_text in "0123456789":
                self.cursor_row = move_row
                self.cursor_column = move_column
                move_row = move_column = 0

        if event.key == "enter":
            if str(current_text) in "0123456789":
                array_row = cursor_row
                array_column = cursor_column
                pixel_coords = self.hexplode.array_to_pixel(
                    array_row, array_column, self.hexplode.size
                )
                cubic_coords = self.hexplode.pixel_to_cubic(*pixel_coords)
                self.hexplode.make_move(cubic_coords)
                self.text = self.hexplode.display_board()
                winner = self.hexplode.winner
                if winner is not None:
                    self.post_message(self.Win(winner))

        self.update_text_with_cursor()

    def update_text_with_cursor(self) -> None:
        lines = self.get_lines()
        cursor_column = self.cursor_column
        cursor_row = self.cursor_row
        _ = [line.stylize("not reverse", 0, len(self.text)) for line in lines]
        lines[cursor_row].stylize("reverse", cursor_column, cursor_column + 1)
        self.text = Text("\n").join(lines)
        self.refresh()

    def get_lines(self) -> Lines:
        return self.text.split("\n")

    def reset(self):
        self.hexplode = Hexplode(size=2)
        self.text = self.hexplode.display_board()
        self.cursor_column = 1
        self.cursor_row = 0
        self.update_text_with_cursor()

    def render(self) -> RenderResult:
        return self.text


class Screen(App):
    CSS_PATH = "css/screen_layout.tcss"

    player_1: PlayerPanel = PlayerPanel(
        player_name="big man", colour="red", classes="player"
    )
    player_2: PlayerPanel = PlayerPanel(
        player_name="lonk", colour="blue", classes="player"
    )
    board: Board = Board()

    def compose(self) -> ComposeResult:
        yield self.board
        yield self.player_1
        yield self.player_2

    @work
    async def on_board_win(self, winner_event: Board.Win) -> None:
        if winner_event.winner == "Player 1":
            self.player_1.increment_score()
        elif winner_event.winner == "Player 2":
            self.player_2.increment_score()
        else:
            log("Error, player not found")

        if await self.push_screen_wait(
            WinnerScreen(Text(f"[red]{winner_event.winner}[/red]"))
        ):
            self.board.reset()
        else:
            self.app.exit()


if __name__ == "__main__":
    app = Screen()
    app.run()
