from graphics import gfx_config
from graphics.img_provider import GameImg
from graphics.observers.game_events import GameObserver


def _cell_name(cell) -> str:
    row, col = cell
    return f"{chr(ord('a') + col)}{8 - row}"


def _fmt_time(ms: int) -> str:
    total_s = ms // 1000
    m, s = divmod(total_s, 60)
    frac = (ms % 1000) // 10
    return f"{m:02d}:{s:02d}.{frac:03d}"


class MovesLog(GameObserver):
    def __init__(self, color: str):
        self._color = color   # "w" or "b"
        self._entries = []    # list of (time_str, move_str)

    def on_piece_moved(self, event) -> None:
        if event.piece.color != self._color:
            return
        move = f"{_cell_name(event.origin)}-{_cell_name(event.destination)}"
        self._entries.append((_fmt_time(event.elapsed_ms), move))

    def on_piece_captured(self, event) -> None:
        if event.by_piece and event.by_piece.color != self._color:
            return
        move = f"x{_cell_name(event.at_cell)}"
        self._entries.append((_fmt_time(event.elapsed_ms), move))

    def render(self, canvas, x, y, width, height) -> None:
        bg = (200, 200, 200, 255)
        header_bg = (230, 230, 230, 255)
        text_color = (20, 20, 20)
        line_color = (160, 160, 160)

        panel = GameImg.blank(width, height, bg)

        # header
        hh = gfx_config.MOVES_LOG_HEADER_H
        header = GameImg.blank(width, hh, header_bg)
        header.put_text("Time", x=8, y=hh - 8, font_size=0.45, color=text_color, thickness=1)
        header.put_text("Move", x=width // 2 + 4, y=hh - 8, font_size=0.45, color=text_color, thickness=1)
        header.draw_on(panel, 0, 0)

        # divider line between columns
        import cv2
        cv2.line(panel.img, (width // 2, 0), (width // 2, height), (*line_color, 255), 1)
        cv2.line(panel.img, (0, hh), (width, hh), (*line_color, 255), 1)

        rh = gfx_config.MOVES_LOG_ROW_H
        max_rows = (height - hh) // rh
        visible = self._entries[-max_rows:]
        for i, (t, m) in enumerate(visible):
            ry = hh + i * rh
            panel.put_text(t, x=4, y=ry + rh - 7, font_size=0.38, color=text_color, thickness=1)
            panel.put_text(m, x=width // 2 + 4, y=ry + rh - 7, font_size=0.38, color=text_color, thickness=1)
            cv2.line(panel.img, (0, ry + rh), (width, ry + rh), (*line_color, 255), 1)

        panel.draw_on(canvas, x, y)
