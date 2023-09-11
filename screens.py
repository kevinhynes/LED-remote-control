import logging
from functools import partial
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineListItem, OneLineRightIconListItem
from kivymd.uix.button import MDFlatButton
from typing import Union
from kivymd.uix.pickers import MDColorPicker
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import BaseListItem, OneLineIconListItem, TwoLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.screenmanager import SlideTransition

from kivymd.uix.widget import Widget
from kivy.graphics import Color
import webcolors
from kivy_gradient import Gradient

from itertools import chain
from kivy.graphics.texture import Texture
from kivy.graphics import RoundedRectangle
from kivy.utils import get_color_from_hex

# from components import *
from device_controller import DeviceController
from bluetooth_helpers import Command
import palettes
from troubleshooting import func_name


########## Find Devices Screen ##########
class PairedDevicesHeader(OneLineListItem):
    info_button = ObjectProperty()

    def give_info(self, *args):
        app = MDApp.get_running_app()
        d = MDDialog(title="Don't see your microcontroller?",
                     text="Use your phone's Bluetooth menu to pair with your microcontroller first, "
                          "then is should appear in this list.",
                     buttons=[MDFlatButton(text='Open Bluetooth Menu',
                                           on_release=lambda x: app.open_bluetooth_settings())]
                     )
        d.open()


class BTDeviceListItem(TwoLineAvatarIconListItem):
    pass


class FindDevicesScreen(MDScreen):
    loaded_devices = ListProperty()
    loaded_devices_list = ObjectProperty()
    paired_devices = ListProperty()
    paired_devices_list = ObjectProperty()

    def on_pre_enter(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        app = MDApp.get_running_app()
        app.get_paired_devices()

    def on_loaded_devices(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        saved_device_list_items_to_remove = [child for child in self.loaded_devices_list.children]
        for device_list_item in saved_device_list_items_to_remove:
            self.loaded_devices_list.remove_widget(device_list_item)
        for device in self.loaded_devices:
            button = BTDeviceListItem(text=device.getName(),
                                      secondary_text=device.getAddress(),
                                      disabled=True)
            self.loaded_devices_list.add_widget(button)

    def on_paired_devices(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        buttons_to_remove = [child for child in self.paired_devices_list.children]
        for child in buttons_to_remove:
            self.paired_devices_list.remove_widget(child)
        app = MDApp.get_running_app()
        for device in self.paired_devices:
            button = BTDeviceListItem(text=device.getName(),
                                      secondary_text=device.getAddress())
            button.bind(on_press=partial(app.connect_as_client, device))
            self.paired_devices_list.add_widget(button)


########## Device Controller Screen ##########
class ControllersScreen(MDScreen):
    loaded_devices = ListProperty()
    controllers_list = ObjectProperty()

    def on_loaded_devices(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        controllers_to_remove = [child for child in self.controllers_list.children]
        for controller in controllers_to_remove:
            self.controllers_list.remove_widget(controller)
        for device in self.loaded_devices:
            controller = DeviceController(device=device)
            self.controllers_list.add_widget(controller)

    def update_controller_connection_status(self, device_address, is_connected):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: '
                      f'{device_address, is_connected}`')
        for controller in self.controllers_list.children:
            if controller.device.getAddress() == device_address:
                controller.is_connected = is_connected
                break


########## Device Info Screen ##########
class DeviceInfoListItem(BaseListItem):
    heading_label = ObjectProperty()
    content_label = ObjectProperty()

    def __init__(self, heading='', content='', **kwargs):
        super().__init__(**kwargs)
        self.heading_label.text = heading
        self.content_label.text = content


class DeviceInfoScreen(MDScreen):
    info_list = ObjectProperty()
    device = ObjectProperty()

    def on_pre_enter(self, *args):
        app = MDApp.get_running_app()
        app.root_screen.ids._top_app_bar.left_action_items = [['arrow-left-bold', self.go_back]]
        if self.device:
            self.on_device()

    def on_device(self, *args):
        labels_to_remove = [child for child in self.info_list.children]
        for child in labels_to_remove:
            self.info_list.remove_widget(child)
        device_info = self.device.get_device_info()
        for k, v in device_info.items():
            if k == 'UUIDs':
                content_text = ''
                uuid_count = 0
                for uuid in v:
                    content_text += uuid.toString()
                    content_text += '\n'
                    uuid_count += 1
                if uuid_count > 1:
                    content_text = content_text[:-1]
                line_item = DeviceInfoListItem(k, content_text)
            else:
                line_item = DeviceInfoListItem(k, str(v))
            self.info_list.add_widget(line_item)

    def go_back(self, *args):
        app = MDApp.get_running_app()
        slide_right = SlideTransition(direction='right')
        app.root_screen.screen_manager.transition = slide_right
        app.root_screen.screen_manager.current = 'controllers'
        open_nav_menu = lambda x: app.root_screen.ids._nav_drawer.set_state('open')
        app.root_screen.ids._top_app_bar.left_action_items = [['menu', open_nav_menu]]


class ColorPickerScreen(MDScreen):
    device_controller = ObjectProperty()

    def on_pre_enter(self, *args):
        app = MDApp.get_running_app()
        app.root_screen.ids._top_app_bar.left_action_items = [['arrow-left-bold', self.go_back]]

    def on_enter(self, *args):
        self.open_color_picker()

    def go_back(self, *args):
        app = MDApp.get_running_app()
        slide_right = SlideTransition(direction='right')
        app.root_screen.screen_manager.transition = slide_right
        app.root_screen.screen_manager.current = 'controllers'
        open_nav_menu = lambda x: app.root_screen.ids._nav_drawer.set_state('open')
        app.root_screen.ids._top_app_bar.left_action_items = [['menu', open_nav_menu]]

    def open_color_picker(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.color_picker = MDColorPicker(size_hint=(0.85, 0.85))
        self.color_picker.bind(
            on_select_color=self.on_select_color,
            on_release=self.get_selected_color,
            on_open=self.remove_color_type_buttons
        )
        self.color_picker.open()

    def on_select_color(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')

    def get_selected_color(self, instance_color_picker: MDColorPicker, type_color: str,
                           selected_color: Union[list, str], ):
        '''Return selected color.'''

        logging.debug(f'Selected color is {selected_color}')

    def remove_color_type_buttons(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.color_picker.remove_widget(self.color_picker.ids.type_color_button_box)


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
        app.root_screen.ids._top_app_bar.left_action_items = [['arrow-left-bold', self.go_back]]

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

    def go_back(self, *args):
        app = MDApp.get_running_app()
        slide_right = SlideTransition(direction='right')
        app.root_screen.screen_manager.transition = slide_right
        app.root_screen.screen_manager.current = 'controllers'
        open_nav_menu = lambda x: app.root_screen.ids._nav_drawer.set_state('open')
        app.root_screen.ids._top_app_bar.left_action_items = [['menu', open_nav_menu]]

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


########## Palettes Screen ##########
class GradientWidget(MDBoxLayout):

    def __init__(self, colors, **kwargs):
        super().__init__(**kwargs)
        # Right now only works for hex values in string form
        colors = [str(color) for color in colors]
        self.gradient = RoundedRectangle()
        gradient_texture = Gradient.horizontal(*[get_color_from_hex(color) for color in colors])
        with self.canvas:
            Color(1, 1, 1)  # Set color to white, not sure why this is necessary.
            self.gradient = RoundedRectangle(size=self.size, pos=self.pos, texture=gradient_texture)
            self.bind(pos=self.update_gradient, size=self.update_gradient)

    def update_gradient(self, *args):
        self.gradient.pos = self.pos
        self.gradient.size = self.size


class PaletteWidget(MDRelativeLayout):

    def __init__(self, device_controller, colors, **kwargs):
        super().__init__(**kwargs)
        self.device_controller = device_controller
        self.colors = colors
        self.gradient_widget = GradientWidget(colors)
        self.button = MDFlatButton(pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                   size_hint=(1, 1))
        self.button.bind(on_press=self.send_palette)
        self.add_widget(self.gradient_widget)
        self.add_widget(self.button)

    def send_palette(self, *args):
        command = Command(mode=3)
        self.device_controller.send_command(command)


class PalettesScreen(MDScreen):
    grid = ObjectProperty()
    device_controller = ObjectProperty()

    def __init__(self, **kwargs):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        super().__init__(**kwargs)
        # Reduce palettes to their hex values.
        self.palettes = []
        for named_palette in palettes.palettes:
            for palette_name in named_palette.keys():
                self.palettes.append(named_palette[palette_name].values())

    def on_pre_enter(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        for palette in self.palettes:
            self.ids.grid_.add_widget(PaletteWidget(
                device_controller=self.device_controller,
                colors=palette)
            )


class RootScreen(MDScreen):
    screen_manager = ObjectProperty()
