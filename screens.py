from functools import partial
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

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


class RootScreen(MDScreen):
    pass



