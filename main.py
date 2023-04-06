import asyncio
import random
import sys
import string
import struct
from functools import partial
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivy.properties import ListProperty, ObjectProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineIconListItem
from kivymd.uix.pickers.colorpicker import MDColorPicker
from jnius import autoclass, cast, java_method


# Trying to get past permissions issue.
from kivy import platform
if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.BLUETOOTH_CONNECT,
                         Permission.BLUETOOTH,
                         Permission.BLUETOOTH_ADMIN,
                         Permission.BLUETOOTH_SCAN])
    from android import mActivity
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
    BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
    BluetoothAdapter_LeScanCallback = autoclass('android.bluetooth.BluetoothAdapter$LeScanCallback')
    Intent = autoclass('android.content.Intent')
    Context = autoclass('android.content.Context')
    IntentFilter = autoclass('android.content.IntentFilter')
    # BroadcastReceiver = autoclass('android.content.BroadcastReceiver')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')

    # try:
    #     from android.broadcast import BroadcastReceiver
    # except Exception as e:
    #     print(f"android.broadcast import exception occurred with exception: {e}")
    # else:
    #     print(f"android.broadcast import succeeded")

if platform == "linux":
    from kivy.core.window import Window
    Window.size = (350, 600)


def func_name():
    return sys._getframe(1).f_code.co_name


class FakeDevice:
    def __init__(self):
        self.name = self.generate_name()
        self.address = self.generate_MAC()

    def generate_MAC(self):
        num = str(random.randrange(10000000, 99999999))
        address = num[:2] + ':' + num[2:4] + ':' + num[4:6] + ':' + num[6:]
        return address

    def generate_name(self):
        lower = random.sample(string.ascii_lowercase, 8)
        upper = random.sample(string.ascii_uppercase, 2)
        temp = lower + upper
        random.shuffle(temp)
        name = "".join(temp)
        return name

    def request_connection(self, *args):
        print(f"Request for {self.address} received with {args}")


class BTDeviceListItem(TwoLineIconListItem):
    pass


class DevicesScreen(MDScreen):
    available_devices = ListProperty()
    available_devices_list = ObjectProperty()
    bonded_devices = ListProperty()
    bonded_devices_list = ObjectProperty()

    def on_available_devices(self, *args):
        print(self.__class__.__name__, func_name())
        buttons_to_remove = [child for child in self.available_devices_list.children]
        for child in buttons_to_remove:
            self.available_devices_list.remove_widget(child)
        for device in self.available_devices:
            button = BTDeviceListItem(text=device.name, secondary_text=device.address)
            button.bind(on_press=partial(device.request_connection, device))
            self.available_devices_list.add_widget(button)

    def on_bonded_devices(self, *args):
        print(self.__class__.__name__, func_name())
        buttons_to_remove = [child for child in self.bonded_devices_list.children]
        for child in buttons_to_remove:
            self.bonded_devices_list.remove_widget(child)
        if platform == "android":
            app = MDApp.get_running_app()
            for device in self.bonded_devices:
                button = BTDeviceListItem(text=device.getName(),
                                          secondary_text=device.getAddress())
                button.bind(on_press=partial(app.connect_as_client, device))
                self.bonded_devices_list.add_widget(button)
        if platform == "linux":
            for device in self.bonded_devices:
                button = BTDeviceListItem(text=device.name, secondary_text=device.address)
                button.bind(on_press=partial(device.request_connection, device))
                self.available_devices_list.add_widget(button)


class RootScreen(MDScreen):
    pass


class MainApp(MDApp):
    theme_cls = ThemeManager()
    available_devices = ListProperty()
    bonded_devices = ListProperty()

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.primary_hue = "500"
        self.bluetooth_adapter = None
        self.send_stream = None
        self.recv_stream = None
        self.esp32 = None

        if platform == "android":
            self.bluetooth_adapter = BluetoothAdapter.getDefaultAdapter()
            if self.bluetooth_adapter.isEnabled():
                print("Bluetooth is enabled.")
            else:
                print("BLUETOOTH IS DISABLED...")
                self.enable_bluetooth()

        self.rootscreen = RootScreen()
        return self.rootscreen

    def enable_bluetooth(self):
        print(self.__class__.__name__, func_name())
        # create the intent
        enable_bluetooth_intent = Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE)

        # All of the following appear to work...
        try:
            print(f"Trying android.mActivity.startActivity")
            mActivity.startActivity(enable_bluetooth_intent)
        except Exception as e:
            print(f"android.mActivity.startActivity failed. Exception: {e}")
        else:
            print(f"SUCCESS: android.mActivity.startActivity")

        try:
            print(f"Trying PythonActivity.mActivity.startActivity")
            activity = PythonActivity.mActivity
            activity.startActivity(enable_bluetooth_intent)
        except Exception as e:
            print(f"PythonActivity.mActivity.startActivity failed. Exception: {e}")
        else:
            print(f"SUCCESS: PythonActivity.mActivity.startActivity")

        try:
            print(f"Trying android.mActivity.startActivityForResult")
            mActivity.startActivityForResult(enable_bluetooth_intent, 0)
        except Exception as e:
            print(f"android.mActivity.startActivityForResult failed. Exception: {e}")
        else:
            print(f"SUCCESS: android.mActivity.startActivityForResult")

        try:
            print(f"Trying PythonActivity.mActivity.startActivityForResult")
            activity = PythonActivity.mActivity
            activity.startActivityForResult(enable_bluetooth_intent, 0)
        except Exception as e:
            print(f"PythonActivity.mActivity.startActivity failed. Exception: {e}")
        else:
            print(f"SUCCESS: PythonActivity.mActivity.startActivityForResult")

    # def connect_to_esp32(self, instance):
    #     if self.esp32 is None:
    #         print("ESP32 not found.")
    #         return
    #     try:
    #         self.socket = self.esp32.createRfcommSocketToServiceRecord(
    #             self.BluetoothDevice.Serial_UUID)
    #         self.socket.connect()
    #         print("Connected to ESP32.")
    #     except Exception as e:
    #         print("Failed to connect:", e)
    #     return

    def start_discovery(self, *args):
        print(self.__class__.__name__, func_name())
        asyncio.create_task(self._start_discovery())

    async def _start_discovery(self):
        print(self.__class__.__name__, func_name())
        await asyncio.sleep(0.5)
        if platform == "linux":
            new_devices = [FakeDevice() for _ in range(20)]
            self.available_devices[:] = new_devices
        if platform == "android":
            try:
                print("In try block")
                # class BluetoothDiscoveryReceiver(BroadcastReceiver):
                #
                #     __javaclass__ = 'android/content/BroadcastReceiver'
                #
                #     def __init__(self):
                #         super().__init__()
                #
                #     @java_method('(Landroid/content/Context;Landroid/content/Intent;)V')
                #     def onReceive(self, context, intent):
                #         action = intent.getAction()
                #         if BluetoothDevice.ACTION_FOUND == action:
                #             device = cast(BluetoothDevice, intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE))
                #             print("Found device:", device.getName(), device.getAddress())

                ##This is kind of working?
                # self.broadcast_receiver = BroadcastReceiver(self.on_broadcast,
                #                                             actions=["airplane_mode_changed"])
                # print("    BroadcastReceiver created")
                # self.broadcast_receiver.start()
                # print("    BroadcastReceiver started")

                # activity = PythonActivity.mActivity
                # print("    activity")
                #
                # intent_filter = IntentFilter()
                # print("    intent_filter")
                #
                # intent_filter.addAction(BluetoothDevice.ACTION_FOUND)
                # print("    intent_filter.addAction")
                #
                # activity.registerReceiver(self.bluetooth_discovery_receiver, intent_filter)
                # print("    activity.registerReceiver")
                #
                # self.bluetooth_adapter.startDiscovery()
                # print("    bluetooth_adapter.startDiscovery()")
                # # Wait for discovery to complete
                # # ...
                # activity.unregisterReceiver(self.bluetooth_discovery_receiver)
                # print("    bluetooth_adapter.unregisterReceiver()")

            except Exception as e:
                print(f"BroadcastReceiver failed with exception: {e}")
            else:
                print(f"BroadcastReceiver success??")

    def get_bonded_devices(self, *args):
        print(self.__class__.__name__, func_name())
        asyncio.create_task(self._get_bonded_devices())

    async def _get_bonded_devices(self):
        print(self.__class__.__name__, func_name())
        await asyncio.sleep(0.5)
        if platform == "linux":
            new_devices = [FakeDevice() for _ in range(20)]
            self.bonded_devices[:] = new_devices
        if platform == "android":
            self.bonded_devices = self.bluetooth_adapter.getBondedDevices().toArray()

    def on_bonded_devices(self, *args):
        if platform == "android":
            print(self.__class__.__name__, func_name())
            for num, device in enumerate(self.bonded_devices):
                print(num, device)
                for k, v in self.get_device_info(device).items():
                    if k != "UUIDs":
                        print(f"    {k}: {v}")

    def get_device_info(self, device):
        bluetooth_class = device.getBluetoothClass()
        name = device.getName()
        address = device.getAddress()
        alias = device.getAlias()
        bond_state = device.getBondState()
        type = device.getType()
        UUIDs = device.getUuids()
        string_representation = device.toString()
        device_info = {"BluetoothClass": bluetooth_class,
                       "Name": name,
                       "Alias": alias,
                       "Address": address,
                       "Type": type,
                       "Bond State": bond_state,
                       "UUIDs": UUIDs,
                       "String Representation": string_representation,
                       }
        return device_info

    def on_broadcast(self, context, intent):
        print(self.__class__.__name__, func_name())
        print(context, intent)
        action = intent.getAction()
        if BluetoothDevice.ACTION_FOUND == action:
            device = cast(BluetoothDevice, intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE))
            print("Found device:", device.getName(), device.getAddress())

    def on_pause(self):
        return True

    def connect_as_client(self, device, button):
        print(self.__class__.__name__, func_name())
        print(device.getUuids())
        try:
            UUID = autoclass('java.util.UUID')
            socket = device.createRfcommSocketToServiceRecord(
                UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
            self.recv_stream = socket.getInputStream()
            self.send_stream = socket.getOutputStream()
            socket.connect()
        except Exception as e:
            print(f"Failed to open socket, exception: {e}")
        else:
            print(f"Successfully opened socket")

    def send_string(self, val):
        print(self.__class__.__name__, func_name())
        print(val)
        mode = 1
        alpha = 1
        if val == '1':
            red, green, blue = [255, 255, 255]
        elif val == '2':
            red, green, blue = [0, 0, 255]
        elif val == '3':
            red, green, blue = [0, 255, 0]
        elif val == '4':
            red, green, blue = [255, 0, 0]
        else:
            red, green, blue = [0, 0, 0]
        if self.send_stream is not None:
            # self.send_stream.write(struct.pack('<s', b'<'))
            self.send_stream.write(struct.pack('<B', mode))
            self.send_stream.write(struct.pack('<B', red))
            self.send_stream.write(struct.pack('<B', green))
            self.send_stream.write(struct.pack('<B', blue))
            self.send_stream.write(struct.pack('<B', alpha))
            self.send_stream.write(struct.pack('<b', -1))
            self.send_stream.flush()
            print("Command sent.")
        else:
            print(f"Failed to send: self.send_stream is {self.send_stream}")

    def send_int(self, val):
        print(self.__class__.__name__, func_name())
        print(val)
        if self.send_stream is not None:
            self.send_stream.write(struct.pack(">b", val))
            self.send_stream.flush()
            print("Command sent.")
        else:
            print(f"Failed to send: self.send_stream is {self.send_stream}")

    def send_float(self, val):
        print(self.__class__.__name__, func_name())
        print(val)
        if self.send_stream is not None:
            self.send_stream.write(bytes(str(val), "utf-8"))
            self.send_stream.flush()
            print("Command sent.")
        else:
            print(f"Failed to send: self.send_stream is {self.send_stream}")


if __name__ == "__main__":
    app = MainApp()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.async_run(async_lib="asyncio"))


