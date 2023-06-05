import asyncio
import struct
from jnius import autoclass
from kivymd.theming import ThemeManager

from screens import *


# Developer Mode:
# from kivy.config import Config
# Config.set('kivy', 'log_level', 'debug')

# Necessary to request these permissions on android.  Order seems to matter(?)
if platform == 'android':
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

    try:
        from android.broadcast import BroadcastReceiver
    except Exception as e:
        print(f'android.broadcast import exception occurred with Exception: {e} ')
    else:
        print(f'android.broadcast import succeeded')

if platform == 'linux':
    from kivy.core.window import Window
    Window.size = (330, 580)


def func_name():
    return sys._getframe(1).f_code.co_name


class MainApp(MDApp):
    theme_cls = ThemeManager()
    screen_manager = ObjectProperty()
    available_devices = ListProperty()
    bonded_devices = ListProperty()
    connected_devices = ListProperty()

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.primary_hue = '700'
        self.bluetooth_adapter = None
        self.send_stream = None
        self.recv_stream = None
        self.esp32 = None

        if platform == 'android':
            self.bluetooth_adapter = BluetoothAdapter.getDefaultAdapter()
            if self.bluetooth_adapter.isEnabled():
                print('Bluetooth is enabled...')
            else:
                print('Bluetooth is disabled...')
                self.enable_bluetooth()

        self.root_screen = RootScreen()
        return self.root_screen

    def on_pause(self):
        return True

    def enable_bluetooth(self):
        print(f'`{self.__class__.__name__}.{func_name()}`')
        enabled_bluetooth_intent = Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE)
        # All of the following appear to work:
        try:
            print(f'Trying android.mActivity.startActivity')
            mActivity.startActivity(enabled_bluetooth_intent)
        except Exception as e:
            print(f'android.mActivity.startActivity failed. Exception: {e}')
        else:
            print(f'Success: android.mActivity.startActivity')

        try:
            print(f'Trying PythonActivity.mActivity.startActivity')
            activity = PythonActivity.mActivity
            activity.startActivity(enabled_bluetooth_intent)
        except Exception as e:
            print(f'PythonActivity.mActivity.startActivity failed. Exception: {e}')
        else:
            print(f'Success: PythonActivity.mActivity.startActivity')

        try:
            print(f'Trying android.mActivity.startActivityForResult')
            mActivity.startActivityForResult(enabled_bluetooth_intent, 0)
        except Exception as e:
            print(f'android.mActivity.startActivityForResult failed. Exception: {e}')
        else:
            print(f'Success: android.mActivity.startActivityForResult')

        try:
            print(f'Trying PythonActivity.mActivity.startActivityForResult')
            activity = PythonActivity.mActivity
            activity.startActivityForResult(enabled_bluetooth_intent, 0)
        except Exception as e:
            print(f'PythonActivity.mActivity.startActivityForResult failed. Exception: {e}')
        else:
            print(f'Success: PythonActivity.mActivity.startActivityForResult')

    def start_discovery(self, *args):
        print(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        asyncio.create_task(self.start_discovery())

    async def _start_discovery(self):
        print(self.__class__.__name__, func_name())
        await asyncio.sleep(0.5)
        if platform == 'linux':
            new_devices = [FakeDevice() for _ in range(20)]
            self.available_devices[:] = new_devices
            if platform == 'android':
                try:
                    print('In try block')
                    # This is kind of working?
                    # self.broadcast_receiver = BroadcastReceiver(self.on_broadcast, actions=['airplane_mode_changed'])
                    # self.broadcast_receiver.start()
                    # activity = PythonActivity.mActivity
                    # intent_filter = IntentFilter()
                    # intent_filter.addAction(BluetoothDevice.ACTION_FOUND)
                    # activity.registerReceiver(self.bluetooth_discovery_receiver, intent_filter)
                    # self.bluetooth_adapter.startDiscovery()
                    # Wait for discovery to complete...
                    # activity.unregisterReceiver(self.bluetooth_discovery_receiver)
                except Exception as e:
                    print(f'BroadcastReceiver failed with Exception: {e}')
                else:
                    print(f'BroadcastReceiver success?')

    def on_broadcast(self, context, intent):
        print(f'`{self.__class__.__name__}.{func_name()}`')
        print(context, intent)
        action = intent.getAction()
        if BluetoothDevice.ACTION_FOUND == action:
            device = cast(BluetoothDevice, intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE))
            print('Found device: ', device.getName(), device.getAddress())

    def get_bonded_devices(self, *args):
        print(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        asyncio.create_task(self._get_bonded_devices())

    async def _get_bonded_devices(self):
        print(f'`{self.__class__.__name__}.{func_name()}`')
        await asyncio.sleep(0.5)
        if platform == 'linux':
            new_devices = [FakeDevice() for _ in range(20)]
            self.bonded_devices[:] = new_devices
        if platform == 'android':
            self.bonded_devices = self.bluetooth_adapter.getBondedDevices().toArray()

    def on_bonded_devices(self, *args):
        if platform == 'android':
            print(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
            for num, device in enumerate(self.bonded_devices):
                print(num, device)
                for k, v in self.get_device_info(device).items():
                    if k != 'UUIDs':
                        print(f'        {k}: {v}')

    def get_device_info(self, device):
        bluetooth_class = device.getBluetoothClass()
        name = device.getName()
        address = device.getAddress()
        alias = device.getAlias()
        bond_state = device.getBondState()
        type = device.getType()
        UUIDs = device.getUuids()
        string_representation = device.toString()
        device_info = {'BluetoothClass': bluetooth_class,
                       'Name': name,
                       'Alias': alias,
                       'Address': address,
                       'Type': type,
                       'BondState': bond_state,
                       'UUIDs': UUIDs,
                       'StringRepresentation': string_representation,
                       }
        return device_info

    def connect_as_client(self, device, button):
        print(f'`{self.__class__.__name__}.{func_name()}`')
        print(device.getUuids())
        try:
            UUID = autoclass('java.util.UUID')
            socket = device.createRfcommSocketToServiceRecord(
                UUID.fromString('00001101-0000-1000-8000-00805F9B34FB'))
            self.recv_stream = socket.getInputStream()
            self.send_stream = socket.getOutputStream()
            socket.connect()
        except Exception as e:
            print(f'Failed to open socket. Exception {e}')
        else:
            print(f'Successfully opened socket')
            success_dialog = MDDialog(text='Device connected successfully')
            success_dialog.open()

    def send(self, val):
        print(f'`{self.__class__.__name__}.{func_name()}`')
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
            self.send_stream.write(struct.pack('<B', mode))
            self.send_stream.write(struct.pack('<B', red))
            self.send_stream.write(struct.pack('<B', green))
            self.send_stream.write(struct.pack('<B', blue))
            self.send_stream.write(struct.pack('<B', alpha))
            self.send_stream.write(struct.pack('<B', -1))
            self.send_stream.flush()
            print('Command sent.')
        else:
            print(f'Failed to send: self.send_stream is {self.send_stream}')


if __name__ == '__main__':
    app = MainApp()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.async_run(async_lib='asyncio'))
