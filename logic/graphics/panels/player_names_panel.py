from graphics.img_provider import GameImg


class PlayerNamesPanel:
    def __init__(self, white_name="White", black_name="Black"):
        self.white_name = white_name
        self.black_name = black_name

    def render(self, canvas, x, y, width, height):
        """Render the top bar: player name centered, plus Black/White labels in sidebars."""
        panel = GameImg.blank(width, height, (18, 18, 18, 255))
        label = f"Name: {self.white_name}"
        text_w = len(label) * 10
        panel.put_text(label, x=(width - text_w) // 2, y=height - 12,
                       font_size=0.7, color=(235, 235, 235), thickness=2)
        panel.draw_on(canvas, x, y)
