from rich.panel import Panel
from textual.app import App, ComposeResult
from textual.reactive import reactive, Reactive
from textual.widgets import Static
from textual.events import Key


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
    board: Reactive[str] = reactive("")

    def on_mount(self):
        self.update_panel()

    def update_panel(self):
        self.update(Panel("0000\n" "0000\n" "0000\n"))


class Screen(App):
    CSS_PATH = "css/screen_layout.tcss"

    board: BoardPanel = BoardPanel(classes="box", id="board")
    player_1: PlayerPanel = PlayerPanel(
        player_name="big man", colour="red", classes="player"
    )
    player_2: PlayerPanel = PlayerPanel(
        player_name="lonk", colour="blue", classes="player"
    )

    def compose(self) -> ComposeResult:
        yield self.board
        yield self.player_1
        yield self.player_2

    def on_key(self, event: Key) -> None:
        if event.key == "space":
            self.player_1.increment_score()


if __name__ == "__main__":
    app = Screen()
    app.run()
