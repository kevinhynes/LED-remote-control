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

from device_controller import DeviceController
from bluetooth_helpers import Command
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


class RootScreen(MDScreen):
    screen_manager = ObjectProperty()

    def open_nav_drawer(self, *args):
        self.ids._nav_drawer.set_state('open')
