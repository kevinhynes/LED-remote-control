import logging
from kivymd.uix.screen import MDScreen
from typing import Union
from kivymd.uix.pickers import MDColorPicker
from kivy.properties import ListProperty, ObjectProperty
from kivymd.app import MDApp
from kivy.uix.screenmanager import SlideTransition

from device_controller import DeviceController
from troubleshooting import func_name


########## Device Controller Screen ##########
class ControllersScreen(MDScreen):
    loaded_devices = ListProperty()
    controllers_list = ObjectProperty()

    def on_loaded_devices(self, *args):
        """Connected to App.loaded_devices on .kv side."""
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        controllers_to_remove = [child for child in self.controllers_list.children]
        for controller in controllers_to_remove:
            self.controllers_list.remove_widget(controller)
        for device in self.loaded_devices:
            controller = DeviceController(device=device)
            self.controllers_list.add_widget(controller)

    def update_controller_connection_status(self, device_address, is_connected):
        # This runs before the controller is done being added.  Sort of fixed by creating controller
        # with the bluetooth connected symbol to start.
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: '
                      f'{device_address, is_connected}`')
        for controller in self.controllers_list.children:
            logging.debug(f'\t {controller.device.getAddress()}  ,   {device_address}')
            if controller.device.getAddress() == device_address:
                controller.is_connected = is_connected
                break


class ColorPickerScreen(MDScreen):
    device_controller = ObjectProperty()

    def on_pre_enter(self, *args):
        app = MDApp.get_running_app()
        app.root_screen.ids.top_app_bar_.left_action_items = [['arrow-left-bold', self.go_back]]

    def on_enter(self, *args):
        self.open_color_picker()

    def go_back(self, *args):
        app = MDApp.get_running_app()
        slide_right = SlideTransition(direction='right')
        app.root_screen.screen_manager.transition = slide_right
        app.root_screen.screen_manager.current = 'controllers'
        open_nav_menu = lambda x: app.root_screen.ids.nav_drawer_.set_state('open')
        app.root_screen.ids.top_app_bar_.left_action_items = [['menu', open_nav_menu]]

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

    def open_nav_drawer_(self, *args):
        self.ids.nav_drawer_.set_state('open')
