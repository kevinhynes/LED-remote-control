from kivy.lang import Builder
from kivy.metrics import dp

from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu

KV = '''
MDScreen:

    MDRaisedButton:
        id: button
        text: "PRESS ME"
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: app.menu.open()
'''


class Test(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen = Builder.load_string(KV)
        menu_items = [
            {
                "text": f"Item {i}",
                "leading_icon": "web",
                "trailing_icon": "apple-keyboard-command",
                "trailing_text": "+Shift+X",
                "trailing_icon_color": "grey",
                "trailing_text_color": "grey",
                "on_release": lambda x=f"Item {i}": self.menu_callback(x),
            } for i in range(5)
        ]
        self.menu = MDDropdownMenu(
            md_bg_color="#bdc6b0",
            caller=self.screen.ids.button,
            items=menu_items,
        )

    def menu_callback(self, text_item):
        print(text_item)

    def build(self):
        return self.screen


Test().run()