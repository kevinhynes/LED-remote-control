import logging
from functools import partial
from kivymd.uix.screen import MDScreen
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.screenmanager import SlideTransition

from bluetooth_helpers import Command
from troubleshooting import func_name


class ConfigureLEDsScreen(MDScreen):
    device_controller = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_corrections = {
            0: 'Typical SMD 5050',
            1: 'Typical LED Strip',
            2: 'Typical 8mm Strip',
            3: 'Typical Pixel String',
            4: 'Uncorrected Color'
        }
        self.temperature_corrections = {
            0: 'Candle',
            1: 'Tungsten 40W',
            2: 'Tungsten 100W',
            3: 'Halogen',
            4: 'Carbon Arc',
            5: 'HighNoonSun',
            6: 'Direct Sunlight',
            7: 'Overcast Sky',
            8: 'Clear Blue Sky',
            9: 'Warm Fluorescent',
            10: 'Standard Fluorescent',
            11: 'Cool White Fluorescent',
            12: 'Full Spectrum Fluorescent',
            13: 'Grow Light Fluorescent',
            14: 'Black Light Fluorescent',
            15: 'Mercury Vapor',
            16: 'Sodium Vapor',
            17: 'Metal Halide',
            18: 'Uncorrected Temperature'
        }

    def on_pre_enter(self, *args):
        app = MDApp.get_running_app()
        app.root_screen.ids.top_app_bar_.left_action_items = [['arrow-left-bold', self.go_back]]

    def on_enter(self, *args):
        color_corrections_options = [
            {'text': v, 'on_release': partial(self.color_corrections_menu_callback, k, v)}
            for k, v in self.color_corrections.items()]
        self.color_corrections_menu = MDDropdownMenu(
            caller=self.ids.color_corrections_btn_,
            items=color_corrections_options)
        temperature_corrections_options = [
            {'text': v, 'on_release': partial(self.temperature_corrections_menu_callback, k, v)}
            for k, v in self.temperature_corrections.items()]
        self.temperature_corrections_menu = MDDropdownMenu(
            caller=self.ids.temperature_corrections_btn_,
            items=temperature_corrections_options)
        self.ids.num_leds_text_field_.hint_text = \
            str(self.device_controller.device.num_leds)
        self.ids.max_brightness_text_field_.hint_text = \
            str(self.device_controller.device.max_brightness)
        self.ids.color_corrections_btn_.text = \
            self.device_controller.device.color_correction
        self.ids.temperature_corrections_btn_.text = \
            self.device_controller.device.color_temperature_correction

    # def on_kv_post(self, *args):
    #     self.ids.num_leds_text_field_.hint_text = self.device_controller.device.num_leds

    def go_back(self, *args):
        app = MDApp.get_running_app()
        slide_right = SlideTransition(direction='right')
        app.root_screen.screen_manager.transition = slide_right
        app.root_screen.screen_manager.current = 'controllers'
        open_nav_menu = lambda x: app.root_screen.ids.nav_drawer_.set_state('open')
        app.root_screen.ids.top_app_bar_.left_action_items = [['menu', open_nav_menu]]

    def validate_num_leds(self, text_field):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {text_field}')
        num_leds = text_field.text
        for char in num_leds:
            if not char.isdigit():
                text_field.error = True
                text_field.focus = True
                text_field.helper_text_mode = 'on_error'
                text_field.helper_text = "Must be whole number between 0 and 65535"
                return
        # Let the maximum number of LEDs be 65535 (way more than enough) so it can fit in 2 bytes.
        num_leds = int(num_leds)
        max_leds = 0
        for bit in range(16):
            max_leds = max_leds << 1
            max_leds += 1
        if not 0 <= num_leds <= max_leds:
            text_field.error = True
            text_field.focus = True
            text_field.helper_text_mode = 'on_error'
            text_field.helper_text = "Must be whole number between 0 and 65535"
            return
        self.device_controller.device.num_leds = num_leds
        self.device_controller.save_device()
        command = Command(mode=0, num_leds=num_leds)
        self.device_controller.send_command(command)

    def validate_brightness(self, text_field):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {text_field}')
        brightness = text_field.text
        for char in brightness:
            if not char.isdigit():
                text_field.error = True
                text_field.focus = True
                text_field.helper_text_mode = 'on_error'
                text_field.helper_text = "Must be whole number between 0 and 255"
                return
        # Brightness can be set to maximum of 255.
        brightness = int(brightness)
        max_brightness = 255
        if not 0 <= brightness <= max_brightness:
            text_field.error = True
            text_field.focus = True
            text_field.helper_text_mode = 'on_error'
            text_field.helper_text = "Must be whole number between 0 and 255"
            return
        self.device_controller.device.max_brightness = brightness
        self.device_controller.save_device()
        command = Command(mode=0, max_brightness=brightness)
        self.device_controller.send_command(command)

    def open_color_corrections_menu(self, button):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.color_corrections_menu.open()

    def color_corrections_menu_callback(self, key, color_correction):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.color_corrections_menu.dismiss()
        self.device_controller.device.color_correction = color_correction
        self.ids.color_corrections_btn_.text = color_correction
        self.device_controller.save_device()
        command = Command(mode=0, color_correction_key=key)
        self.device_controller.send_command(command)

    def open_temperature_corrections_menu(self, button):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.temperature_corrections_menu.open()

    def temperature_corrections_menu_callback(self, key, color_temperature_correction):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.temperature_corrections_menu.dismiss()
        self.device_controller.device.color_temperature_correction = color_temperature_correction
        self.ids.temperature_corrections_btn_.text = color_temperature_correction
        self.device_controller.save_device()
        command = Command(mode=0, color_temperature_correction_key=key)
        self.device_controller.send_command(command)
