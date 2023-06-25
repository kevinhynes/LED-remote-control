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

from troubleshooting import *
from device_controller import *
from device_connection_dialog import *


def func_name():
    return sys._getframe(1).f_code.co_name


class BTDeviceListItem(TwoLineAvatarIconListItem):
    pass


class DeviceInfoListItem(BaseListItem):
    heading_label = ObjectProperty()
    content_label = ObjectProperty()

    def __init__(self, heading='', content='', **kwargs):
        super().__init__(**kwargs)
        self.heading_label.text = heading
        self.content_label.text = content


class FakeDevice:
    def __init__(self):
        self.name = self.generate_name()
        self.address = self.generate_MAC()
        self.alias = 'FakeDevice.alias\n' * 10

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

    # Mimic the Java / custom methods to avoid checking platform.
    def setAlias(self, new_alias):
        self.alias = str(new_alias)

    def get_device_info(self, device):
        device_info = {'Name': self.name,
                       'Address': self.address,
                       'Alias': self.alias}
        return device_info


class TestLabel(MDLabel):
    overlay_color_ = ListProperty([0.5, 0, 0.5, 0.5])


