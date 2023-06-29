import asyncio
import random
import sys
import string
import logging
from functools import partial
from kivy.core.window import Window
from kivy.clock import mainthread
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivy.metrics import dp, sp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRoundFlatButton, MDRectangleFlatButton
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import BaseListItem, OneLineIconListItem, TwoLineListItem
from kivymd.uix.card import MDCard
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.slider import MDSlider
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.screenmanager import SlideTransition

from troubleshooting import *


def func_name():
    return sys._getframe(1).f_code.co_name


class RenameDeviceTextField(MDTextField):
    pass


class ColorPresetButton(MDRoundFlatButton):
    pass


class DeviceController(BaseListItem):
    device = ObjectProperty()
    power_button = ObjectProperty()
    dimmer = ObjectProperty()
    brightness = NumericProperty(50)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._initialize_slider, 0.5)
        Clock.schedule_once(self._initialize_switch, 1.65)

    def _initialize_slider(self, *args):
        # In order for the thumb icon to show the off ring at value == 0 when MDSlider is just
        # instantiated, change it and then change it back to 0.
        self.dimmer.value = 1
        self.dimmer.value = 0
        self.dimmer.disabled = True
        self.dimmer.bind(on_touch_down=self.dimmer_touch_down)
        self.dimmer.bind(on_touch_up=self.dimmer_touch_up)

    def _initialize_switch(self, *args):
        self.power_button.ids.thumb._no_ripple_effect = True
        self.power_button.ids.thumb.ids.icon.icon = 'power'

    def on_device(self, *args):
        self.save_device()

    def save_device(self):
        pass

    def power(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        if self.power_button.active:
            logging.debug('LIGHTS ON!')
            self.dimmer.value = self.brightness
            self.dimmer.disabled = False
        else:
            logging.debug('LIGHTS OFF!')
            self.brightness = self.dimmer.value
            self.dimmer.value = 0
            self.dimmer.disabled = True

    def dim(self, dimmer):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`'
                      f'called with dimmer.value == {dimmer.value}')
        self.app = MDApp.get_running_app()
        self.app.send(2, dimmer.value)

    def dimmer_touch_down(self, dimmer, touch):
        # Reducing the slider to 0 should also turn off the power button, but only after releasing
        # the slider at 0 - in case slider is moved to 0 and back up again.
        #
        # Therefore need the on_touch_up event, but if the touch_up occurs outside of the slider,
        # it isn't possible to know which slider it was for.
        #
        # Grab the touch event for the slider to check the touch_up event later. Don't return True
        # so that KivyMD's slider animations can complete.
        if dimmer.collide_point(touch.x, touch.y) and not dimmer.disabled:
            logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
            logging.debug('Grabbing touch_down INSIDE Dimmer')
            touch.grab(dimmer)

    def dimmer_touch_up(self, dimmer, touch):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        if touch.grab_current is dimmer:
            logging.debug('Found touch_up...')
            if dimmer.collide_point(touch.x, touch.y):
                logging.debug('               ...INSIDE Dimmer')
            else:
                logging.debug('               ...OUTSIDE Dimmer')
            if dimmer.value == 0:
                dimmer.disabled = True
                self.power_button.active = False
            touch.ungrab(dimmer)

    def open_options_menu(self, button):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        rename = {'text': 'Rename Device',
                  'on_release': self.rename_device}
        info = {'text': 'Device Info',
                'on_release': self.show_device_info}
        settings = {'text': 'Settings',
                    'on_release': self.open_settings}
        menu_items = [rename, info, settings]
        self.menu = MDDropdownMenu(caller=button, items=menu_items, hor_growth='left')
        self.menu.open()

    def rename_device(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.menu.dismiss()
        _label = self.ids._label
        scrollview = self.parent.parent
        # Create a blur / disabled look
        _label.opacity = 0
        self.ids._card.opacity = 0.15
        self.ids._card_overlay.opacity = 0.75
        for child in self.ids._card.children:
            child.disabled = True
        # Get existing _label's coordinates to use for the text_field. Scrollview complicates it.
        width, height = _label.width,  _label.height
        wx, wy = _label.to_window(_label.x, _label.y)
        x, y = self.ids._card_overlay.to_widget(wx, wy)
        sx, sy = scrollview.pos  # Needed?

        self.text_field = RenameDeviceTextField(size=(width, height), pos=(x, y-dp(10)))
        self.text_field.bind(on_text_validate=self.rename_device_validate)
        self.ids._card_overlay.add_widget(self.text_field)
        scrollview.update_from_scroll()  # Should reset the view, doesn't always work

    def rename_device_validate(self, text_field):
        # print(f'`{self.__class__.__name__}.{func_name()}` called with args: {text_field}')
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {text_field}')
        name = text_field.text
        # Fail
        if not name.isalnum():
            text_field.error = True
            text_field.focus = True
            text_field.helper_text_mode = 'on_error'
            text_field.helper_text = "Name may only contain letters & numbers"
            Clock.schedule_once(self.set_text_field_focus, 0.1)
            return
        # Success
        self.device.user_assigned_alias = name
        self.ids._label.text = name
        self.ids._label.opacity = 1
        self.ids._card.opacity = 1
        self.ids._card_overlay.opacity = 0
        self.ids._card_overlay.remove_widget(self.text_field)
        for child in self.ids._card.children:
            child.disabled = False
        self.save_device()

    def set_text_field_focus(self, dt):
        text_field = self.text_field
        text_field.focus = True

    def show_device_info(self, *args):
        self.menu.dismiss()
        app = MDApp.get_running_app()
        device_info_screen = app.root_screen.screen_manager.get_screen('device_info')
        device_info_screen.device = self.device
        slide_left = SlideTransition(direction='left')
        app.root_screen.screen_manager.transition = slide_left
        app.root_screen.screen_manager.current = 'device_info'

    def open_settings(self, *args):
        # print(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.menu.dismiss()
