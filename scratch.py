from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle, Color
from kivy.utils import get_color_from_hex
from kivy_gradient import Gradient


class GradientRectangleApp(App):
    def build(self):
        # Create a RelativeLayout as the root widget
        root_widget = BoxLayout()

        # Create a BoxLayout
        box = BoxLayout()

        # Create a gradient texture using kivy_gradient
        gradient_texture = Gradient.horizontal(
            get_color_from_hex("E91E63"),
            get_color_from_hex("FCE4EC"),
            get_color_from_hex("2962FF")
        )

        # Create a colored Rectangle with the gradient texture
        with box.canvas:
            # Color(1, 1, 1)  # Set color to white
            Rectangle(size=box.size, pos=box.pos, texture=gradient_texture)

        # Add the BoxLayout to the RelativeLayout
        root_widget.add_widget(box)

        return root_widget

if __name__ == '__main__':
    GradientRectangleApp().run()