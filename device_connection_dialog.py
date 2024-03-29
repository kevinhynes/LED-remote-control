import asyncio
import random
import sys
import string
import logging
from functools import partial
from kivy.core.window import Window
from kivy.clock import mainthread
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivy.metrics import dp, sp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRoundFlatButton, MDRectangleFlatButton
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import BaseListItem, OneLineIconListItem, TwoLineListItem
from kivymd.uix.card import MDCard
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.slider import MDSlider
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.screenmanager import SlideTransition

from troubleshooting import func_name


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

    @mainthread
    def update_height(self, *args):
        # Resize spacer_top_box, container, dialog window as DialogContent changes.
        # spacer_top_box.height is bound to MDDialog._spacer_top
        self.ids.spacer_top_box.height = self.content_cls.height
        self.height = self.ids.container.height
        # Force redraw of shadow or it misbehaves
        self.elevation = 1 if self.elevation == 0 else 0


class DialogContent(MDBoxLayout):
    dialog = ObjectProperty()
    overlay_color_ = ListProperty([0, 1, 0, 0.25])
    label = ObjectProperty()
    status_container = ObjectProperty()

    def __init__(self, device_controller=None, **kwargs):
        super().__init__(**kwargs)
        self.spinner = StatusSpinner()
        self.success_icon = SuccessIcon()
        self.fail_icon = FailIcon()
        self.status_container.add_widget(self.spinner)
        # Using the same DeviceConnectionDialog for initial connection and reconnection.
        # Need access to DeviceController.reconnect_BluetoothSocket.
        self.device_controller = device_controller

    @mainthread
    def on_size(self, *args):
        self.spinner.size = (self.success_icon.width * 0.8, self.success_icon.width * 0.8)
        self.dialog.update_height()
        self.pos = self.dialog.pos

    @mainthread
    def update_success(self, device):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.status_container.remove_widget(self.spinner)
        self.label.text = 'Successfully connected to ' + device.getName()
        self.label.theme_text_color = 'Custom'
        self.label.text_color = (0, 1, 0, 1)
        self.status_container.add_widget(self.success_icon)

    @mainthread
    def update_failure(self, device):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.status_container.remove_widget(self.spinner)
        self.label.text = 'Failed to connect to ' + device.getName()
        self.label.theme_text_color = 'Custom'
        self.label.text_color = (1, 0, 0, 1)
        self.status_container.add_widget(self.fail_icon)
        app = MDApp.get_running_app()
        if self.device_controller:
            retry_btn = MDRectangleFlatButton(text='Retry?',
                                              on_release=partial(self.device_controller.reconnect_BluetoothSocket,
                                                                 self.parent),
                                              line_color=app.theme_cls.primary_dark,
                                              )
        else:
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
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {device, retry_btn}`')
        self.dialog.dismiss()
        app = MDApp.get_running_app()
        app.connect_as_client(device, retry_btn)


class StatusContainer(MDFloatLayout):
    overlay_color_ = ListProperty([0, 1, 0.75, 0.25])


class StatusSpinner(MDSpinner):
    overlay_color_ = ListProperty([0, 1, 0, 0.25])


class SuccessIcon(MDIconButton):
    font_size = sp(50)


class FailIcon(MDIconButton):
    font_size = sp(50)
