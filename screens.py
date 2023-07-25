from functools import partial
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivy.event import EventDispatcher

from components import *


########## Find Devices Screen ##########

class BTDeviceListItem(TwoLineAvatarIconListItem):
    pass


class FindDevicesScreen(MDScreen):
    paired_devices = ListProperty()
    paired_devices_list = ObjectProperty()
    available_devices = ListProperty()
    available_devices_list = ObjectProperty()

    def on_pre_enter(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        app = MDApp.get_running_app()
        app.find_bluetooth_devices()

    def on_paired_devices(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        buttons_to_remove = [child for child in self.paired_devices_list.children]
        for child in buttons_to_remove:
            self.paired_devices_list.remove_widget(child)
        app = MDApp.get_running_app()
        for device in self.paired_devices:
            button = BTDeviceListItem(text=device.getName(), secondary_text=device.getAddress())
            button.bind(on_press=partial(app.connect_as_client, device))
            self.paired_devices_list.add_widget(button)

    def on_available_devices(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        buttons_to_remove = [child for child in self.avaiable_devices_list.children]
        for child in buttons_to_remove:
            self.available_devices_list.remove_widget(child)
        app = MDApp.get_running_app()
        for device in self.available_devies:
            button = BTDeviceListItem(text=device.name, secondary_text=device.address)
            button.bind(on_press=partial(app.connect_as_client, device))
            self.available_devices_list.add_widget(button)


########## Device Controller Screen ##########

class ControlScreen(MDScreen):
    connected_devices = ListProperty()
    connected_devices_list = ObjectProperty()

    def on_connected_devices(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        # add_device_button = self.ids._add_device_button
        buttons_to_remove = [child for child in self.connected_devices_list.children]
        for child in buttons_to_remove:
            self.connected_devices_list.remove_widget(child)
        for device in self.connected_devices:
            controller = DeviceController(device=device)
            self.connected_devices_list.add_widget(controller)

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
        app.root_screen.screen_manager.current = 'connected_devices'
        open_nav_menu = lambda x: app.root_screen.ids._nav_drawer.set_state('open')
        app.root_screen.ids._top_app_bar.left_action_items = [['menu', open_nav_menu]]


class MainScreen(MDScreen):
    pass


class RootScreen(MDScreen):
    screen_manager = ObjectProperty()
