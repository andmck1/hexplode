from rich.panel import Panel
from textual.app import App, ComposeResult
from textual.events import Key
from textual.widgets import Static


class TimeDisplay(Static):
    pass


class Stopwatch(Static):
    def compose(self) -> ComposeResult:
        yield TimeDisplay(Panel("[bold red]00:00:00.00"))

    def on_event(self, event: Key) -> None:
        pass


class StopwatchApp(App):
    def compose(self) -> ComposeResult:
        yield Stopwatch()


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
