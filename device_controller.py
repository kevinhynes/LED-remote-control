import asyncio
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
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRoundFlatButton, MDRectangleFlatButton
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import BaseListItem, OneLineListItem, OneLineAvatarIconListItem, \
    IRightBodyTouch
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

from device_connection_dialog import DeviceConnectionDialog, DialogContent
from troubleshooting import func_name
from bluetooth_helpers import Command

if platform == 'android':
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')

AnimationPresetButtonAttr = namedtuple('AnimationPresetButtonAttr',
                                       ('icon_filepath', 'animation', 'speed', 'palette_name',))


class AnimationPresetButton(MDIconButton, MDRoundFlatButton):
    pass


class AnimationPresetsSlide(MDBoxLayout):
    device_controller = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.presets_grid = MDGridLayout()
        self.control_grid = MDGridLayout()

    def on_kv_post(self, *args):
        presets_grid = MDGridLayout(cols=4,
                                    # md_bg_color=(1, 0, 0, 0.25),
                                    adaptive_size=True,
                                    pos_hint={'bottom': 0},
                                    padding=(dp(0), dp(10), dp(0), dp(10)),
                                    # spacing=(dp(5))
                                    )
        ap_btn_attrs = [
            AnimationPresetButtonAttr(
                icon_filepath="data/comet.png", animation=1, speed=1, palette_name='forest'),
            AnimationPresetButtonAttr(
                icon_filepath="data/bounce.png", animation=1, speed=1, palette_name='forest'),
            AnimationPresetButtonAttr(
                icon_filepath="data/star.png", animation=1, speed=1, palette_name='forest'),
            AnimationPresetButtonAttr(
                icon_filepath="data/firework.png", animation=1, speed=1, palette_name='forest'),
            AnimationPresetButtonAttr(
                icon_filepath="data/rocket.png", animation=1, speed=1, palette_name='forest'),
            AnimationPresetButtonAttr(
                icon_filepath="data/bonfire.png", animation=1, speed=1, palette_name='forest'),
            AnimationPresetButtonAttr(
                icon_filepath="data/comet.png", animation=1, speed=1, palette_name='forest'),
            AnimationPresetButtonAttr(
                icon_filepath="data/bounce.png", animation=1, speed=1, palette_name='forest'),
            AnimationPresetButtonAttr(
                icon_filepath="data/star.png", animation=1, speed=1, palette_name='forest'),
            AnimationPresetButtonAttr(
                icon_filepath="data/firework.png", animation=1, speed=1, palette_name='forest'),
            AnimationPresetButtonAttr(
                icon_filepath="data/rocket.png", animation=1, speed=1, palette_name='forest'),
            AnimationPresetButtonAttr(
                icon_filepath="data/bonfire.png", animation=1, speed=1, palette_name='forest'),
        ]

        for i in range(len(ap_btn_attrs)):
            ap_btn_attr = ap_btn_attrs[i]
            ap_btn = AnimationPresetButton(icon=ap_btn_attr.icon_filepath, )
            presets_grid.add_widget(ap_btn)

        control_grid = MDGridLayout(cols=2,
                                    # md_bg_color=(1, 0, 0, 0.25),
                                    adaptive_size=True,
                                    pos_hint={'bottom': 0},
                                    padding=(dp(0), dp(10), dp(0), dp(10)),
                                    spacing=(dp(5))
                                    )
        control_button_attrs = [
            ControlButtonAttr(color='red', icon='arrow-up-bold', rgb_inc=[5, 0, 0]),
            ControlButtonAttr(color='red', icon='arrow-down-bold', rgb_inc=[-5, 0, 0]),
            ControlButtonAttr(color='green', icon='arrow-up-bold', rgb_inc=[0, 5, 0]),
            ControlButtonAttr(color='green', icon='arrow-down-bold', rgb_inc=[0, -5, 0]),
            ControlButtonAttr(color='blue', icon='arrow-up-bold', rgb_inc=[0, 0, 5]),
            ControlButtonAttr(color='blue', icon='arrow-down-bold', rgb_inc=[0, 0, -5]),
            ControlButtonAttr(color='blue', icon='arrow-up-bold', rgb_inc=[0, 0, 0]),
            ControlButtonAttr(color='blue', icon='arrow-down-bold', rgb_inc=[0, 0, 0]),
        ]
        for i in range(8):
            control_btn_attr = control_button_attrs[i]
            control_btn = ColorPresetsSlideControlButton(
                icon=control_btn_attr.icon,
                theme_icon_color='Custom',
                icon_color=control_btn_attr.color,
                # md_bg_color=(1, 1, 1),
                size_hint=(None, None),
            )
            control_btn.bind(on_release=partial(self.device_controller.increment_rgb,
                                                control_btn_attr.rgb_inc))
            control_grid.add_widget(control_btn)
        self.control_grid = control_grid
        self.presets_grid = presets_grid
        self.add_widget(presets_grid)
        self.add_widget(control_grid)

    def on_size(self, *args):
        self.update_buttons()

    def on_pos(self, *args):
        self.update_buttons()

    def update_buttons(self):
        # Because of control_grid and color_grid adaptive_size: True
        btn_width = (self.width - dp(30)) / 6
        for btn in self.control_grid.children:
            btn.size = (btn_width, btn_width)

        for btn in self.presets_grid.children:
            btn.size = (btn_width, btn_width)
            # btn.pos = btn.x - dp(2), btn.y - dp(2)


class ColorPresetButton(MDRoundFlatButton):
    pass


class ColorPresetsSlideButton(MDRoundFlatButton):
    pass


class ColorPresetsSlideControlButton(MDIconButton):
    pass


ControlButtonAttr = namedtuple('ControlButton', ['color', 'icon', 'rgb_inc'])


class ColorPresetsSlide(MDBoxLayout):
    device_controller = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_grid = MDGridLayout()
        self.control_grid = MDGridLayout()

    def on_kv_post(self, *args):
        color_grid = MDGridLayout(cols=4,
                                  # md_bg_color=(1, 0, 0, 0.25),
                                  adaptive_size=True,
                                  pos_hint={'bottom': 0},
                                  padding=(dp(0), dp(10), dp(0), dp(10)),
                                  spacing=(dp(5))
                                  )
        control_grid = MDGridLayout(cols=2,
                                    # md_bg_color=(1, 0, 0, 0.25),
                                    adaptive_size=True,
                                    pos_hint={'bottom': 0},
                                    padding=(dp(0), dp(10), dp(0), dp(10)),
                                    spacing=(dp(5))
                                    )
        num_buttons = 16
        hue_step = 255 / num_buttons
        for i in range(0, num_buttons):
            hue = i * hue_step
            hsv = [hue / 255, 1, 1]
            rgb = colorsys.hsv_to_rgb(*hsv)
            color_preset_btn = ColorPresetsSlideButton(
                md_bg_color=rgb,
                size_hint=(None, None),
            )
            color_preset_btn.bind(on_release=partial(self.device_controller.update_rgb_sliders,
                                                     color_preset_btn.md_bg_color))
            color_grid.add_widget(color_preset_btn)
        control_button_attrs = [
            ControlButtonAttr(color='red', icon='arrow-up-bold', rgb_inc=[5, 0, 0]),
            ControlButtonAttr(color='red', icon='arrow-down-bold', rgb_inc=[-5, 0, 0]),
            ControlButtonAttr(color='green', icon='arrow-up-bold', rgb_inc=[0, 5, 0]),
            ControlButtonAttr(color='green', icon='arrow-down-bold', rgb_inc=[0, -5, 0]),
            ControlButtonAttr(color='blue', icon='arrow-up-bold', rgb_inc=[0, 0, 5]),
            ControlButtonAttr(color='blue', icon='arrow-down-bold', rgb_inc=[0, 0, -5]),
            ControlButtonAttr(color='blue', icon='arrow-up-bold', rgb_inc=[0, 0, 0]),
            ControlButtonAttr(color='blue', icon='arrow-down-bold', rgb_inc=[0, 0, 0]),
        ]
        for i in range(8):
            control_btn_attr = control_button_attrs[i]
            control_btn = ColorPresetsSlideControlButton(
                icon=control_btn_attr.icon,
                theme_icon_color='Custom',
                icon_color=control_btn_attr.color,
                # md_bg_color=(1, 1, 1),
                size_hint=(None, None),
            )
            control_btn.bind(on_release=partial(self.device_controller.increment_rgb,
                                                control_btn_attr.rgb_inc))
            control_grid.add_widget(control_btn)
        self.color_grid = color_grid
        self.control_grid = control_grid
        self.add_widget(color_grid)
        self.add_widget(control_grid)

    def on_size(self, *args):
        self.update_buttons()

    def on_pos(self, *args):
        self.update_buttons()

    def update_buttons(self):
        # Because of control_grid and color_grid adaptive_size: True
        btn_width = (self.width - dp(30)) / 6
        for btn in self.control_grid.children:
            btn.size = (btn_width, btn_width)

        for btn in self.color_grid.children:
            btn.size = (btn_width, btn_width)

    def update_rgb_sliders(self, md_bg_color, *args):
        logging.debug(
            f'`{self.__class__.__name__}.{func_name()}` called with args: {md_bg_color}')
        self.device_controller.update_rgb_sliders(md_bg_color)


class ColorPresets(MDBoxLayout):
    pass


class ColorPresetGrid(MDGridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_kv_post(self, *args):
        num_buttons = 16
        hue_step = 255 / num_buttons
        for i in range(0, num_buttons):
            hue = i * hue_step
            hsv = [hue / 255, 1, 1]
            rgb = colorsys.hsv_to_rgb(*hsv)
            color_preset_btn = ColorPresetsSlideButton(
                md_bg_color=rgb,
                size_hint=(None, None),
            )
            color_preset_btn.bind(on_release=partial(self.device_controller.update_rgb_sliders,
                                                     color_preset_btn.md_bg_color))
            self.add_widget(color_preset_btn)


class RenameDeviceTextField(MDTextField):
    pass


class DeviceController(BaseListItem):
    device = ObjectProperty()
    power_button = ObjectProperty()
    carousel = ObjectProperty()
    dimmer_container = ObjectProperty()
    dimmer = ObjectProperty()
    rgb_container = ObjectProperty()
    red_slider = ObjectProperty()
    green_slider = ObjectProperty()
    blue_slider = ObjectProperty()
    brightness = NumericProperty(100)
    r = NumericProperty(255)
    g = NumericProperty(255)
    b = NumericProperty(255)
    is_connected = BooleanProperty()
    is_expanded = BooleanProperty(False)
    off_screen = ObjectProperty()
    color_presets_slide = ObjectProperty()
    animation_presets_slide = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rename_active = False
        self.reconnection_active = True
        self.slide_num = 0
        configure_leds = {
            'text': 'Configure LEDs',
            'on_release': self.open_configure_leds_screen,
        }
        rename = {
            'text': 'Rename Device',
            'on_release': self.rename_device,
        }
        info = {
            'text': 'Device Info',
            'on_release': self.show_device_info,
        }
        reconnect = {
            'text': 'Reconnect Device',
            'on_release': self.reconnect_BluetoothSocket,
        }
        disconnect = {
            'text': 'Disconnect Device',
            'on_release': self.disconnect_BluetoothSocket,
        }
        forget = {
            'text': 'Forget Device',
            'on_release': self.forget_device,
        }
        color = {
            'text': 'Open Color Picker',
            'on_release': self.open_color_picker,
        }
        color_screen = {
            'text': 'Open Color Picker Screen',
            'on_release': self.open_color_picker_screen,
        }
        palettes = {
            'text': 'Palettes',
            'on_release': self.open_palettes_screen,
        }
        animations = {
            'text': 'Animations',
            'on_release': self.open_animations_screen,
        }
        menu_items = [configure_leds, rename, info, forget, reconnect, disconnect, forget,
                      color, color_screen, palettes, animations]
        self.menu = MDDropdownMenu(
            caller=self.ids.menu_button_,
            items=menu_items,
            hor_growth='left',
            width_mult=3)
        Clock.schedule_once(self._initialize_dimmer)
        Clock.schedule_once(self._initialize_sliders)
        Clock.schedule_once(self._initialize_switch)

    def _initialize_dimmer(self, *args):
        # Save - might be necessary for multiple controllers. Untested.
        # self.dimmer.bind(on_touch_down=self.dimmer_touch_down)
        # self.dimmer.bind(on_touch_up=self.dimmer_touch_up)
        self.dimmer.disabled = True

    def _initialize_sliders(self, *args):
        # Save - might be necessary for multiple controllers. Untested.
        # self.dimmer.bind(on_touch_down=self.red_slider_touch_down)
        # self.dimmer.bind(on_touch_up=self.red_slider_touch_up)
        # self.dimmer.bind(on_touch_down=self.green_slider_touch_down)
        # self.dimmer.bind(on_touch_up=self.green_slider_touch_up)
        # self.dimmer.bind(on_touch_down=self.blue_slider_touch_down)
        # self.dimmer.bind(on_touch_up=self.blue_slider_touch_up)
        pass

    def _initialize_switch(self, *args):
        self.power_button.ids.thumb._no_ripple_effect = True
        self.power_button.ids.thumb.ids.icon.icon = 'power'

    def on_is_connected(self, *args):
        logging.debug(
            f'`{self.__class__.__name__}.{func_name()}`\n\tis_connected: {self.is_connected}')
        if self.is_connected:
            self.ids.status_icon_.icon_color = 'green'
            self.ids.status_icon_.icon = 'bluetooth-audio'
        else:
            self.ids.status_icon_.icon_color = 'red'
            self.ids.status_icon_.icon = 'bluetooth-off'

    def on_touch_up(self, touch):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with touch: {touch}'
                      f'from device: {self.device.getAddress()}')
        if self.rename_active and not self.collide_point(touch.x, touch.y):
            Clock.schedule_once(self.exit_rename)
        # Returning False alone should work, not sure why this is necessary.
        self.ids.card_.dispatch('on_touch_up', touch)

    def open_options_menu(self, button):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.menu.open()

    def rename_device(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.menu.dismiss()
        self.rename_active = True
        label_ = self.ids.label_
        scrollview = self.parent.parent
        # Create a blur / disabled look
        label_.opacity = 0
        self.ids.card_.opacity = 0.15
        self.ids.card_overlay_.opacity = 0.75
        for child in self.ids.card_.children:
            child.disabled = True
        # Get existing label_'s coordinates to use for the text_field. Scrollview complicates it.
        width, height = label_.width, label_.height
        wx, wy = label_.to_window(label_.x, label_.y)
        x, y = self.ids.card_overlay_.to_widget(wx, wy)
        sx, sy = scrollview.pos  # Needed?

        self.text_field = RenameDeviceTextField(size=(width, height), pos=(x, y - dp(10)))
        self.text_field.bind(on_text_validate=self.rename_device_validate)
        self.ids.card_overlay_.add_widget(self.text_field)
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
        self.device.nickname = name
        self.ids.label_.text = name
        self.exit_rename()
        self.save_device()

    def set_text_field_focus(self, dt):
        text_field = self.text_field
        text_field.focus = True

    def exit_rename(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.ids.label_.opacity = 1
        self.ids.card_.opacity = 1
        self.ids.card_overlay_.opacity = 0
        self.ids.card_overlay_.remove_widget(self.text_field)
        for child in self.ids.card_.children:
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

    def open_color_picker_screen(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.menu.dismiss()
        app = MDApp.get_running_app()
        color_picker_screen = app.root_screen.screen_manager.get_screen('color_picker')
        color_picker_screen.device_controller = self
        slide_left = SlideTransition(direction='left')
        app.root_screen.screen_manager.transition = slide_left
        app.root_screen.screen_manager.current = 'color_picker'

    def open_color_picker(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.menu.dismiss()
        self.color_picker = MDColorPicker(size_hint=(0.95, 0.85))
        self.color_picker.open()
        self.color_picker.bind(
            on_select_color=self.on_select_color,
            on_release=self.get_selected_color,
        )
        # self.color_picker.ids.gradient_widget.bind(on_touch_move=self.gradient_on_touch_move)

    def open_palettes_screen(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.menu.dismiss()
        app = MDApp.get_running_app()
        palettes_screen = app.root_screen.screen_manager.get_screen('palettes')
        palettes_screen.device_controller = self
        slide_left = SlideTransition(direction='left')
        app.root_screen.screen_manager.transition = slide_left
        app.root_screen.screen_manager.current = 'palettes'

    def open_animations_screen(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.menu.dismiss()
        app = MDApp.get_running_app()
        animations_screen = app.root_screen.screen_manager.get_screen('animations')
        animations_screen.device_controller = self
        slide_left = SlideTransition(direction='left')
        app.root_screen.screen_manager.transition = slide_left
        app.root_screen.screen_manager.current = 'animations'

    # def gradient_on_touch_move(self, touch):
    #     """Handles the ``self.ids.gradient_widget`` touch event."""
    #     gradient_widget = self.color_picker.ids.gradient_widget
    #     if gradient_widget.collide_point(*touch.pos):
    #         color = gradient_widget.get_rgba_color_from_touch_region(gradient_widget, touch)
    #         self.color_picker.dispatch(
    #             "on_select_color", [x / 255.0 for x in color]
    #         )
    #     return super(Widget, self).on_touch_down(touch)

    def on_select_color(self, color_picker, rgba):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` '
                      f'called with args: {color_picker, rgba}')
        for i, color in enumerate(rgba):
            rgba[i] = int(color * 255)
        # self.send(1, rgba)

    def get_selected_color(self, instance_color_picker: MDColorPicker, type_color: str,
                           selected_color: Union[list, str], ):
        '''Return selected color.'''
        logging.debug(f'Selected color is {selected_color}')

    def carousel_change_slides(self, increment):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with : {increment}')
        # Dimmer slide...
        if self.slide_num == 0:
            self.dimmer_container.x = Window.width
        # RGB sliders...
        if self.slide_num == 1:
            self.rgb_container.x = Window.width
        # Color presets slide...
        if self.slide_num == 2:
            self.color_presets_slide.x = Window.width
        # Animation presets slide...
        if self.slide_num == 3:
            self.animation_presets_slide.x = Window.width
        self.slide_num = (self.slide_num + increment) % 4
        # Dimmer slide...
        if self.slide_num == 0:
            self.height = dp(165)
            self.ids.card_bottom_.height = dp(100)
            self.dimmer_container.x = self.x
        # RGB sliders...
        if self.slide_num == 1:
            self.height = dp(165) + dp(100)
            self.ids.card_bottom_.height = dp(100) + dp(100)
            self.rgb_container.x = self.x
        # Color presets slide...
        if self.slide_num == 2:
            self.height = dp(165) + dp(150)
            self.ids.card_bottom_.height = dp(100) + dp(150)
            self.color_presets_slide.x = self.x
        # Animation presets slide...
        if self.slide_num == 3:
            self.height = dp(165) + dp(150)
            self.ids.card_bottom_.height = dp(100) + dp(150)
            self.animation_presets_slide.x = self.x

    def open_configure_leds_screen(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.menu.dismiss()
        app = MDApp.get_running_app()
        configure_leds_screen = app.root_screen.screen_manager.get_screen('configure_leds')
        configure_leds_screen.device_controller = self
        slide_left = SlideTransition(direction='left')
        app.root_screen.screen_manager.transition = slide_left
        app.root_screen.screen_manager.current = 'configure_leds'

    def disconnect_BluetoothSocket(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        if not self.device.bluetooth_socket:
            d = MDDialog(text='No BluetoothSocket found.')
            d.open()
        elif self.device.bluetooth_socket.isConnected():
            self.device.bluetooth_socket.close()
            d = MDDialog(text='BluetoothSocket closed.')
            d.open()
        elif not self.device.bluetooth_socket.isConnected():
            d = MDDialog(text='BluetoothSocket is already closed.')
            d.open()

    @mainthread
    def reconnect_BluetoothSocket(self, *args):
        # Added @mainthread because trying to stop multiple reconnects when sending palette
        # instructions.
        logging.debug(
            f'`{self.__class__.__name__}.{func_name()}` was called with args: {args}')
        dcd = DeviceConnectionDialog(
            type='custom',
            content_cls=DialogContent(),
        )
        dcd.content_cls.label.text = 'Reconnecting to... ' + self.device.name
        dcd.content_cls.dialog = dcd  # back-reference to parent
        dcd.open()
        # Must use separate thread for connecting to Bluetooth device to keep GUI functional.
        t = Thread(target=self._reconnect_BluetoothSocket, args=[dcd])
        t.start()

    def _reconnect_BluetoothSocket(self, dcd, *args):
        logging.debug(
            f'`{self.__class__.__name__}.{func_name()}` was called with dcd, args: {dcd, args}')
        if self.device.bluetooth_socket and self.device.bluetooth_socket.isConnected():
            d = MDDialog(text='Device already connected')
            d.open()
            return
        self.reconnection_active = True
        try:
            logging.debug(f'Re-creating BluetoothSocket')
            UUID = autoclass('java.util.UUID')
            esp32_UUID = '00001101-0000-1000-8000-00805F9B34FB'
            self.device.bluetooth_socket = self.device.createRfcommSocketToServiceRecord(
                UUID.fromString(esp32_UUID))
            self.device.bluetooth_socket.connect()
            self.device.recv_stream = self.device.bluetooth_socket.getInputStream()
            self.device.send_stream = self.device.bluetooth_socket.getOutputStream()
        except Exception as e:
            logging.debug(f'Failed to open socket in DeviceController._reconnect_BluetoothSocket.'
                          f'Exception {e}')
            dcd.content_cls.update_failure(self.device)
            self.reconnection_active = False
            self.is_connected = False
        else:
            logging.debug(f'Successfully opened socket')
            dcd.content_cls.update_success(self.device)
            self.reconnection_active = False
            self.is_connected = True

    # def dimmer_touch_down(self, dimmer, touch):
    #     # Reducing the slider to 0 should also turn off the power button, but only after releasing
    #     # the slider at 0 - in case slider is moved to 0 and back up again.
    #     #
    #     # Therefore need the on_touch_up event, but if the touch_up occurs outside of the slider,
    #     # it isn't possible to know which slider it was for.
    #     #
    #     # Grab the touch event for the slider to check the touch_up event later. Don't return True
    #     # so that KivyMD's slider animations can complete.
    #     if dimmer.collide_point(touch.x, touch.y) and not dimmer.disabled:
    #         logging.debug(f'`{self.__class__.__name__}.{func_name()}` '
    #                       f'called from device: {self.device.getAddress()}')
    #         logging.debug('Grabbing touch_down INSIDE Dimmer')
    #         touch.grab(dimmer)
    #
    # def dimmer_touch_up(self, dimmer, touch):
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
    #     if touch.grab_current is dimmer:
    #         logging.debug('Found touch_up...')
    #         if dimmer.collide_point(touch.x, touch.y):
    #             logging.debug('               ...INSIDE Dimmer')
    #         else:
    #             logging.debug('               ...OUTSIDE Dimmer')
    #         if dimmer.value == 0:
    #             dimmer.disabled = True
    #             self.power_button.active = False
    #         touch.ungrab(dimmer)

    # def red_slider_touch_down(self, red_slider, touch):
    #     if red_slider.collide_point(touch.x, touch.y) and not red_slider.disabled:
    #         logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
    #         logging.debug('Grabbing touch_down INSIDE red_slider')
    #         touch.grab(red_slider)
    #
    # def red_slider_touch_up(self, red_slider, touch):
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
    #     if touch.grab_current is red_slider:
    #         logging.debug('Found touch_up...')
    #         if red_slider.collide_point(touch.x, touch.y):
    #             logging.debug('               ...INSIDE red_slider')
    #         else:
    #             logging.debug('               ...OUTSIDE red_slider')
    #         if self.red_slider.value == 0 and self.green_slider.value == 0 \
    #                 and self.blue_slider.value == 0:
    #             red_slider.disabled = True
    #             self.power_button.active = False
    #         touch.ungrab(red_slider)
    #
    # def green_slider_touch_down(self, green_slider, touch):
    #     if green_slider.collide_point(touch.x, touch.y) and not green_slider.disabled:
    #         logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
    #         logging.debug('Grabbing touch_down INSIDE green_slider')
    #         touch.grab(green_slider)
    #
    # def green_slider_touch_up(self, green_slider, touch):
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
    #     if touch.grab_current is green_slider:
    #         logging.debug('Found touch_up...')
    #         if green_slider.collide_point(touch.x, touch.y):
    #             logging.debug('               ...INSIDE green_slider')
    #         else:
    #             logging.debug('               ...OUTSIDE green_slider')
    #         if self.red_slider.value == 0 and self.green_slider.value == 0 \
    #                 and self.blue_slider.value == 0:
    #             green_slider.disabled = True
    #             self.power_button.active = False
    #         touch.ungrab(green_slider)
    #
    # def blue_slider_touch_down(self, blue_slider, touch):
    #     if blue_slider.collide_point(touch.x, touch.y) and not blue_slider.disabled:
    #         logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
    #         logging.debug('Grabbing touch_down INSIDE blue_slider')
    #         touch.grab(blue_slider)
    #
    # def blue_slider_touch_up(self, blue_slider, touch):
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
    #     if touch.grab_current is blue_slider:
    #         logging.debug('Found touch_up...')
    #         if blue_slider.collide_point(touch.x, touch.y):
    #             logging.debug('               ...INSIDE blue_slider')
    #         else:
    #             logging.debug('               ...OUTSIDE blue_slider')
    #         if self.red_slider.value == 0 and self.green_slider.value == 0 \
    #                 and self.blue_slider.value == 0:
    #             blue_slider.disabled = True
    #             self.power_button.active = False
    #         touch.ungrab(blue_slider)

    def power(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        if self.power_button.active:
            logging.debug('LIGHTS ON!')
            self.dimmer.value = self.brightness
            # self.red_slider.value = self.r
            # self.green_slider.value = self.g
            # self.blue_slider.value = self.b
            self.dimmer.disabled = False
            self.red_slider.disabled = False
            self.green_slider.disabled = False
            self.blue_slider.disabled = False
            command = Command(mode=2, dimmer_val=self.brightness)
        else:
            logging.debug('LIGHTS OFF!')
            self.brightness = self.dimmer.value
            # self.r = self.red_slider.value
            # self.g = self.green_slider.value
            # self.b = self.blue_slider.value
            # self.dimmer.value = 0
            self.dimmer.disabled = True
            self.red_slider.disabled = True
            self.green_slider.disabled = True
            self.blue_slider.disabled = True
            command = Command(mode=2, dimmer_val=0)
        self.send_command(command)

    def dim(self, dimmer):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`'
                      f'called with dimmer.value == {dimmer.value}')
        command = Command(mode=2, dimmer_val=dimmer.value)
        self.send_command(command)

    def increment_rgb(self, rgb_inc, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        red = min(max(0, self.red_slider.value + rgb_inc[0]), 255)
        green = min(max(0, self.green_slider.value + rgb_inc[1]), 255)
        blue = min(max(0, self.blue_slider.value + rgb_inc[2]), 255)
        self.update_rgb_sliders((red / 255, green / 255, blue / 255))

    def update_rgb_sliders(self, md_bg_color, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        logging.debug(f'`\tmd_bg_color: {md_bg_color}')
        r = self.red_slider.value
        g = self.green_slider.value
        b = self.blue_slider.value
        self.red_slider.value = int(md_bg_color[0] * 255)
        self.green_slider.value = int(md_bg_color[1] * 255)
        self.blue_slider.value = int(md_bg_color[2] * 255)
        # Send message even if values haven't technically changed (fixes first send issue)
        if all(c1 == c2 for c1, c2 in zip((r, g, b), (
                self.red_slider.value, self.green_slider.value, self.blue_slider.value))):
            self.send_rgb()

    def send_rgb(self, *args):
        """Triggered by any RGB sliders' on_value call"""
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        command = Command(mode=1,
                          red=self.red_slider.value,
                          green=self.green_slider.value,
                          blue=self.blue_slider.value)
        self.send_command(command)

    def send_command(self, command: Command):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` command: {command}')
        '''Check connection before sending the message'''
        if platform != 'android':
            return
        app = MDApp.get_running_app()
        if not app.bluetooth_adapter.isEnabled():
            logging.debug(f'\tDeviceController.send called without Bluetooth enabled...')
            app.enable_bluetooth()
        try:
            logging.debug(f'\tBluetoothSocket: {self.device.bluetooth_socket}')
            logging.debug(
                f'\tBluetoothSocket.isConnected(): {self.device.bluetooth_socket.isConnected()}')
            logging.debug(f'\tCommand: {command}')
        except Exception as e:
            logging.debug(f'Exception in DeviceController.send: {e}')
        if not self.device.bluetooth_socket or not self.device.bluetooth_socket.isConnected():
            logging.debug(f'\tDeviceController.send called without BluetoothSocket connected...')
            logging.warning(f'\t TRYING TO BLOCK OTHER PALETTE SENDS')
            t = Thread(target=self.reconnect_BluetoothSocket)
            t.start()
            # self.reconnect_BluetoothSocket()
        self._send_command(command)

    def _send_command(self, command: Command):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` command: {command}')
        byte0 = byte1 = byte2 = byte3 = byte4 = byte5 = -1

        # Configuration Mode
        if command.mode == 0:
            byte0 = 0
            if command.num_leds is not None:
                byte1 = 0
                bin_num_leds = bin(command.num_leds)[2:]  # get rid of '0b'
                zeros = 16 - len(bin_num_leds)
                bin_num_leds = '0' * zeros + bin_num_leds  # make sure it's 16 bits long
                left_bits = int(bin_num_leds[0:8], 2)
                right_bits = int(bin_num_leds[8:], 2)
                byte2 = left_bits
                byte3 = right_bits
            elif command.max_brightness is not None:
                byte1 = 2
                byte2 = command.max_brightness
            elif command.color_correction_key is not None:
                byte1 = 3
                byte2 = command.color_correction_key
            elif command.color_temperature_correction_key is not None:
                byte1 = 4
                byte2 = command.color_temperature_correction_key
            self._send_to_ESP32([byte0, byte1, byte2, byte3, byte4, byte5])

        # Color Mode
        elif command.mode == 1:
            byte0 = 1
            # RGB Color
            if not any(color is None for color in [command.red, command.green, command.blue]):
                byte1 = command.red
                byte2 = command.green
                byte3 = command.blue

            elif type(byte1) is list:
                # red, green, blue = val[0], val[1], val[2]
                logging.debug(f'From a ColorPicker? This wont work anymore')
            self._send_to_ESP32([byte0, byte1, byte2, byte3, byte4, byte5])

        # Dimmer Mode
        elif command.mode == 2:
            byte0 = 2
            byte1 = int(command.dimmer_val)
            self._send_to_ESP32([byte0, byte1, byte2, byte3, byte4, byte5])

        # Palettes...
        elif command.mode == 3:
            byte0 = 3
            command.mirrored = True
            if command.mirrored:
                command.hex_colors = list(command.hex_colors) + list(command.hex_colors)[::-1]
            byte1 = len(command.hex_colors)
            self._send_to_ESP32([byte0, byte1, byte2, byte3, byte4, byte5])
            for hex_color in command.hex_colors:
                rgb = webcolors.hex_to_rgb(hex_color)
                byte1, byte2, byte3, = rgb
                self._send_to_ESP32([byte0, byte1, byte2, byte3, byte4, byte5])

        # Animations...
        elif command.mode == 4:
            byte0 = 4
            byte1 = command.animation_id
            self._send_to_ESP32([byte0, byte1, byte2, byte3, byte4, byte5])

    def _send_to_ESP32(self, send_bytes: List[int]) -> None:
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with bytes {send_bytes}')
        send_bytes = [int(b) for b in send_bytes]
        try:
            for b in send_bytes:
                if b == -1:
                    self.device.send_stream.write(struct.pack('<b', b))
                else:
                    self.device.send_stream.write(struct.pack('<B', b))
            self.device.send_stream.flush()
        except jnius.JavaException as e:
            # if isinstance(e.__java__object__, jnius.JavaIOException):
            #     # Handle the IOException (Broken pipe) error
            #     logging.debug("IOException occurred: Broken pipe")
            #     # Perform any necessary cleanup or recovery actions
            logging.debug(
                f'During device_controller._send_to_ESP32, a Java exception occurred: {e}')
        except Exception as e:
            # Handle any other Python exceptions
            logging.debug(
                f'During device_controller._send_to_ESP32, a Python exception occurred: {e}')
            # Perform appropriate actions for other exceptions
        else:
            logging.debug('Command sent.')
