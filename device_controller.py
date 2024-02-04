from math import pi, sin, trunc
import logging
import jnius
import struct
import webcolors
import colorsys
from collections import namedtuple
from typing import List
from threading import Thread
from jnius import cast, autoclass
from functools import partial
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.clock import mainthread
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty
from kivy.metrics import dp, sp
from kivy.graphics import Color, Line, Rectangle
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.button import MDIconButton, MDRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import BaseListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.selectioncontrol import MDCheckbox

from device_connection_dialog import DeviceConnectionDialog, DialogContent
from troubleshooting import func_name
from bluetooth_helpers import Command

if platform == 'android':
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')

AnimationPresetButtonAttr = namedtuple('AnimationPresetButtonAttr',
                                       ('icon_filepath', 'animation', 'speed', 'palette_name',))


class Drawer(MDRelativeLayout):
    # control_panel should point to the instance's "control panel" in .kv rule.
    control_panel = ObjectProperty()

    def open_drawer(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.height = self.control_panel.height + dp(20)
        self.control_panel.x = dp(0)

    def close_drawer(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.height = dp(20)
        self.control_panel.x = Window.width

    def toggle_drawer(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        if self.height == dp(20):
            self.open_drawer()
        else:
            self.close_drawer()


class RGBDrawer(Drawer):
    device_controller = ObjectProperty()


class Presets(MDBoxLayout):
    pass


class ColorPresets(MDGridLayout):
    device_controller = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_device_controller(self, *args):
        num_buttons = 20
        hue_step = 255 / num_buttons
        for i in range(0, num_buttons):
            hue = i * hue_step
            hsv = [hue / 255, 1, 1]
            rgb = colorsys.hsv_to_rgb(*hsv)
            color_preset_btn = ColorPresetButton(
                md_bg_color=rgb,
            )
            color_preset_btn.bind(on_release=partial(self.device_controller.update_rgb_sliders,
                                                     color_preset_btn.md_bg_color))
            self.add_widget(color_preset_btn)


class WhitePresets(MDGridLayout):
    device_controller = ObjectProperty()

    def on_device_controller(self, *args):
        for i in range(4):
            rgb = (1, 1, (255 - i * 30) / 255)
            color_preset_btn = ColorPresetButton(
                md_bg_color=rgb,
            )
            color_preset_btn.bind(on_release=partial(self.device_controller.update_rgb_sliders,
                                                     color_preset_btn.md_bg_color))
            self.add_widget(color_preset_btn)


class ColorPresetButton(MDRoundFlatButton):
    pass


class WaveDrawer(Drawer):
    device_controller = ObjectProperty()
    frequency = NumericProperty(10)
    range_min = NumericProperty(0)
    range_max = NumericProperty(255)
    speed = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._animation = None
        self._phase_offset = 0
        self._active_wave_option = 'hue'
        self._active_strip_option = 'strip'
        self.wave_debounce = False
        self.strip_debounce = False
        # Clock.schedule_once(self.draw_wave)

    def close_drawer(self, *args):
        super().close_drawer()
        self.ids.graph_.canvas.before.clear()

    def open_drawer(self, *args):
        super().open_drawer()
        Clock.schedule_once(self.draw_wave)

    def on_kv_post(self, *args):
        mac_address = self.device_controller.device.getAddress()
        for box in self.ids.wave_options_.children:
            for child in box.children:
                if isinstance(child, WaveOptionRadioButton):
                    child.group = mac_address + '1'
        for box in self.ids.strip_options_.children:
            for child in box.children:
                if isinstance(child, WaveOptionRadioButton):
                    child.group = mac_address + '2'
        self.ids.animate_button_.group = mac_address + '3'

    def on_frequency(self, *args):
        self.draw_wave()

    def on_range_min(self, *args):
        self.draw_wave()

    def on_range_max(self, *args):
        self.draw_wave()

    def on_speed(self, *args):
        if self._animation:
            self.draw_wave()

    def draw_wave(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.ids.graph_.canvas.before.clear()
        points = []
        wave_height = self.ids.graph_.height - dp(30)  # Adds vertical 'padding' for labels
        amplitude = abs(self.range_max - self.range_min)
        normalized_amplitude = (amplitude / 255) * (wave_height / 2)
        x0, y0 = self.ids.graph_.pos
        xi = trunc(self.ids.graph_.width)
        range_midpoint = (self.range_max + self.range_min) / 2
        ym = y0 + (range_midpoint / 255) * wave_height + dp(15)
        self.ids.x_axis_lbl_.center_y = ym - self.ids.wave_options_.height - dp(20)
        self.ids.x_axis_lbl_.text = str(range_midpoint) + ' '
        _frame_offset = 0.5 * pi * (self.speed/100)  # when new frame value == pi it just flip flops
        self._phase_offset = (self._phase_offset + _frame_offset) % (2 * pi)
        for x in range(xi):
            points.append(x0 + x)
            points.append(sin(self.frequency * (x / xi) + self._phase_offset) * normalized_amplitude + ym)
        with self.ids.graph_.canvas.before:
            # Sin Wave
            Color(1, 0, 0, 1)
            Line(points=points)
            # Background
            Color(1, 1, 1, 0.1)
            Rectangle(pos=self.ids.graph_.pos, size=self.ids.graph_.size)
            # X-Axis
            Color(0, 0, 0, 1)
            Line(points=(x0, ym, xi + x0, ym))

    def on_wave_option_active(self, radio_button):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` \t '
                      f'{radio_button.state, radio_button.active, radio_button.value}')
        if self.wave_debounce:
            self.wave_debounce = False
            return
        if radio_button.value == self._active_wave_option:
            radio_button.active = True
            self.wave_debounce = True
        else:
            self._active_wave_option = radio_button.value

    def on_strip_option_active(self, radio_button):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` \t '
                      f'{radio_button.state, radio_button.active, radio_button.value}')
        if self.strip_debounce:
            self.strip_debounce = False
            return
        if radio_button.value == self._active_strip_option:
            radio_button.active = True
            self.strip_debounce = True
        else:
            self._active_strip_option = radio_button.value

    def on_animation_active(self, radio_button):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` \t '
                      f'{radio_button.state, radio_button.active, radio_button.value}')
        if radio_button.active:
            self._animation = Clock.schedule_interval(self.draw_wave, 0.05)
        else:
            self._animation.cancel()
            self._animation = None


class WaveOptionRadioButton(MDCheckbox):
    pass


class PaletteDrawer(Drawer):
    device_controller = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def close_drawer(self, *args):
        super().close_drawer()
        self.control_panel.unbind(height=self._update_height)

    def open_drawer(self, *args):
        super().open_drawer()
        self.control_panel.bind(height=self._update_height)

    def _update_height(self, *args):
        # PaletteDrawer contains the AnimationsList, which can also grow in height when its
        # AnimationExpansionPanels have been expanded.  In that case, PaletteDrawer should also
        # grow in height to visually contain the AnimationsList.  Previously this was done in .kv
        # (height: pallette_cp_.height + dp(20)) but requries closing the drawer on start-up.
        self.height = self.control_panel.height + dp(20)


class FavoriteButton(MDRoundFlatButton):
    pass


class RenameDeviceTextField(MDTextField):
    pass


class DeviceController(MDRelativeLayout):
    device = ObjectProperty()
    power_button = ObjectProperty()
    carousel = ObjectProperty()
    dimmer_container = ObjectProperty()
    dimmer = ObjectProperty()
    rgb_container = ObjectProperty()
    red_slider = ObjectProperty()
    green_slider = ObjectProperty()
    blue_slider = ObjectProperty()
    presets = ObjectProperty()
    brightness = NumericProperty(100)
    # r = NumericProperty(255)
    # g = NumericProperty(255)
    # b = NumericProperty(255)
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
        palettes = {
            'text': 'Palettes',
            'on_release': self.open_palettes_screen,
        }
        animations = {
            'text': 'Animations',
            'on_release': self.open_animations_screen,
        }
        menu_items = [configure_leds, rename, info, forget, palettes, animations]
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
            self.presets.disabled = False
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
            self.presets.disabled = True
            command = Command(mode=2, dimmer_val=0)
        self.send_command(command)

    def dim(self, dimmer):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`'
                      f'called with dimmer.value == {dimmer.value}')
        command = Command(mode=2, dimmer_val=dimmer.value)
        self.send_command(command)

    def update_rgb_sliders(self, md_bg_color, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        # logging.debug(f'`\tmd_bg_color: {md_bg_color}')
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
        byte0 = byte1 = byte2 = byte3 = byte4 = byte5 = 0

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
            byte1 = len(command.hex_colors)
            if command.is_mirrored:
                byte2 = 1
            if command.is_blended:
                byte3 = 1
            self._send_to_ESP32([byte0, byte1, byte2, byte3, byte4, byte5])
            for hex_color in command.hex_colors:
                rgb = webcolors.hex_to_rgb(hex_color)
                byte1, byte2, byte3, = rgb
                self._send_to_ESP32([byte0, byte1, byte2, byte3, byte4, byte5])

        # Animations...
        elif command.mode == 4:
            byte0 = 4
            byte1 = command.animation_id
            byte2 = command.animation_speed
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
