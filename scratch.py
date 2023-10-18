from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.list import OneLineListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.slider import Slider
from kivymd.uix.button import MDRaisedButton
from kivy.metrics import dp
from rgb_panel import RGBPanelTray


class TestApp(MDApp):

    def build(self):
        self.root_layout = MDBoxLayout()
        self.root_layout.add_widget(RGBPanelTray())
        return self.root_layout


if __name__ == '__main__':
    TestApp().run()
