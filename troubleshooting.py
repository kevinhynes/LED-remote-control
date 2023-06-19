from kivy.uix.widget import Widget
from kivy.properties import ListProperty, NumericProperty
from kivy.graphics import Line, Color, Rectangle, Ellipse
from kivy.metrics import dp
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDSwitch


class Overlay_(Widget):
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

    or using KivyMD with a ColorProperty:
        - a collection of 3-4 floats between 0-1 (RGB, RGBA)
        - a string in the format #rrggbb or #rrggbbaa
        - a string representing color name from this list:
            https://www.w3.org/TR/SVG11/types.html#ColorKeywords
    <TestWidget@MDWidget>:
        md_bg_color: (1, 1, 0, 0)
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
    border_color_ = ListProperty([1, 0, 0, 0.75])
    border_width_ = NumericProperty(2)
    border_rect_ = Line()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.after:
            Color(*self.border_color_)
            self.border_rect_ = Line(rectangle=[0, 0, 0, 0],
                                     width=self.border_width_)
        self.bind(pos=self.update_border_rect,
                  size=self.update_border_rect,
                  border_color_=self.update_border_rect,
                  border_width_=self.update_border_rect)

    def update_border_rect(self, *args):
        # self.canvas.clear()
        with self.canvas.after:
            Color(*self.border_color_)
            self.border_rect_.rectangle = [self.x, self.y, self.width - self.border_width_ / 2,
                                          self.height - self.border_width_ / 2]


class Dot(Widget):
    dot_color_ = ListProperty([1, 0, 0, 0.75])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.after:
            Color(*self.dot_color_)
            self.dot = Ellipse()
        self.dot.size = (dp(10), dp(10))
        self.bind(pos=self.update_dot,
                  size=self.update_dot,
                  dot_color_=self.update_dot)

    def update_dot(self, *args):
        self.dot.pos = (self.x - dp(5), self.y - dp(5))


class BorderedMDLabel(MDLabel, Border):
    pass


class BorderedMDSwitch(MDSwitch, Border):
    pass





















