"""
Observes the game (via GameEventSource) and keeps a bounded, human-readable
move history. Rendering is just a stack of text lines drawn with put_text -
no scrollable widget needed.
"""
from graphics import gfx_config
from graphics.img_provider import GameImg
from graphics.observers.game_events import GameObserver

_MAX_VISIBLE_LINES = 12


def _cell_name(cell) -> str:
    row, col = cell
    file_letter = chr(ord("a") + col)
    rank_number = 8 - row
    return f"{file_letter}{rank_number}"


class MovesLog(GameObserver):
    def __init__(self):
        self._lines = []

    def on_piece_moved(self, event) -> None:
        piece = event.piece
        text = f"{piece.color}{piece.piece_type.value} {_cell_name(event.origin)}-{_cell_name(event.destination)}"
        self._lines.append(text)

    def on_piece_captured(self, event) -> None:
        captured = event.captured_piece
        text = f"x {captured.color}{captured.piece_type.value} at {_cell_name(event.at_cell)}"
        self._lines.append(text)

    def render(self, canvas, x, y, width, height) -> None:
        panel = GameImg.blank(width, height, gfx_config.COLOR_PANEL_BG)
        line_height = 20
        visible = self._lines[-_MAX_VISIBLE_LINES:]
        for i, line in enumerate(visible):
            panel.put_text(line, x=8, y=8 + i * line_height, font_size=14,
                            color=gfx_config.COLOR_PANEL_TEXT[:3])
        panel.draw_on(canvas, x, y)