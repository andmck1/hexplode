from time import monotonic
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
    cursor_position: int

    def __init__(self, text: Text = Text("hello there"), **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.cursor_position = len(self.text)
        self.update_text_with_cursor()

    def on_key(self, event: Key) -> None:
        if event.key == "left":
            self.cursor_position = max(0, self.cursor_position - 1)
        elif event.key == "right":
            self.cursor_position = min(
                len(self.text), self.cursor_position + 1
            )
        elif event.key == "enter":
            self.text = Text("general kenobi")

    def update_text_with_cursor(self) -> None:
        line = self.text
        cursor_position = self.cursor_position
        line.stylize("bold magenta", cursor_position, cursor_position + 1)
        self.text = line

    def render(self) -> RenderResult:
        return self.text


class TestApp(App):
    def compose(self) -> ComposeResult:
        yield CustomTextBox()


if __name__ == "__main__":
    app = TestApp()
    app.run()
