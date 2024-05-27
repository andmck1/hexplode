from textual.app import App, ComposeResult
from textual import events
from textual.widgets import TextArea
from game import Hexplode


hexplode = Hexplode(size=2)


class Board(TextArea):
    text = ""

    @staticmethod
    def generate_board_text():
        board = hexplode.create_board()
        board_text = ""
        for row in board:
            board_text += "|"
            for val in row:
                board_text += str(val) if val is not None else " "
                board_text += "|"
            board_text += "\n"
        return board_text

    def compose(self) -> ComposeResult:
        board_text = self.generate_board_text()
        self.text = board_text
        yield TextArea(self.text, read_only=True)

    def on_key(self, event: events.Key) -> None:
        if event.key == "e":
            location = self.cursor_location
            hexplode.make_move((0, 0, 0))
            board_text = self.generate_board_text()
            self.text = board_text


class HexplodeApp(App):
    def compose(self):
        yield Board()


app = HexplodeApp()
if __name__ == "__main__":
    app.run()
