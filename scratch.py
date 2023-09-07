from kivy.app import App
from kivy.lang import Builder


kv = """
#:import get_color_from_hex kivy.utils.get_color_from_hex
#:import Gradient kivy_gradient.Gradient
RelativeLayout:
    BoxLayout
        id: box
        canvas:
            Rectangle:
                size: self.size
                pos: self.pos
                texture: 
                    Gradient.horizontal(
                    get_color_from_hex("E91E63"), 
                    get_color_from_hex("FCE4EC"), 
                    get_color_from_hex("2962FF")
                    )
"""


class Test(App):
    def build(self):
        return Builder.load_string(kv)

    def on_stop(self):
        self.root.ids.box.export_to_png("gradient.png")


Test().run()