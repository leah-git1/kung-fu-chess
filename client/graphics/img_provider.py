from graphics.img import Img
import cv2
import numpy as np

class GameImg(Img):
    @classmethod
    def read(cls, path, size=None, keep_aspect_ratio=False):
        inst = cls()
        Img.read(inst, path, size=size, keep_aspect=keep_aspect_ratio)
        if inst.img.shape[2] == 3:          # normalize to BGRA everywhere
            inst.img = cv2.cvtColor(inst.img, cv2.COLOR_BGR2BGRA)
        return inst

    @classmethod
    def blank(cls, width, height, color=(0, 0, 0, 0)):
        inst = cls()
        r, g, b, a = color
        canvas = np.zeros((height, width, 4), dtype=np.uint8)
        canvas[:, :] = (b, g, r, a)           # cv2 stores B,G,R,A
        inst.img = canvas
        return inst

    def resize(self, width, height):
        out = GameImg()
        out.img = cv2.resize(self.img, (max(1, width), max(1, height)))
        return out

    def show(self, window_name="Kung-Fu Chess"):
        cv2.imshow(window_name, self.img)
        cv2.waitKey(1)                         

class WindowManager:
    def __init__(self, window_name, width, height):
        self.window_name = window_name
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, width, height)
        self._events = []
        self._last_size = (width, height)
        cv2.setMouseCallback(window_name, self._on_mouse)

    def _on_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self._events.append({"type": "left_click", "x": x, "y": y})
        elif event == cv2.EVENT_RBUTTONDOWN:
            self._events.append({"type": "right_click", "x": x, "y": y})

    def poll_events(self):
        events, self._events = self._events, []
        w, h = cv2.getWindowImageRect(self.window_name)[2:]
        if (w, h) != self._last_size and w > 0 and h > 0:
            self._last_size = (w, h)
            events.append({"type": "resize", "width": w, "height": h})
        return events

    def is_open(self):
        return cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) >= 1

    def close(self):
        cv2.destroyWindow(self.window_name)