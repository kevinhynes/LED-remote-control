import logging
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.card import MDCard
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelThreeLine
from kivy.graphics import Color
from kivy_gradient import Gradient

from kivy.graphics import RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.metrics import dp

from bluetooth_helpers import Command
import palettes
from troubleshooting import func_name


class Animation:

    def __init__(self, name='', icon_filepath='', animation_id=-1, variables=(), **kwargs):
        self.name = name
        self.icon_filepath = icon_filepath
        self.animation_id = animation_id
        self.variables = variables


class CometContent(MDBoxLayout):
    pass


class TopPanel(MDCard):
    panel = ObjectProperty()


class BottomPanel(MDCard):
    content = ObjectProperty()


class AnimationExpansionPanel(MDCard):
    top_panel = ObjectProperty()
    bottom_panel = ObjectProperty()

    def __init__(self, name, icon_filepath, **kwargs):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.is_expanded = False
        self.name = name
        self.icon_filepath = icon_filepath
        super().__init__(**kwargs)

    def expand_contract(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        if self.is_expanded:
            self.height = dp(50)
            self.is_expanded = False
        else:
            self.height = dp(250)
            self.is_expanded = True

    def on_kv_post(self, *args):
        self.top_panel.anim_icon.icon = self.icon_filepath
        self.top_panel.name_lbl.text = self.name


class AnimationsScreen(MDScreen):
    grid = ObjectProperty()
    device_controller = ObjectProperty()

    def __init__(self, **kwargs):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        super().__init__(**kwargs)
        self.is_expanded = False
        animation_attrs = [
            ('Comet', 'data/comet.png', 0, []),
            ('Walk', 'data/marcher.png', 1, []),
            ('Splatter', 'data/paint.png', 2, []),
            ('Twinkle', 'data/star.png', 3, [])
        ]

        animations = []
        for attrs in animation_attrs:
            animations.append(Animation(name=attrs[0],
                                        icon_filepath=attrs[1],
                                        animation_id=attrs[2],
                                        variables=attrs[3]))
        self.animations = animations

    def on_pre_enter(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        app = MDApp.get_running_app()
        app.root_screen.ids._top_app_bar.left_action_items = [['arrow-left-bold', self.go_back]]

    def on_kv_post(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        for i, anim in enumerate(self.animations):
            anim_panel = AnimationExpansionPanel(name=anim.name, icon_filepath=anim.icon_filepath)
            anim_panel.bottom_panel.add_widget(CometContent())
            self.grid.add_widget(anim_panel)

    def go_back(self, *args):
        app = MDApp.get_running_app()
        slide_right = SlideTransition(direction='right')
        app.root_screen.screen_manager.transition = slide_right
        app.root_screen.screen_manager.current = 'controllers'
        open_nav_menu = lambda x: app.root_screen.ids._nav_drawer.set_state('open')
        app.root_screen.ids._top_app_bar.left_action_items = [['menu', open_nav_menu]]
