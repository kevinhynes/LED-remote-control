import logging
from kivymd.uix.screen import MDScreen
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.list import BaseListItem, OneLineIconListItem, TwoLineListItem
from kivy.uix.screenmanager import SlideTransition

from troubleshooting import func_name


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
        app.root_screen.ids.top_app_bar_.left_action_items = [['arrow-left-bold', self.go_back]]
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
        open_nav_menu = lambda x: app.root_screen.ids.nav_drawer_.set_state('open')
        app.root_screen.ids.top_app_bar_.left_action_items = [['menu', open_nav_menu]]