from rich.panel import Panel
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Static
from textual.events import Key
from dataclasses import dataclass


class PlayerScore:
    name: str
    colour: str
    score: int = reactive(0)





class PlayerScorePanel(Static):
    score: int = reactive(0)
    name: str
    colour: str

    def __init__(self, name: str, colour: str):
        self.name = name
        self.colour = colour

    def on_mount(self) -> None:
        self.update(Panel(f"[bold {self.colour}]Player 1: {self.score}"))


class BoardPanel:
    pass


class Screen(App):
    def compose(self) -> ComposeResult:
        PlayerScorePanel(name="Player 1", colour="blue")
        PlayerScorePanel(name="Player 2", colour="red")


if __name__ == "__main__":
    app = Screen()
    app.run()
