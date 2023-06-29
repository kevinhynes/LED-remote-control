import asyncio
import os
import struct
import jnius
import logging
from jnius import autoclass, cast
from threading import Thread
from kivy.lang import Builder
from kivymd.theming import ThemeManager
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.button import MDFlatButton
from screens import *

logging.basicConfig(level=logging.DEBUG)

# Developer Mode:
# from kivy.config import Config
# Config.set('kivy', 'log_level', 'debug')

# Needed for Python code to communicate with android operating system, sensors, etc.
if platform == 'android':
    from android import mActivity
    BluetoothManager = autoclass('android.bluetooth.BluetoothManager')
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
    BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    Context = autoclass('android.content.Context')
    IntentFilter = autoclass('android.content.IntentFilter')
    Manifest = autoclass('android.Manifest')
    PackageManager = autoclass('android.content.pm.PackageManager')
    Activity = autoclass('android.app.Activity')
    # BroadcastReceiver = autoclass('android.content.BroadcastReceiver')
    # try:
    #     from android.broadcast import BroadcastReceiver
    # except Exception as e:
    #     logging.debug(f'android.broadcast import exception occurred with Exception: {e} ')
    # else:
    #     logging.debug(f'android.broadcast import succeeded')

if platform == 'linux':
    from kivy.core.window import Window
    Window.size = (330, 600)


def func_name():
    return sys._getframe(1).f_code.co_name


class MainApp(MDApp):
    theme_cls = ThemeManager()
    # screen_manager = ObjectProperty()
    available_devices = ListProperty()
    bonded_devices = ListProperty()
    connected_devices = ListProperty()

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'BlueGray'
        self.theme_cls.primary_hue = '400'
        # self.theme_cls.material_style = 'M3'  # 'M3' breaks MDSwitch
        self.bluetooth_manager = None
        self.bluetooth_adapter = None
        self.bluetooth_socket = None
        self.send_stream = None
        self.recv_stream = None

        # Create storage for saving settings b/w instances of app.
        if platform == 'android':
            # # Get the application's internal storage directory path
            # internal_storage_dir = self.user_data_dir
            # # Construct the filepath for JsonStore relative to the internal storage directory
            # filename = internal_storage_dir + '/my_data.json'
            # # print(internal_storage_dir, filename)
            # logging.debug(f'{internal_storage_dir}, {filename}')

            # # Create a JsonStore instance with the specified filepath
            # self.storage = JsonStore(filename)
            # self.storage.put('key', value1='one', value2='two')
            # self.storage.put('key1', value1='three', value2='four')
            # data = self.storage.get('key')
            # print(data['value1'], data['value2'])
            # data = self.storage.get('key1')
            # print(data['value1'], data['value2'])
            pass

        if platform == 'linux':
            # Get the project directory path
            current_directory = os.getcwd()
            # Add the filename to the path
            filename = os.path.join(current_directory, 'my_data.json')
            # Create a JsonStore instance with the specified filepath
            self.storage = JsonStore(filename)
            # Rest of your application code...
            # self.storage.put('key', value1='one', value2='two')
            # self.storage.put('key1', value1='three', value2='four')
            # data = self.storage.get('key')
            # print(data['value1'], data['value2'])
            # logging.debug(data['value1'], data['value2'])
            # data = self.storage.get('key1')
            # print(data['value1'], data['value2'])
            # logging.debug(data['value1'], data['value2'])

        Builder.load_file('device_controller.kv')
        Builder.load_file('device_connection_dialog.kv')
        Builder.load_file('device_info_list_item.kv')

        Clock.schedule_once(self.request_bluetooth_permissions)

        self.root_screen = RootScreen()
        return self.root_screen

    def on_start(self):
        # This method is called when the application is starting.
        # You can perform additional initialization here.
        pass

    def on_resume(self):
        # This method is called when the application is resumed after being paused or stopped.
        # You can register listeners or start services here.
        pass

    def on_pause(self):
        # This method is called when the application is paused (e.g., when the home button is pressed).
        # You can save application state or perform any necessary cleanup here.
        return True

    def on_stop(self):
        # This method is called when the application is stopped (e.g., when the app is closed).
        # You can perform any necessary cleanup here.
        pass

    def request_bluetooth_permissions(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        if platform == 'android':
            logging.debug(f'Requesting Bluetooth Permissions')
            from android.permissions import request_permissions, Permission
            activity = cast('android.app.Activity', PythonActivity.mActivity)
            package_manager = activity.getPackageManager()
            try:
                logging.debug(f'Attempting checking permissions as objects')
                permissions = [Permission.BLUETOOTH_CONNECT,
                                Permission.BLUETOOTH,
                                Permission.BLUETOOTH_ADMIN,
                                Permission.BLUETOOTH_SCAN]
                if not all(package_manager.checkPermission(permission, activity.getPackageName())
                           == PackageManager.PERMISSION_GRANTED for permission in permissions):
                    bluetooth_dialog = MDDialog(
                        title='Allow Bluetooth access?',
                        text='This app is meant to connect to an ESP32 or other microcontroller via '
                             'Bluetooth. Without Bluetooth permissions it will not function.',
                        buttons=[MDFlatButton(text='Dismiss',
                                              on_release=lambda x: bluetooth_dialog.dismiss()
                                              ),
                                 MDFlatButton(text='OK',
                                              on_release=lambda x:
                                              (request_permissions(permissions),
                                               bluetooth_dialog.dismiss())
                                              )
                                 ]
                    )
                    bluetooth_dialog.open()
            except Exception as e:
                logging.debug(f'Exception occured: {e}')

    def find_bluetooth_devices(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        if platform == 'android':
            context = cast('android.content.Context', mActivity)
            self.bluetooth_manager = context.getSystemService(context.BLUETOOTH_SERVICE)
            self.bluetooth_adapter = self.bluetooth_manager.getAdapter()
            if self.bluetooth_adapter is None:
                no_bluetooth_dialog = MDDialog(
                    title='Sorry!',
                    text='This device does not appear to have Bluetooth capabilities.'
                )
                no_bluetooth_dialog.open()
            elif self.bluetooth_adapter.isEnabled():
                logging.debug('Bluetooth is enabled...')
                self.get_bonded_devices()
            else:
                logging.debug('Bluetooth is disabled...')
                self.enable_bluetooth()

    def enable_bluetooth(self):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        enabled_bluetooth_intent = Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE)
        # All of the following appear to work:
        try:
            logging.debug(f'Trying android.mActivity.startActivity')
            mActivity.startActivity(enabled_bluetooth_intent)
        except Exception as e:
            logging.debug(f'android.mActivity.startActivity failed. Exception: {e}')
        else:
            logging.debug(f'Success: android.mActivity.startActivity')

        try:
            logging.debug(f'Trying PythonActivity.mActivity.startActivity')
            activity = PythonActivity.mActivity
            activity.startActivity(enabled_bluetooth_intent)
        except Exception as e:
            logging.debug(f'PythonActivity.mActivity.startActivity failed. Exception: {e}')
        else:
            logging.debug(f'Success: PythonActivity.mActivity.startActivity')

        try:
            logging.debug(f'Trying android.mActivity.startActivityForResult')
            mActivity.startActivityForResult(enabled_bluetooth_intent, 0)
        except Exception as e:
            logging.debug(f'android.mActivity.startActivityForResult failed. Exception: {e}')
        else:
            logging.debug(f'Success: android.mActivity.startActivityForResult')

        try:
            logging.debug(f'Trying PythonActivity.mActivity.startActivityForResult')
            activity = PythonActivity.mActivity
            activity.startActivityForResult(enabled_bluetooth_intent, 0)
        except Exception as e:
            logging.debug(f'PythonActivity.mActivity.startActivityForResult failed. Exception: {e}')
        else:
            logging.debug(f'Success: PythonActivity.mActivity.startActivityForResult')
        self.get_bonded_devices()

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
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        asyncio.create_task(self._get_bonded_devices())

    async def _get_bonded_devices(self):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        await asyncio.sleep(0.5)
        if platform == 'linux':
            new_devices = [FakeDevice() for _ in range(10)]
            self.bonded_devices[:] = new_devices
        if platform == 'android':
            bonded_devices = self.bluetooth_adapter.getBondedDevices().toArray()
            # Add custom functionality
            self.bonded_devices = [CustomBluetoothDevice(device) for device in bonded_devices]
            logging.debug(f'{self.bonded_devices}')

# def on_bonded_devices(self, *args):
    #     print(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
    #     if platform == 'android':
    #         for num, device in enumerate(self.bonded_devices):
    #             print(num, device)
    #             for k, v in self.get_device_info(device).items():
    #                 if k != 'UUIDs':
    #                     print(f'        {k}: {v}')

    # def get_device_info(self, device):
    #     bluetooth_class = device.getBluetoothClass()
    #     name = device.getName()
    #     address = device.getAddress()
    #     alias = device.getAlias()
    #     bond_state = device.getBondState()
    #     type = device.getType()
    #     UUIDs = device.getUuids()
    #     string_representation = device.toString()
    #     device_info = {'BluetoothClass': bluetooth_class,
    #                    'Name': name,
    #                    'Alias': alias,
    #                    'Address': address,
    #                    'Type': type,
    #                    'BondState': bond_state,
    #                    'UUIDs': UUIDs,
    #                    'StringRepresentation': string_representation,
    #                    }
    #     return device_info

    def connect_as_client(self, device, button):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {device, button}`')
        if platform == 'android':
            asyncio.create_task(self._connect_as_client_android(device, button))
        if platform == 'linux':
            asyncio.create_task(self._connect_as_client_linux(device, button))

    async def _connect_as_client_android(self, device, button):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {device, button}`')
        for k, v in device.get_device_info().items():
            logging.debug(f'{k}: {v}')
        dcd = DeviceConnectionDialog(
            type='custom',
            content_cls=DialogContent(),
        )
        dcd.content_cls.label.text = 'Connecting to... ... ... ' + device.name
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

        UUID for
        Bluetooth Classic Serial Port Profile (SPP)     00001101-0000-1000-8000-00805F9B34FB
        Generic Attribute Profile (GATT)                00001801-0000-1000-8000-00805F9B34FB
        Generic Access Profile (GAP)                    00001800-0000-1000-8000-00805F9B34FB
        ...

        '''
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {device}`')
        try:
            UUID = autoclass('java.util.UUID')
            logging.debug(f'Creating BluetoothSocket')
            esp32_UUID = '00001101-0000-1000-8000-00805F9B34FB'
            self.bluetooth_socket = device.createRfcommSocketToServiceRecord(
                UUID.fromString(esp32_UUID))
            logging.debug(f'BluetoothSocket.connect()')
            self.bluetooth_socket.connect()
            self.recv_stream = self.bluetooth_socket.getInputStream()
            self.send_stream = self.bluetooth_socket.getOutputStream()
        except Exception as e:
            logging.debug(f'Failed to open socket. Exception {e}')
            # Note: @mainthread needed on DeviceConnectionDialog methods to avoid error.
            dcd.content_cls.update_failure(device)
        else:
            logging.debug(f'Successfully opened socket')
            # Note: @mainthread needed on DeviceConnectionDialog methods to avoid error.
            dcd.content_cls.update_success(device)
            device_info = device.get_device_info()
            logging.debug('Device Info')

            for k, v in device.get_device_info().items():
                if k != 'UUIDs':
                    logging.debug(f'\t{k}: {v}')
            logging.debug('UUIDs')
            for uuid in device_info['UUIDs']:
                logging.debug(f'\t {uuid}')
                logging.debug(f'\t\t {uuid.toString()}')
            logging.debug('toString()')
            logging.debug(f'\t {device.toString()}')
            logging.debug('hashCode()')
            logging.debug(f'\t {device.hashCode()}')

    async def _connect_as_client_linux(self, device, button):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {device, button}`')
        dcd = DeviceConnectionDialog(
            type='custom',
            content_cls=DialogContent(),
        )
        dcd.content_cls.label.text = 'Connecting to... ... ... ' + device.name
        dcd.content_cls.dialog = dcd  # back-reference to parent
        dcd.open()
        await asyncio.sleep(2)
        # TODO: Check existing connection (really for android)
        if random.choice([0, 1]):
            dcd.content_cls.update_success(device)
            device_info = device.get_device_info()
            self.save_device(device_info)
        else:
            dcd.content_cls.update_failure(device)

    def save_device(self, device_info):
        # Make UUIDs strings
        uuids = [uuid.toString() for uuid in device_info['UUIDs']]
        device_info['UUIDs'] = uuids
        key = device_info['Address']
        self.storage[key] = device_info
        ret_value = self.storage[key]
        logging.debug(f'Retrieved data for {key}: \n\t{ret_value}')

    def send(self, mode, val):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        logging.debug(f'mode={mode}, val={val}')
        red, green, blue = [0, 0, 0]
        brightness = 100
        # Color Mode - ESP32 will maintain it's current brightness level.
        if mode == 1:
            # White
            if val == 1:
                red, green, blue = [255, 255, 255]
            # Red
            elif val == 2:
                red, green, blue = [255, 0, 0]
            # Orange
            elif val == 3:
                red, green, blue = [255, 130, 0]
            # Yellow
            elif val == 4:
                red, green, blue = [255, 255, 0]
            # Green
            elif val == 5:
                red, green, blue = [0, 255, 0]
            # Blue
            elif val == 6:
                red, green, blue = [0, 0, 255]

        # Dimmer Mode - ESP32 will maintain it's current color.
        if mode == 2:
            brightness = int(val)
        try:
            self.send_stream.write(struct.pack('<B', mode))
            self.send_stream.write(struct.pack('<B', red))
            self.send_stream.write(struct.pack('<B', green))
            self.send_stream.write(struct.pack('<B', blue))
            self.send_stream.write(struct.pack('<B', brightness))
            self.send_stream.write(struct.pack('<b', -1))
            self.send_stream.flush()
        except jnius.JavaException as e:
            if isinstance(e.__java__object__, jnius.JavaIOException):
                # Handle the IOException (Broken pipe) error
                logging.debug("IOException occurred: Broken pipe")
                # Perform any necessary cleanup or recovery actions
            else:
                # Handle other types of Java exceptions
                logging.debug(f'Other Java exception occurred: {e}')
                # Perform appropriate actions for other exceptions
        except Exception as e:
            # Handle any other Python exceptions
            logging.debug(f'Python exception occurred: {e}')
            # Perform appropriate actions for other exceptions
        else:
            logging.debug('Command sent.')


if __name__ == '__main__':
    app = MainApp()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.async_run(async_lib='asyncio'))
    # app.run()