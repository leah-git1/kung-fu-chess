from controller.input_controller import InputController
from graphics.layout import Layout
from graphics import gfx_config

class InputAdapter:
    def __init__(self, controller: InputController, layout: Layout, game):
        self._controller, self._layout, self._game = controller, layout, game

    def on_mouse_event(self, kind, screen_x, screen_y):
        board_pixel = self._layout.screen_to_board_pixel(screen_x, screen_y)
        if board_pixel is None:
            return
        x, y = board_pixel
        if kind == gfx_config.EventType.LEFT_CLICK:
            self._controller.on_click(x, y, self._game)
        elif kind == gfx_config.EventType.RIGHT_CLICK:
            self._controller.on_jump(x, y, self._game)

    def on_window_resized(self, new_width, new_height):
        self._layout.on_resize(new_width, new_height)