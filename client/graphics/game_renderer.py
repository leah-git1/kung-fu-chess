import cv2
from graphics import gfx_config
from graphics.board_renderer import BoardRenderer
from graphics.piece_renderer import PieceRenderer
from graphics.layout import Layout
from graphics.img_provider import GameImg
from graphics.observers.moves_log import MovesLog
from graphics.observers.score_board import ScoreBoard
from graphics.panels.player_names_panel import PlayerNamesPanel
from graphics.panels.game_over_panel import GameOverPanel
from events.event_bus import EventBus


class GameRenderer:
    """
    Owns every rendering object needed to draw a game frame.
    Used by both GraphicsApp (local) and GameView (networked) — no duplication.
    """

    def __init__(self, white_name: str, black_name: str,
                 bus: EventBus,
                 my_name: str = "", my_rating: int = 0, player_color: str = "w"):
        self.layout        = Layout()
        self.board_renderer = BoardRenderer(self.layout)
        self.piece_renderer = PieceRenderer(self.layout, player_color=player_color)
        self._flip          = (player_color == "b")
        self.names_panel    = PlayerNamesPanel(white_name, black_name,
                                               my_name=my_name, my_rating=my_rating)

        self.bus            = bus
        self.moves_log_b    = MovesLog("b", self.bus)
        self.moves_log_w    = MovesLog("w", self.bus)
        self.score_board    = ScoreBoard(self.bus)
        self.game_over_panel = GameOverPanel(self.bus, white_name, black_name)

    def render_frame(self, canvas: GameImg, game, now_ms: int,
                     selected_cell=None, overlay=None,
                     disconnect_countdown: int | None = None) -> None:
        """
        Draw a complete game frame onto canvas.

        game         : anything with snapshot/active_moves/active_jumps/cooldown_progress
        overlay      : optional panel with a .render(canvas) and .active property
                       drawn on top (e.g. StartGamePanel)
        """
        W = self.layout.window_px_w

        self.names_panel.render(canvas, 0, 0, W, gfx_config.TOP_BAR_H)
        view_selected = (7 - selected_cell[0], 7 - selected_cell[1]) \
            if selected_cell and self._flip else selected_cell
        self.board_renderer.render(canvas, selected_cell=view_selected)
        self.piece_renderer.render(canvas, game, now_ms)
        self._render_sidebar(canvas, "b", self.layout.left_sidebar_x, self.moves_log_b)
        self._render_sidebar(canvas, "w", self.layout.right_sidebar_x, self.moves_log_w)

        if overlay and overlay.active:
            overlay.render(canvas)
        elif self.game_over_panel.active:
            self.game_over_panel.render(canvas)

        if disconnect_countdown is not None:
            self._render_disconnect_overlay(canvas, disconnect_countdown)

    def _render_disconnect_overlay(self, canvas: GameImg, seconds: int) -> None:
        import cv2
        img   = canvas.img
        H, W  = img.shape[:2]
        text  = f"Opponent disconnected — forfeiting in {seconds}s"
        gold  = gfx_config.COLOR_GOLD[:3]
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        x = (W - tw) // 2
        y = H - gfx_config.DISCONNECT_OVERLAY_BOTTOM
        cv2.rectangle(img, (x - gfx_config.PANEL_PADDING, y - th - gfx_config.PANEL_PADDING),
                      (x + tw + gfx_config.PANEL_PADDING, y + gfx_config.PANEL_PADDING),
                      (10, 10, 10, 220), -1)
        cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (*gold, 255), 2, cv2.LINE_AA)

    def _render_sidebar(self, canvas, color: str, x: int, log: MovesLog) -> None:
        sw    = gfx_config.SIDEBAR_PX_W
        top_h = gfx_config.TOP_BAR_H
        log_h = gfx_config.MOVES_LOG_H
        name  = (self.names_panel.black_name if color == "b"
                 else self.names_panel.white_name)

        box_w, box_h = gfx_config.SIDEBAR_NAME_BOX_W, gfx_config.SIDEBAR_NAME_BOX_H
        bx = x + (sw - box_w) // 2
        by = top_h - box_h - gfx_config.SIDEBAR_NAME_BOX_GAP
        if by >= 0:
            cv2.rectangle(canvas.img, (bx, by), (bx + box_w, by + box_h), (20, 20, 20, 255), -1)
            cv2.rectangle(canvas.img, (bx, by), (bx + box_w, by + box_h), (30, 190, 210, 255), 2)
            tx = bx + (box_w - len(name) * gfx_config.SIDEBAR_NAME_CHAR_W) // 2
            cv2.putText(canvas.img, name, (tx, by + box_h - 9),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220, 220, 220, 255), 1, cv2.LINE_AA)

        self.score_board.render_for(canvas, color, x, top_h, sw, gfx_config.SIDEBAR_SCORE_H)
        log.render(canvas, x, top_h + gfx_config.SIDEBAR_SCORE_H, sw, log_h - gfx_config.SIDEBAR_SCORE_H)
