from kivy.uix.relativelayout import RelativeLayout
from kivy.lang import Builder
from kivymd.app import MDApp

KV = '''
RelativeLayout:
    MDCard:
        size_hint: None, None
        size: "280dp", "180dp"
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        elevation: 10  # Adjust elevation to control shadow intensity
        radius: [15,]
        elevation_normal: 0  # Remove default shadow

    MDCard:
        size_hint: None, None
        size: "280dp", "180dp"
        pos_hint: {"center_x": 0.6, "center_y": 0.6}
        elevation: 10  # Adjust elevation to control shadow intensity
        radius: [15,]
        elevation_normal: 0  # Remove default shadow

    MDIconButton:
        icon: "circle"
        theme_text_color: "Custom"
        text_color: 0, 0, 0, 0.2  # Adjust opacity to control shadow intensity
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        size_hint: None, None
        size: "280dp", "180dp"
'''

class MyApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

MyApp().run()
