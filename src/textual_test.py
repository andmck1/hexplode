from time import monotonic
from rich.panel import Panel
from textual.app import App, ComposeResult
from textual.events import Key
from textual.widgets import TextArea, Static
from textual.reactive import reactive


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


class WeirdSelect(TextArea):
    def on_mount(self) -> None:
        self.text = "X|O|X\n" " |X|O\n" "X|O|O"
        self.read_only = True
        self.cursor_blink = False

    def on_key(self, event: Key) -> None:
        if event.key == "enter":
            cursor_location = self.cursor_location
            text = list(map(list, self.text.split("\n")))

            cursor_row = cursor_location[0]
            cursor_col = cursor_location[1]
            if (cursor_row >= len(text[0])) or (cursor_col >= len(text[1])):
                return None

            options = ["X", "O"]
            current_option = text[cursor_row][cursor_col]
            next_option = options[(options.index(current_option) + 1) % 2]

            text[cursor_row][cursor_col] = next_option
            text = "\n".join(map(lambda text_row: "".join(text_row), text))
            self.text = text


class Stopwatch(Static):
    def compose(self) -> ComposeResult:
        yield TimeDisplay()


class StopwatchApp(App):
    def compose(self) -> ComposeResult:
        yield Stopwatch()
        yield WeirdSelect()

    def on_key(self, event: Key) -> None:
        if event.key == "space":
            timedisplay = self.query_one(TimeDisplay)
            timedisplay.pause = not timedisplay.pause


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
