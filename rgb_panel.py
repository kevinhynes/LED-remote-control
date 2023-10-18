import random
import sys
import string
import logging
import jnius
import struct
import webcolors
import colorsys
from collections import namedtuple
from typing import Optional, List
from threading import Thread
from jnius import cast, autoclass
from functools import partial
from typing import Union
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.clock import mainthread
from kivy.properties import NumericProperty, ListProperty, ObjectProperty, StringProperty, \
    BooleanProperty
from kivy.metrics import dp, sp
from kivy.graphics import Color
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRoundFlatButton, MDRectangleFlatButton
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.slider import MDSlider
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.pickers import MDColorPicker

from troubleshooting import func_name, Dot
from bluetooth_helpers import Command


class ToggleTray(MDRelativeLayout):
    panel = ObjectProperty()

    def __init__(self, **kwargs):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        super().__init__(**kwargs)
        self.is_opened = True
        self.opened_height = 0

    def on_panel(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        # self.panel.bind(height=self.update_opened_height)
        Clock.schedule_once(self.update_opened_height)

    def update_opened_height(self, *args):
        self.opened_height = dp(50) + self.panel.height
        # Clock.schedule_once(self.open)

    def open(self, *args):
        self.height = self.opened_height
        self.panel.x = self.x
        # self.panel.top = self.y
        self.is_opened = True
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        logging.debug(f'\t heights: {self.height, self.panel.height}')

    def close(self, *args):
        self.height = dp(50)
        self.panel.x = Window.width
        self.is_opened = False
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        logging.debug(f'\t heights: {self.height, self.panel.height}')

    def toggle(self, *args):
        if self.is_opened:
            self.close()
        else:
            self.open()


class RGBPanelTray(ToggleTray, Dot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class RGBPanel(MDBoxLayout, Dot):
    dot_color_ = (0, 0, 1, 1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class RGBSlidersTray(ToggleTray):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class RGBSliderBox(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class RGBPresetsTray(ToggleTray):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class RGBPresetsBox(MDGridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        num_buttons = 20
        hue_step = 255 / num_buttons
        for i in range(0, num_buttons):
            hue = i * hue_step
            hsv = [hue / 255, 1, 1]
            rgb = colorsys.hsv_to_rgb(*hsv)
            color_preset_btn = ColorPresetButton(
                md_bg_color=rgb,
            )
            color_preset_btn.bind(on_release=partial(self.update_rgb_sliders,
                                                     color_preset_btn.md_bg_color))
            self.add_widget(color_preset_btn)

    def update_rgb_sliders(self, md_bg_color, *args):
        logging.debug(
            f'`{self.__class__.__name__}.{func_name()}` called with args: {md_bg_color}')
        # self.device_controller.update_rgb_sliders(md_bg_color)


class ColorPresetButton(MDRoundFlatButton):
    pass


class PaletteBuilderTray(ToggleTray):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PaletteBuilder(MDStackLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
