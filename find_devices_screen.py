import logging
from functools import partial
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineListItem, OneLineRightIconListItem
from kivymd.uix.button import MDFlatButton
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivymd.uix.dialog import MDDialog

from troubleshooting import func_name


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
        """Connected to App.loaded_devices on .kv side."""
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
        """Connected to App.paired_devices on .kv side."""
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
