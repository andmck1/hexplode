from time import monotonic
from rich.containers import Lines
from rich.panel import Panel
from textual.app import App, ComposeResult, RenderResult
from textual.events import Key
from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text


class TimeDisplay(Static):
    start_time = reactive(monotonic)
    time = reactive(0.0)
    pause = False

    def on_mount(self) -> None:
        self.set_interval(1 / 60, self.update_time)

    def update_time(self) -> None:
        self.time = monotonic() - self.start_time

    def watch_time(self, time: float) -> None:
        if not self.pause:
            minutes, seconds = divmod(time, 60)
            hours, minutes = divmod(minutes, 60)
            self.update(
                Panel(
                    f"[bold blue]{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}"
                )
            )


class CustomTextBox(Static, can_focus=True):
    cursor_column: int
    cursor_row: int
    text: reactive[Text] = reactive(Text("hello there"))

    def __init__(
        self, text: Text = Text("hello there\ngeneral kenobi"), **kwargs
    ):
        super().__init__(**kwargs)
        self.text = text
        self.cursor_column = 0
        self.cursor_row = 0
        self.update_text_with_cursor()

    def on_key(self, event: Key) -> None:
        lines = self.get_lines()
        cursor_row = self.cursor_row
        current_line = lines[cursor_row]

        if event.key == "left":
            self.cursor_column = max(0, self.cursor_column - 1)
        elif event.key == "right":
            self.cursor_column = min(
                len(current_line) - 1, self.cursor_column + 1
            )
        elif event.key == "up":
            self.cursor_row = max(0, self.cursor_row - 1)
        elif event.key == "down":
            self.cursor_row = min(len(lines) - 1, self.cursor_row + 1)
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


class TestApp(App):
    def compose(self) -> ComposeResult:
        yield CustomTextBox()


if __name__ == "__main__":
    app = TestApp()
    app.run()
