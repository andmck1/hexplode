from rich.panel import Panel
from rich.text import Text
from rich.containers import Lines

from textual.app import App, ComposeResult, RenderResult
from textual.events import Key
from textual.reactive import reactive, Reactive
from textual.widgets import Static, TextArea
from textual import events

from game import Hexplode

hexplode = Hexplode(size=3)


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


class BoardTextBox(Static, can_focus=True):
    cursor_column: int
    cursor_row: int
    text: reactive[Text] = reactive(Text(""))

    def __init__(self, text: Text, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.cursor_column = 2
        self.cursor_row = 0
        self.update_text_with_cursor()

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
                pixel_coords = hexplode.array_to_pixel(
                    array_row, array_column, hexplode.size
                )
                cubic_coords = hexplode.pixel_to_cubic(*pixel_coords)
                hexplode.make_move(cubic_coords)
                self.text = hexplode.display_board()
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

    def render(self) -> RenderResult:
        return self.text


class Board(TextArea):
    def on_key(self, event: events.Key) -> None:
        current_text = self.text.split("\n")
        current_row, current_column = self.cursor_location
        move_rows = move_columns = 0
        if event.key == "up":
            if current_row - 1 >= 0:
                if current_column - 1 >= 0:
                    move_columns = -1
                    move_rows = -1
                else:
                    move_columns = 1
                    move_rows = -1
        if event.key == "down":
            if current_row + 1 < len(current_text):
                if current_column - 1 >= 0:
                    move_columns = -1
                    move_rows = 1
                else:
                    move_columns = 1
                    move_rows = 1
        if event.key == "left":
            if current_column - 2 >= 0:
                move_columns = -2
                move_rows = 0
        if event.key == "right":
            if current_column + 2 < len(current_text[current_row]):
                move_columns = 2
                move_rows = 0
        if (
            current_text[current_row + move_rows][
                current_column + move_columns
            ]
            in "0123456789"
        ):
            self.move_cursor_relative(columns=move_columns, rows=move_rows)
        if event.key == "enter":
            array_row = current_row
            array_column = current_column
            pixel_coords = hexplode.array_to_pixel(
                array_row, array_column, hexplode.size
            )
            cubic_coords = hexplode.pixel_to_cubic(*pixel_coords)
            hexplode.make_move(cubic_coords)
            self.text = hexplode.display_board()
            self.move_cursor((current_row, current_column))
        event.prevent_default()


class Screen(App):
    CSS_PATH = "css/screen_layout.tcss"

    player_1: PlayerPanel = PlayerPanel(
        player_name="big man", colour="red", classes="player"
    )
    player_2: PlayerPanel = PlayerPanel(
        player_name="lonk", colour="blue", classes="player"
    )
    board: BoardTextBox | None = None

    def compose(self) -> ComposeResult:
        self.board = BoardTextBox(hexplode.display_board())
        yield self.board
        yield self.player_1
        yield self.player_2

    def on_key(self, event: events.Key) -> None:
        if event.key == "space":
            self.player_1.increment_score()


if __name__ == "__main__":
    app = Screen()
    app.run()
