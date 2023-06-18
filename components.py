import asyncio
import random
import sys
import string
from functools import partial
from kivy.core.window import Window
from kivy.clock import mainthread
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivy.metrics import dp, sp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFlatButton, MDRectangleFlatButton
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem, BaseListItem
from kivymd.uix.card import MDCard
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.slider import MDSlider
from kivy.uix.behaviors import ButtonBehavior

from kivy.clock import Clock

from troubleshooting import *


def func_name():
    return sys._getframe(1).f_code.co_name


class BTDeviceListItem(TwoLineAvatarIconListItem):
    pass


class FakeDevice:
    def __init__(self):
        self.name = self.generate_name()
        self.address = self.generate_MAC()
        self.alias = 'FakeDevice.alias'

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

    def rename(self, new_alias):
        self.alias = str(new_alias)


class DeviceConnectionDialog(MDDialog):

    def __init__(self, **kwargs):
        '''
        Struggling to make this look right; overriding some source code
        MDDialog is a ModalView, which is an AnchorLayout
              dialog (MDDialog)
                  container (MDCard)
                      title
                      spacer_top_box
                          content_cls  <--- this is where content_cls is added if type=='custom'
                      text             <--- gets removed when type=='custom'
                      scroll           <--- gets removed when type=='custom'
                          box_items
                      spacer_bottom_box
                      root_button_box
                          button_box
        '''
        super().__init__(**kwargs)
        self.ids.container.padding = (dp(10), dp(10), dp(10), dp(10))
        self.ids.container.remove_widget(self.ids.title)
        self.ids.spacer_top_box.padding = (0, 0, 0, 0)
        # Dialog can't keep Dialog.content_cls contained / centered within it if Window is resized
        Window.unbind(on_resize=self.update_width)

    # @mainthread
    # def on_open(self, *args):
    #     print(f'`{self.__class__.__name__}.{func_name()}`')
    #     print(self.height, self.ids.container.height, self.content_cls.height)

    @mainthread
    def update_height(self, *args):
        # print(f'`{self.__class__.__name__}.{func_name()}`')
        # print('Before: ', self.height, self.ids.container.height, self.content_cls.height)
        # Resize spacer_top_box, container, dialog window as DialogContent changes.
        # spacer_top_box.height is bound to MDDialog._spacer_top
        self.ids.spacer_top_box.height = self.content_cls.height
        # self._spacer_top = self.content_cls.height
        # self.ids.container.height = self.content_cls.height + \
        #                             self.ids.spacer_bottom_box.height + \
        #                             self.ids.root_button_box.height
        self.height = self.ids.container.height
        # print('After: ', self.height, self.ids.container.height, self.content_cls.height)


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

    @mainthread
    def on_size(self, *args):
        # print(f'`{self.__class__.__name__}.{func_name()}`')
        # print('Before: ', self.dialog.height, self.dialog.ids.container.height, self.dialog.content_cls.height)
        self.spinner.size = (self.success_icon.width * 0.8, self.success_icon.width * 0.8)
        self.dialog.update_height()
        self.pos = self.dialog.pos
        # print('After: ', self.dialog.height, self.dialog.ids.container.height, self.dialog.content_cls.height)

    @mainthread
    def update_success(self, device):
        print(f'`{self.__class__.__name__}.{func_name()}`')
        self.status_container.remove_widget(self.spinner)
        self.label.text = 'Successfully connected to ' * 5 + device.name
        self.label.theme_text_color = 'Custom'
        self.label.text_color = (0, 1, 0, 1)
        self.status_container.add_widget(self.success_icon)
        app = MDApp.get_running_app()
        app.connected_devices.append(device)
        app.root_screen.screen_manager.current = 'connected_devices'

    @mainthread
    def update_failure(self, device):
        print(f'`{self.__class__.__name__}.{func_name()}`')
        self.status_container.remove_widget(self.spinner)
        self.label.text = 'Failed to connect to ' * 5 + device.name
        self.label.theme_text_color = 'Custom'
        self.label.text_color = (1, 0, 0, 1)
        self.status_container.add_widget(self.fail_icon)
        app = MDApp.get_running_app()
        retry_btn = MDRectangleFlatButton(text='Retry?',
                                          on_release=partial(self.retry, device),
                                          line_color=app.theme_cls.primary_dark,
                                          )
        self.dialog.buttons.append(retry_btn)
        # Dialog gives root_button_box some height in __init__ if there are buttons.
        # Giving it height here since we're re-using the same Dialog window.
        self.dialog.ids.root_button_box.height = dp(46)
        self.dialog.create_buttons()
        self.dialog.update_height()

    @mainthread
    def retry(self, device, retry_btn):
        print(f'`{self.__class__.__name__}.{func_name()} called with args: {device, retry_btn}`')
        self.dialog.dismiss()
        app = MDApp.get_running_app()
        app.connect_as_client(device, retry_btn)


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


class PowerButton(MDSwitch, ButtonBehavior):

    # def on_touch_up(self, touch):
    #     if self.collide_point(touch.x, touch.y):
    #         print('Touch INSIDE PowerButton')
    #         return True
    # print('Touch OUTSIDE of PowerButton')
    pass


class Dimmer(MDSlider):

    # def on_touch_up(self, touch):
    #     if self.collide_point(touch.x, touch.y):
    #         print('Touch INSIDE Dimmer')
    #         return True
    #     print('Touch OUTSIDE of Dimmer')
    pass


class DeviceController(BaseListItem):
    device = ObjectProperty()
    power_button = ObjectProperty()
    dimmer = ObjectProperty()
    brightness = NumericProperty(50)
    num = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._initialize_slider, 0.5)
        Clock.schedule_once(self._initialize_switch, 1.65)

    def _initialize_slider(self, *args):
        # In order for the thumb icon to show the off ring at value == 0 when MDSlider is just
        # instantiated, change it and then change it back to 0.
        self.dimmer.value = 1
        self.dimmer.value = 0
        self.dimmer.disabled = True
        self.dimmer.bind(on_touch_down=self.dimmer_touch_down)
        self.dimmer.bind(on_touch_up=self.dimmer_touch_up)

    def _initialize_switch(self, *args):
        self.power_button.ids.thumb._no_ripple_effect = True
        # self.power_button.ids.thumb.ids.icon.icon = 'power'

    # def on_touch_down(self, touch):
    #     print(f'`{self.__class__.__name__}.{func_name()}` called with args: {touch}')
    #     if self.dimmer.collide_point(touch.x, touch.y):
    #         print('Touch INSIDE Dimmer')
    #         return True
    #     elif self.power_button.collide_point(touch.x, touch.y):
    #         print('Touch INSIDE PowerButton')
    #         return True
    #     elif self.collide_point(touch.x, touch.y):
    #         print('Touch INSIDE DeviceController')
    #         return True
    #     else:
    #         print('Touch OUTSIDE DeviceController')
    #     return super(DeviceController, self).on_touch_up(touch)

    def power(self, *args):
        print(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        if self.power_button.active:
            print('LIGHTS ON!')
            self.dimmer.value = self.brightness
            self.dimmer.disabled = False
        else:
            print('LIGHTS OFF!')
            self.brightness = self.dimmer.value
            self.dimmer.value = 0
            self.dimmer.disabled = True
        print('')

    def dim(self, dimmer):
        print(f'`{self.__class__.__name__}.{func_name()}`'
              f'called with dimmer.value == {dimmer.value}')
        print('')
        pass

    def dimmer_touch_down(self, dimmer, touch):
        # Reducing the slider to 0 should also turn off the power button, but only after releasing
        # the slider at 0 - in case slider is moved to 0 and back up again.
        #
        # Therefore need the on_touch_up event, but if the touch_up occurs outside of the slider,
        # it isn't possible to know which slider it was for.
        #
        # Grab the touch event for the slider to check the touch_up event later. Don't return True
        # so that KivyMD's slider animations can complete.
        if dimmer.collide_point(touch.x, touch.y) and not dimmer.disabled:
            print(f'`{self.__class__.__name__}.{func_name()}`')
            print('Grabbing touch_down INSIDE Dimmer')
            touch.grab(dimmer)
            # return True
        # return super(DeviceController, dimmer).on_touch_up(touch)
        # if dimmer == self.dimmer:
        #     print(f'`{self.__class__.__name__}.{func_name()}`')
        #     if self.dimmer.value == 0:
        #         self.dimmer.disabled = True
        #         self.power_button.active = False
        #         self.dimmer._offset = dp(15), dp(15)
        #     else:
        #         self.dimmer.offset = 0, 0
        #         self.dimmer.disabled = False
        # print('')

    def dimmer_touch_up(self, dimmer, touch):
        if touch.grab_current is dimmer:
            print('Found touch_up...')
            if dimmer.collide_point(touch.x, touch.y):
                print('               ...INSIDE Dimmer')
            else:
                print('               ...OUTSIDE Dimmer')
            if dimmer.value == 0:
                dimmer.disabled = True
                self.power_button.active = False
            touch.ungrab(dimmer)
            # return True