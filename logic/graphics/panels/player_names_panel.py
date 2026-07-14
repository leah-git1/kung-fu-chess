from graphics import gfx_config
from graphics.img_provider import GameImg

class PlayerNamesPanel:
    def __init__(self, white_name, black_name):
        self.white_name, self.black_name = white_name, black_name

    def render(self, canvas, x, y, width, height):
        panel = GameImg.blank(width, height, gfx_config.COLOR_PANEL_BG)
        panel.put_text(f"White: {self.white_name}", x=8, y=8, font_size=16, color=gfx_config.COLOR_PANEL_TEXT[:3])
        panel.put_text(f"Black: {self.black_name}", x=8, y=32, font_size=16, color=gfx_config.COLOR_PANEL_TEXT[:3])
        panel.draw_on(canvas, x, y)