from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineListItem

KV = '''
BoxLayout:
    orientation: 'vertical'

    WrapTwoLineListItem:
        text: "Primary Text"
        secondary_text: "Long secondary text that should wrap to the next line"
    WrapTwoLineListItem:
        text: "Another Item"
        secondary_text: "Short secondary text"
        
<WrapTwoLineListItem>:
    orientation: 'vertical'
    size_hint_y: None
    height: pri_label.height + secondary_label.height
    padding: "16dp"
    
    MDLabel:
        id: pri_label
        text: root.text
        theme_text_color: "Primary"
        
    MDLabel:
        id: secondary_label
        text: root.secondary_text
        theme_text_color: "Secondary"
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
'''


class WrapTwoLineListItem(TwoLineListItem):
    pass


class MyApp(MDApp):
    def build(self):
        return Builder.load_string(KV)


MyApp().run()
