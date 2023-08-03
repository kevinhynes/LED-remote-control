import asyncio
import random
import sys
import string
import struct
import jnius
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
from jnius import autoclass, java_method, PythonJavaClass

from troubleshooting import *
from device_controller import *
from device_connection_dialog import *


class CustomBluetoothDevice:
    # To allow user to rename device and save, I think this class is necessary?

    def __init__(self, bluetooth_device=None, user_assigned_alias=''):
        self.bluetooth_device = bluetooth_device
        self.user_assigned_alias = user_assigned_alias
        self.bluetooth_socket = None
        self.recv_stream = None
        self.send_stream = None

    def __getattr__(self, attr):
        if hasattr(self.bluetooth_device, attr):
            return getattr(self.bluetooth_device, attr)
        raise AttributeError(f"'CustomBluetoothDevice' object has no attribute '{attr}'")

    def get_device_info(self):
        if self.bluetooth_device is None:
            return {}
        name = self.getName()
        address = self.getAddress()
        alias = self.getAlias()
        bond_state = self.getBondState()
        type = self.getType()
        UUIDs = self.getUuids()
        device_info = {'Name': name,
                       'Alias': alias,
                       'User Assigned Alias': self.user_assigned_alias,
                       'Address': address,
                       'Type': type,
                       'BondState': bond_state,
                       'UUIDs': UUIDs,
                       }
        return device_info


class FakeUUID:

    def __init__(self, uuid=''):
        if uuid == '':
            self.uuid = self.generate_uuid()
        else:
            self.load_uuid(uuid)

    def generate_uuid(self):
        uuid = 0
        for i in range(128):
            bit = random.choice([0, 1])
            if i == 0:
                uuid = bit
            else:
                uuid = uuid << 1
                uuid = uuid | bit
        logging.debug(f'`FakeUUID generated {uuid}')
        return uuid

    def toString(self):
        uuid_str = str(hex(self.uuid))
        uuid_str = f'{uuid_str[:8]}-{uuid_str[8:12]}-{uuid_str[12:16]}-{uuid_str[16:20]}-' \
                   f'{uuid_str[20:]}'
        return uuid_str

    def load_uuid(self, uuid_str):
        # Convert the saved string UUID back to hex
        uuid_str = uuid_str.replace('-', '')
        self.uuid = int(uuid_str, 16)
        logging.debug(f'`FakeUUID loaded {self.uuid}')


class FakeDevice:

    def __init__(self, device_info={}):
        if device_info == {}:
            self.name = self.generate_name()
            self.alias = 'FakeDevice.alias'
            self.user_assigned_alias = ''
            self.address = self.generate_MAC()
            self.type = random.randrange(1, 10)
            self.bond_state = random.randrange(1, 12)
            self.uuids = [FakeUUID() for _ in range(10)]
        else:
            self.load_device_info(device_info)

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
    def getName(self):
        return self.name

    def getAddress(self):
        return self.address

    def get_device_info(self):
        device_info = {'Name': self.name,
                       'Address': self.address,
                       'Alias': self.alias,
                       'User Assigned Alias': self.user_assigned_alias,
                       'Type': self.type,
                       'BondState': self.bond_state,
                       'UUIDs': self.uuids,
                       }
        return device_info

    def load_device_info(self, device_info):
        self.name = device_info['Name']
        self.address = device_info['Address']
        self.alias = device_info['Alias']
        self.user_assigned_alias = device_info['User Assigned Alias']
        self.type = device_info['Type']
        self.bond_state = device_info['BondState']
        # Convert saved UUIDs from string back to hex
        self.uuids = [FakeUUID(uuid) for uuid in device_info['UUIDs']]

    def isConnected(self):
        return random.choice([0, 1])

    def disconnected_status(self, *args):
        pass

    def connected_status(self, *args):
        pass



