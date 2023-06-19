import asyncio
import struct
from threading import Thread
from jnius import autoclass
from kivy.lang import Builder
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
    Window.size = (300, 600)


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
        self.theme_cls.primary_palette = 'BlueGray'
        self.theme_cls.primary_hue = '400'
        # self.theme_cls.material_style = 'M3'  # 'M3' breaks MDSwitch
        self.bluetooth_adapter = None
        self.bluetooth_socket = None
        self.send_stream = None
        self.recv_stream = None

        if platform == 'android':
            self.bluetooth_adapter = BluetoothAdapter.getDefaultAdapter()
            if self.bluetooth_adapter.isEnabled():
                print('Bluetooth is enabled...')
            else:
                print('Bluetooth is disabled...')
                self.enable_bluetooth()

        Builder.load_file('device_controller.kv')
        Builder.load_file('device_connection_dialog.kv')

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

    # def start_discovery(self, *args):
    #     print(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
    #     asyncio.create_task(self._start_discovery())
    #
    # async def _start_discovery(self):
    #     print(self.__class__.__name__, func_name())
    #     await asyncio.sleep(0.5)
    #     if platform == 'linux':
    #         new_devices = [FakeDevice() for _ in range(10)]
    #         self.available_devices[:] = new_devices
    #         if platform == 'android':
    #             try:
    #                 print('In try block')
    #                 # This is kind of working?
    #                 # self.broadcast_receiver = BroadcastReceiver(self.on_broadcast, actions=['airplane_mode_changed'])
    #                 # self.broadcast_receiver.start()
    #                 # activity = PythonActivity.mActivity
    #                 # intent_filter = IntentFilter()
    #                 # intent_filter.addAction(BluetoothDevice.ACTION_FOUND)
    #                 # activity.registerReceiver(self.bluetooth_discovery_receiver, intent_filter)
    #                 # self.bluetooth_adapter.startDiscovery()
    #                 # Wait for discovery to complete...
    #                 # activity.unregisterReceiver(self.bluetooth_discovery_receiver)
    #             except Exception as e:
    #                 print(f'BroadcastReceiver failed with Exception: {e}')
    #             else:
    #                 print(f'BroadcastReceiver success?')
    #
    # def on_broadcast(self, context, intent):
    #     print(f'`{self.__class__.__name__}.{func_name()}`')
    #     print(context, intent)
    #     action = intent.getAction()
    #     if BluetoothDevice.ACTION_FOUND == action:
    #         device = cast(BluetoothDevice, intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE))
    #         print('Found device: ', device.getName(), device.getAddress())

    def get_bonded_devices(self, *args):
        print(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        asyncio.create_task(self._get_bonded_devices())

    async def _get_bonded_devices(self):
        print(f'`{self.__class__.__name__}.{func_name()}`')
        await asyncio.sleep(0.5)
        if platform == 'linux':
            new_devices = [FakeDevice() for _ in range(10)]
            self.bonded_devices[:] = new_devices
        if platform == 'android':
            self.bonded_devices = self.bluetooth_adapter.getBondedDevices().toArray()

    def on_bonded_devices(self, *args):
        print(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        if platform == 'android':
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
        print(f'`{self.__class__.__name__}.{func_name()} called with args: {device, button}`')
        if platform == 'android':
            asyncio.create_task(self._connect_as_client_android(device, button))
        if platform == 'linux':
            asyncio.create_task(self._connect_as_client_linux(device, button))

    async def _connect_as_client_android(self, device, button):
        print(f'`{self.__class__.__name__}.{func_name()} called with args: {device, button}`')
        for k, v in self.get_device_info(device).items():
            print(k, ': ', v)
        dcd = DeviceConnectionDialog(
            type='custom',
            content_cls=DialogContent(),
        )
        dcd.content_cls.label.text = 'Connecting to... ... ... ' * 10 + device.name
        dcd.content_cls.dialog = dcd  # back-reference to parent
        dcd.open()
        # Must use separate thread for connecting to Bluetooth device to keep GUI functional.
        t = Thread(target=self._connect_BluetoothSocket, args=[device, dcd])
        t.start()

    def _connect_BluetoothSocket(self, device, dcd):
        '''
        Create and open the android.bluetooth.BluetoothSocket connection to the ESP32.
        BluetoothSocket.connect() is a blocking call that stops the main Kivy thread from executing
        and pauses the GUI; execute this function in a separate thread to avoid this problem.
        Inversely, Kivy GUI (graphics) instructions cannot be changed from outside main Kivy thread.
        Use kivy.clock @mainthread decorator on the MDDialog methods that are initiated here to
        keep graphics instructions in the main thread.
        '''
        print(f'`{self.__class__.__name__}.{func_name()} called with args: {device}`')
        try:
            UUID = autoclass('java.util.UUID')
            print(f'Creating BluetoothSocket')
            esp32_UUID = '00001101-0000-1000-8000-00805F9B34FB'
            self.bluetooth_socket = device.createRfcommSocketToServiceRecord(
                UUID.fromString(esp32_UUID))
            print(f'BluetoothSocket.connect()')
            self.bluetooth_socket.connect()
            self.recv_stream = self.bluetooth_socket.getInputStream()
            self.send_stream = self.bluetooth_socket.getOutputStream()
        except Exception as e:
            print(f'Failed to open socket. Exception {e}')
            # Note: @mainthread needed on DeviceConnectionDialog methods to avoid error.
            dcd.content_cls.update_failure(device)
        else:
            print(f'Successfully opened socket')
            # Note: @mainthread needed on DeviceConnectionDialog methods to avoid error.
            dcd.content_cls.update_success(device)

    async def _connect_as_client_linux(self, device, button):
        print(f'`{self.__class__.__name__}.{func_name()} called with args: {device, button}`')
        dcd = DeviceConnectionDialog(
            type='custom',
            content_cls=DialogContent(),
        )
        dcd.content_cls.label.text = 'Connecting to... ... ... ' * 10 + device.name
        dcd.content_cls.dialog = dcd  # back-reference to parent
        dcd.open()
        await asyncio.sleep(2)
        if random.choice([0, 1]):
            dcd.content_cls.update_success(device)
        else:
            dcd.content_cls.update_failure(device)

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
    # app.run()