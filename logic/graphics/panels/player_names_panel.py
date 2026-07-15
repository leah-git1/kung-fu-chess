from graphics import gfx_config
from graphics.img_provider import GameImg


class PlayerNamesPanel:
    def __init__(self, white_name="White", black_name="Black"):
        self.white_name = white_name
        self.black_name = black_name

    def render(self, canvas, x, y, width, height):
        panel = GameImg.blank(width, height, gfx_config.COLOR_PANEL_BG)
        label = f"{self.black_name} vs {self.white_name}"
        text_w = len(label) * 14
        panel.put_text(label, x=(width - text_w) // 2, y=height - 10,
                       font_size=0.9, color=gfx_config.COLOR_GOLD[:3], thickness=2)
        panel.draw_on(canvas, x, y)
