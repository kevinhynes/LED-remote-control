import logging
import random
import string
from collections import defaultdict


class Command:
    """
    Template for any possible command that can be sent from App to ESP32.
    An instance of this class is given to DeviceController.send_command().
    """

    def __init__(self, mode, red=None, green=None, blue=None, dimmer_val=None,
                 num_leds=None, max_brightness=None, color_correction_key=None,
                 color_temperature_correction_key=None, hex_colors=None, is_mirrored=False,
                 is_blended=False,
                 animation_id=None, animation_speed=None, trail_length=None, num_comets=None):
        self.mode = mode
        self.red = red
        self.green = green
        self.blue = blue
        self.dimmer_val = dimmer_val
        self.num_leds = num_leds
        self.max_brightness = max_brightness
        self.color_correction_key = color_correction_key
        self.color_temperature_correction_key = color_temperature_correction_key
        self.hex_colors = hex_colors
        self.is_mirrored = is_mirrored
        self.is_blended = is_blended
        self.animation_id = animation_id
        self.animation_speed = animation_speed
        self.trail_length = trail_length
        self.num_comets = num_comets

    def as_dict(self):
        """Commands need to be saved to the App's JSON storage when a FavoriteButton is added."""
        command_as_dict = {'mode': self.mode,
                           'red': self.red,
                           'green': self.green,
                           'blue': self.blue,
                           'dimmer_val': self.dimmer_val,
                           'num_leds': self.num_leds,
                           'max_brightness': self.max_brightness,
                           'color_correction_key': self.color_correction_key,
                           'color_temperature_correction_key': self.color_temperature_correction_key,
                           'hex_colors': self.hex_colors,
                           'is_mirrored': self.is_mirrored,
                           'is_blended': self.is_blended,
                           'animation_id': self.animation_id,
                           'animation_speed': self.animation_speed,
                           'trail_length': self.trail_length,
                           'num_comets': self.num_comets}
        return command_as_dict

    @staticmethod
    def load_from_dict(command_as_dict):
        """When the App is loaded, any FavoriteButton.command_list's commands will have to be
        reloaded as a Command object."""
        command = Command(mode=command_as_dict['mode'],
                          red=command_as_dict['red'],
                          green=command_as_dict['green'],
                          blue=command_as_dict['blue'],
                          dimmer_val=command_as_dict['dimmer_val'],
                          num_leds=command_as_dict['num_leds'],
                          max_brightness=command_as_dict['max_brightness'],
                          color_correction_key=command_as_dict['color_correction_key'],
                          color_temperature_correction_key=command_as_dict[
                              'color_temperature_correction_key'],
                          hex_colors=command_as_dict['hex_colors'],
                          is_mirrored=command_as_dict['is_mirrored'],
                          is_blended=command_as_dict['is_blended'],
                          animation_id=command_as_dict['animation_id'],
                          animation_speed=command_as_dict['animation_speed'],
                          trail_length=command_as_dict['trail_length'],
                          num_comets=command_as_dict['num_comets'],
                          )
        return command


class CustomBluetoothDevice:
    """
    CustomBluetoothDevice will hold the instance of the Android BluetoothDevice object:
    https://developer.android.com/reference/android/bluetooth/BluetoothDevice

    which is how we can open a BluetoothSocket and send data to the ESP32.

    This class is essentially what gets saved to the App's storage / persistence.
    Each CustomBluetoothDevice gets its own DeviceController.
    """

    def __init__(self, bluetooth_device=None, name='', address='', nickname='',
                 favorites={}):
        self.bluetooth_device = bluetooth_device
        self.name = name
        self.address = address
        self.nickname = nickname
        self.favorites = favorites
        self.bluetooth_socket = None
        self.recv_stream = None
        self.send_stream = None
        self.num_leds = 100
        self.max_brightness = 100
        # ESP32 will default to these if not set otherwise:
        self.color_correction = 'Uncorrected Color'
        self.color_temperature_correction = 'Uncorrected Temperature'

    def __getattr__(self, attr):
        """This allows CustomBluetoothDevice.METHOD_NAME to immediately defer to the Android API's
        BluetoothDevice.METHOD_NAME instead, where all the desired methods are defined.
        """
        if hasattr(self.bluetooth_device, attr):
            return getattr(self.bluetooth_device, attr)
        raise AttributeError(f"'CustomBluetoothDevice' object has no attribute '{attr}'")

    def getName(self, *args):
        """This method is handled by the __getattr__ defined above, but if app is started with
        Bluetooth off, BluetoothDevice.getName() returns None and will cause app to crash."""
        name = self.bluetooth_device.getName()
        if name is None:
            return self.name
        return name

    def getAddress(self, *args):
        """This method is handled by the __getattr__ defined above, but if app is started with
        Bluetooth off, BluetoothDevice.getAddress() returns None and will cause app to crash."""
        address = self.bluetooth_device.getAddress()
        if address is None:
            return self.address
        return address

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
                       'Nickname': self.nickname,
                       'Address': address,
                       'Favorites': self.favorites,
                       'Type': type,
                       'BondState': bond_state,
                       'UUIDs': UUIDs,
                       'Number of LEDs': self.num_leds,
                       'Maximum Brightness': self.max_brightness,
                       'Color Correction': self.color_correction,
                       'Color Temperature Correction': self.color_temperature_correction
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
            self.nickname = ''
            self.address = self.generate_MAC()
            self.type = random.randrange(1, 10)
            self.bond_state = random.randrange(1, 12)
            self.uuids = [FakeUUID() for _ in range(10)]
            self.num_leds = 100
            self.max_brightness = 100
            self.color_correction = 'Uncorrected Color'
            self.color_temperature_correction = 'Uncorrected Temperature'
            self.favorites = defaultdict(dict)
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
                       'Nickname': self.nickname,
                       'Type': self.type,
                       'BondState': self.bond_state,
                       'UUIDs': self.uuids,
                       'Number of LEDs': self.num_leds,
                       'Maximum Brightness': self.max_brightness,
                       'Color Correction': self.color_correction,
                       'Color Temperature Correction': self.color_temperature_correction,
                       'Favorites': self.favorites,
                       }
        return device_info

    def load_device_info(self, device_info):
        self.name = device_info['Name']
        self.address = device_info['Address']
        self.alias = device_info['Alias']
        self.nickname = device_info['Nickname']
        self.type = device_info['Type']
        self.bond_state = device_info['BondState']
        # Convert saved UUIDs from string back to hex
        self.uuids = [FakeUUID(uuid) for uuid in device_info['UUIDs']]
        self.num_leds = device_info['Number of LEDs']
        self.max_brightness = device_info['Maximum Brightness']
        self.color_correction = device_info['Color Correction']
        self.color_temperature_correction = device_info['Color Temperature Correction']
        self.favorites = defaultdict(dict)
        for fav_idx, loaded_commands_dict in device_info['Favorites'].items():
            self.favorites[fav_idx] = loaded_commands_dict

    def isConnected(self):
        return random.choice([0, 1])

    def disconnected_status(self, *args):
        pass

    def connected_status(self, *args):
        pass
