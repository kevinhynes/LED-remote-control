import asyncio
import random
import sys
import string
import logging
import jnius
import struct
from functools import partial
from kivy.core.window import Window
from kivy.clock import mainthread
from kivy.properties import NumericProperty, ListProperty, ObjectProperty, StringProperty
from kivy.metrics import dp, sp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRoundFlatButton, MDRectangleFlatButton
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import BaseListItem, OneLineListItem, OneLineAvatarIconListItem, IRightBodyTouch
from kivymd.uix.card import MDCard
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.slider import MDSlider
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.pickers import MDColorPicker
from kivy.uix.modalview import ModalView

from troubleshooting import *


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
        self.rename_active = False
        rename = {'text': 'Rename Device',
                  'on_release': self.rename_device,
                  'viewclass': 'OneLineListItem',
                  'height': dp(54)
                  }
        info = {'text': 'Device Info',
                'on_release': self.show_device_info,
                'viewclass': 'OneLineListItem',
                'height': dp(54)
                }
        settings = {'text': 'Settings',
                    'on_release': self.open_settings,
                    'viewclass': 'OneLineListItem',
                    'height': dp(54)
                    }
        forget = {'text': 'Forget Device',
                  'on_release': self.forget_device,
                  'viewclass': 'OneLineListItem',
                  'height': dp(54)
                  }
        menu_items = [rename, info, settings, forget]
        self.menu = MDDropdownMenu(caller=self.ids._menu_button,
                                   items=menu_items,
                                   hor_growth='left',
                                   width_mult=3)
        Clock.schedule_once(self._initialize_slider, 0.5)
        Clock.schedule_once(self._initialize_switch, 1.65)

    def _initialize_slider(self, *args):
        # In order for the thumb icon to show the off ring at value == 0 when MDSlider is just
        # instantiated, change it and then change it back to 0.

        # This might not be working / necessary anymore
        # self.dimmer.value = -1
        # self.dimmer.value = 0
        self.dimmer.disabled = True
        self.dimmer.bind(on_touch_down=self.dimmer_touch_down)
        self.dimmer.bind(on_touch_up=self.dimmer_touch_up)

    def _initialize_switch(self, *args):
        self.power_button.ids.thumb._no_ripple_effect = True
        self.power_button.ids.thumb.ids.icon.icon = 'power'

    def on_touch_up(self, touch):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with touch: {touch}')
        if self.rename_active and not self.collide_point(touch.x, touch.y):
            Clock.schedule_once(self.exit_rename)
        # Returning False alone should work, not sure why this is necessary.
        self.ids._card.dispatch('on_touch_up', touch)

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
        self.send(2, dimmer.value)

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
        self.menu.open()

    def rename_device(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.menu.dismiss()
        self.rename_active = True
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
        self.exit_rename()
        self.save_device()

    def set_text_field_focus(self, dt):
        text_field = self.text_field
        text_field.focus = True

    def exit_rename(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.ids._label.opacity = 1
        self.ids._card.opacity = 1
        self.ids._card_overlay.opacity = 0
        self.ids._card_overlay.remove_widget(self.text_field)
        for child in self.ids._card.children:
            child.disabled = False
        self.rename_active = False

    def save_device(self):
        app = MDApp.get_running_app()
        app.save_device(self.device)

    def forget_device(self, *args):
        self.menu.dismiss()
        app = MDApp.get_running_app()
        app.forget_device(self.device)

    def show_device_info(self, *args):
        self.menu.dismiss()
        app = MDApp.get_running_app()
        device_info_screen = app.root_screen.screen_manager.get_screen('device_info')
        device_info_screen.device = self.device
        slide_left = SlideTransition(direction='left')
        app.root_screen.screen_manager.transition = slide_left
        app.root_screen.screen_manager.current = 'device_info'

    def open_settings(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.menu.dismiss()
        color_picker = MDColorPicker(size_hint=(None, None),
                                     size=(dp(250), dp(400)))
        color_picker.bind(on_select_color=self.on_select_color)
        color_picker.open()

    def on_select_color(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')

    def launch_color_picker(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        color_picker = MDColorPicker(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            # size_hint=(None, None),
            # size=Window.size
        )
        color_picker.bind(on_select_color=self.on_select_color)
        color_picker.open()

    def send(self, mode, val):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        logging.debug(f'\tmode={mode}, val={val}')
        red, green, blue = [0, 0, 0]
        brightness = 100
        # Color Mode - ESP32 will maintain it's current brightness level.
        if mode == 1:
            # White
            if val == 1:
                red, green, blue = [255, 255, 255]
            # Red
            elif val == 2:
                red, green, blue = [255, 0, 0]
            # Orange
            elif val == 3:
                red, green, blue = [255, 130, 0]
            # Yellow
            elif val == 4:
                red, green, blue = [255, 255, 0]
            # Green
            elif val == 5:
                red, green, blue = [0, 255, 0]
            # Blue
            elif val == 6:
                red, green, blue = [0, 0, 255]

        # Dimmer Mode - ESP32 will maintain it's current color.
        if mode == 2:
            brightness = int(val)
        try:
            self.device.send_stream.write(struct.pack('<B', mode))
            self.device.send_stream.write(struct.pack('<B', red))
            self.device.send_stream.write(struct.pack('<B', green))
            self.device.send_stream.write(struct.pack('<B', blue))
            self.device.send_stream.write(struct.pack('<B', brightness))
            self.device.send_stream.write(struct.pack('<b', -1))
            self.device.send_stream.flush()
        except jnius.JavaException as e:
            if isinstance(e.__java__object__, jnius.JavaIOException):
                # Handle the IOException (Broken pipe) error
                logging.debug("IOException occurred: Broken pipe")
                # Perform any necessary cleanup or recovery actions
            else:
                # Handle other types of Java exceptions
                logging.debug(f'Other Java exception occurred: {e}')
                # Perform appropriate actions for other exceptions
        except Exception as e:
            # Handle any other Python exceptions
            logging.debug(f'Python exception occurred: {e}')
            # Perform appropriate actions for other exceptions
        else:
            logging.debug('Command sent.')