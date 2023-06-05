from kivy.uix.widget import Widget
from kivy.properties import ListProperty, NumericProperty
from kivy.graphics import Line, Color, Rectangle


class Overlay(Widget):
    """Convenience class to put a colored Rectangle on any widget's canvas, defined by and bound
    to the widget's size and pattern.

    For use in troubleshooting the GUI. Inherit this class and redefine `overlay_color_` to change
    the color.

    in python:
    class TestWidget(Overlay):
        overlay_color_ = ListProperty([0, 0, 0.5, 0.5])

    or in .kv file (still need to create TestWidget in python):
    <TestWidget>:
        overlay_color_: (0, 0, 0.5, 0.5)

    This can be done ad hoc in .kv file using Kivy:
    <TestWidget@Widget>:
        canvas:
            Color:
                rgba: 1, 0, 0, 0.25
            Rectangle:
                pos: self.pos
                size: self.size

    but there is no way to create a generic Kivy widget rule in .kv that other widgets can inherit
    from.

    Can also be done very simply using KivyMD theming:
    <TestWidget@MDWidget>:
        md_bg_color: app.theme_cls.primary_light
    """

    # overlay_color is used for some kivy widgets.
    overlay_color_ = ListProperty([1, 0, 0, 0.25])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(*self.overlay_color_)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect, overlay_color_=self.update_color)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def update_color(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*self.overlay_color_)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.update_rect()


class Border(Widget):
    border_color = ListProperty([1, 0, 0, 1])
    border_width = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*self.border_color)
            self.border_rect = Line(rectangle=[0, 0, 0, 0], width=self.border_width)

    def on_pos(self, *args):
        self.update_border_rect()

    def on_size(self, *args):
        self.udpate_border_rect()

    def update_border_rect(self):
        self.border_rect.rectangle = [self.x, self.y, self.width - self.border_width / 2, self.height - self.border_width / 2]


































