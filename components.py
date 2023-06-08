import asyncio
import random
import sys
import string
from functools import partial
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.dialog import MDDialog

from troubleshooting import *


def func_name():
    return sys._getframe(1).f_code.co_name


class BTDeviceListItem(TwoLineAvatarIconListItem):
    pass


class FakeDevice:
    def __init__(self):
        self.name = self.generate_name()
        self.address = self.generate_MAC()
        self.is_connected = False

    @staticmethod
    def generate_MAC():
        num = str(random.randrange(10000000, 99999999))
        address = num[:2] + ':' + num[2:4] + ':' + num[4:6] + ':' + num[6:]
        return address

    @staticmethod
    def generate_name():
        lower = random.sample(string.ascii_lowercase, 8)
        upper = random.sample(string.ascii_uppercase, 2)
        temp_name = lower + upper
        random.shuffle(temp_name)
        name = ''.join(temp_name)
        return name

    def connect_as_client(self, *args):
        print(f'`{self.__class__.__name__}.{func_name()}`')
        asyncio.create_task(self._connect_as_client())

    async def _connect_as_client(self, *args):
        print(f'Request for {self.address} received with args: {args}')
        dcd = DeviceConnectionDialog(
            title="gay",
            type='custom',
            content_cls=DialogContent(),
        )
        dcd.content_cls.label.text = 'Connecting to... ... ... ' * 10 + self.name
        dcd.content_cls.dialog = dcd #???
        dcd.open()
        await asyncio.sleep(1)

        if random.choice([0, 1]):
            self.is_connected = True
            dcd.content_cls.update_success(self)
        else:
            dcd.content_cls.update_failure(self)
            self.is_connected = False


class DeviceConnectionDialog(MDDialog):

    def __init__(self, **kwargs):
        # Struggling to make this look right; overriding some source code
        # MDDialog is a ModalView, which is an AnchorLayout
        #       dialog (MDDialog)
        #           container (MDCard)
        #               title
        #               spacer_top_box
        #                   content_cls  <--- this is where content_cls is added if type=='custom'
        #               text
        #               scroll
        #                   box_items
        #               spacer_bottom_box
        #               root_button_box
        #                   button_box
        super().__init__(**kwargs)
        self.ids.container.padding = ('10sp', '10sp', '10sp', '10sp')
        self.ids.container.remove_widget(self.ids.title)
        self.ids.spacer_top_box.padding = (0, 0, 0, 0)
        # Dialog can't keep Dialog.content_cls contained / centered within it if Window is resized
        Window.unbind(on_resize=self.update_width)

    def update_height(self, *args):
        # Resize spacer_top_box, container, dialog window as DialogContent changes.
        self.ids.spacer_top_box.height = self.content_cls.height
        self.ids.container.height = self.ids.spacer_top_box.height + \
                                    self.ids.spacer_bottom_box.height + \
                                    self.ids.root_button_box.height
        self.height = self.ids.container.height


class DialogContent(MDBoxLayout):
    dialog = ObjectProperty()
    overlay_color_ = ListProperty([0, 1, 0, 0.25])
    label = ObjectProperty()
    status_container = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spinner = StatusSpinner()
        self.success_icon = SuccessIcon()
        self.fail_icon = FailIcon()
        self.status_container.add_widget(self.spinner)

    def on_size(self, *args):
        self.spinner.size = (self.success_icon.width * 0.8, self.success_icon.width * 0.8)
        self.dialog.update_height()
        self.pos = self.dialog.pos

    def update_success(self, device):
        self.status_container.remove_widget(self.spinner)
        self.label.text = 'Successfully conntected to ' + device.name
        self.label.theme_text_color = 'Custom'
        self.label.text_color = (0, 1, 0, 1)
        self.status_container.add_widget(self.success_icon)
        app = MDApp.get_running_app()
        app.connected_devices.append(device)
        app.root_screen.screen_manager.current = 'connected_devices'

    def update_failure(self, device):
        self.status_container.remove_widget(self.spinner)
        self.label.text = 'Failed to connect to ' + device.name
        self.label.theme_text_color = 'Custom'
        self.label.text_color = (1, 0, 0, 1)
        self.status_container.add_widget(self.fail_icon)
        app = MDApp.get_running_app()
        retry_btn = MDFlatButton(text='Retry?',
                                 on_release=partial(self.retry, device),
                                 md_bg_color=app.theme_cls.primary_light)
        self.dialog.buttons.append(retry_btn)
        # Dialog gives root_button_box some height in __init__ if there are buttons.
        # Giving it height here since we're re-using the same Dialog window.
        self.dialog.ids.root_button_box.height = dp(46)
        self.dialog.create_buttons()
        self.dialog.update_height()

    def retry(self, device, *args):
        self.dialog.dismiss()
        device.connect_as_client()


class StatusContainer(MDFloatLayout):
    overlay_color_ = ListProperty([0, 1, 0.75, 0.25])


class StatusSpinner(MDSpinner):
    overlay_color_ = ListProperty([0, 1, 0, 0.25])


class SuccessIcon(MDIconButton):
    # overlay_color_ = ListProperty([0, 0, 1, 0.3])
    font_size = sp(50)


class FailIcon(MDIconButton):
    # overlay_color_ = ListProperty([0, 0, 1, 0.3])
    font_size = sp(50)


class TestLabel(MDLabel):
    overlay_color_ = ListProperty([0.5, 0, 0.5, 0.5])


class DeviceController(MDBoxLayout, Border):
    device = ObjectProperty()
    power_button = ObjectProperty()
    dimmer = ObjectProperty()

    def power(self, *args):
        print(f'`{self.__class__.__name__}.{func_name()}`')
        print(self.power_button.state)
        app = MDApp.get_running_app()
        if self.power_button.state == 'normal':
            self.power_button.state = 'down'
            self.md_bg_color = app.theme_cls.primary_light
            # self.dimmer.disable = True
            # self.dimmer.value = 0
        else:
            self.power_button.state = 'normal'
            self.md_bg_color = app.theme_cls.primary_light
            # self.dimmer.disabled = False
            # self.dimmer.value = 50

    def dim(self, *args):
        print(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')


