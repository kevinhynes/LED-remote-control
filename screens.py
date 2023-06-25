from functools import partial
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineListItem

from components import *


def func_name():
    return sys._getframe(1).f_code.co_name


class FindDevicesScreen(MDScreen):
    bonded_devices = ListProperty()
    bonded_devices_list = ObjectProperty()
    available_devices = ListProperty()
    available_devices_list = ObjectProperty()

    def on_bonded_devices(self, *args):
        print(f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        buttons_to_remove = [child for child in self.bonded_devices_list.children]
        for child in buttons_to_remove:
            self.bonded_devices_list.remove_widget(child)
        app = MDApp.get_running_app()
        if platform == 'android':
            for device in self.bonded_devices:
                button = BTDeviceListItem(text=device.getName(), secondary_text=device.getAddress())
                button.bind(on_press=partial(app.connect_as_client, device))
                self.bonded_devices_list.add_widget(button)
        if platform == 'linux':
            for device in self.bonded_devices:
                button = BTDeviceListItem(text=device.name, secondary_text=device.address)
                button.bind(on_press=partial(app.connect_as_client, device))
                self.bonded_devices_list.add_widget(button)

    def on_available_devices(self, *args):
        print(f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        buttons_to_remove = [child for child in self.avaiable_devices_list.children]
        for child in buttons_to_remove:
            self.available_devices_list.remove_widget(child)
        app = MDApp.get_running_app()
        for device in self.available_devies:
            button = BTDeviceListItem(text=device.name, secondary_text=device.address)
            button.bind(on_press=partial(app.connect_as_client, device))
            self.available_devices_list.add_widget(button)


class ControlScreen(MDScreen):
    connected_devices = ListProperty()
    connected_devices_list = ObjectProperty()

    def on_connected_devices(self, *args):
        print(f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        buttons_to_remove = [child for child in self.connected_devices_list.children]
        for child in buttons_to_remove:
            self.connected_devices_list.remove_widget(child)
        if platform == 'android':
            for device in self.connected_devices:
                controller = DeviceController(device=device)
                self.connected_devices_list.add_widget(controller)
        if platform == 'linux':
            for device in self.connected_devices:
                controller = DeviceController(device=device)
                self.connected_devices_list.add_widget(controller)


class DeviceInfoScreen(MDScreen):
    info_list = ObjectProperty()
    device = ObjectProperty()

    def on_pre_enter(self, *args):
        app = MDApp.get_running_app()
        app.root_screen.ids._top_app_bar.left_action_items = [['arrow-left-bold', self.go_back]]

    def on_device(self, *args):
        labels_to_remove = [child for child in self.info_list.children]
        app = MDApp.get_running_app()
        for child in labels_to_remove:
            self.info_list.remove_widget(child)
        if platform == 'android':
            for k, v in app.get_device_info(self.device).items():
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

        if platform == 'linux':
            for attr in [self.device.name, self.device.address, self.device.alias]:
                line_item = DeviceInfoListItem('key', attr)
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




