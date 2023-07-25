import asyncio
import os
import struct
import jnius
import logging
import threading
from jnius import autoclass, cast, java_method
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

# Needed for Python code to communicate with Android operating system, sensors, etc.
if platform == 'android':
    from android import mActivity
    from android.permissions import Permission, request_permissions, check_permission

    BluetoothManager = autoclass('android.bluetooth.BluetoothManager')
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
    BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
    # Probably only need PythonActivity?
    Activity = autoclass('android.app.Activity')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    Context = autoclass('android.content.Context')
    IntentFilter = autoclass('android.content.IntentFilter')
    Manifest = autoclass('android.Manifest')
    PackageManager = autoclass('android.content.pm.PackageManager')
    # BroadcastReceiver needed for discovering devices to pair with through the app, difficult to
    # get working right. At current, pairing needs to be done via Android OS.  Once paired, app
    # can connect to 'bonded' devices.
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


class MainApp(MDApp):
    theme_cls = ThemeManager()
    # screen_manager = ObjectProperty()
    available_devices = ListProperty()
    paired_devices = ListProperty()
    connected_devices = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bluetooth_manager = None
        self.bluetooth_adapter = None
        self.bluetooth_socket = None
        self.send_stream = None
        self.recv_stream = None
        self.saved_data = None

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'BlueGray'
        self.theme_cls.primary_hue = '400'
        # self.theme_cls.material_style = 'M3'
        # 'M3' breaks MDSwitch. widget_style=ios looks good but also acts funky

        Builder.load_file('device_controller.kv')
        Builder.load_file('device_connection_dialog.kv')
        Builder.load_file('device_info_list_item.kv')

        Clock.schedule_once(self.request_bluetooth_permissions)
        Clock.schedule_once(self.load_saved_data)

        self.root_screen = RootScreen()
        return self.root_screen

    def on_start(self, *args):
        # This method is called when the application is starting.
        # You can perform additional initialization here.
        logging.warning(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        pass

    def on_resume(self, *args):
        # This method is called when the application is resumed after being paused or stopped.
        # You can register listeners or start services here.
        logging.warning(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        pass

    def on_pause(self, *args):
        # This method is called when the application is paused (e.g., when the home button is pressed).
        # You can save application state or perform any necessary cleanup here.
        logging.warning(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        
        return True

    def on_stop(self, *args):
        # This method is called when the application is stopped (e.g., when the app is closed).
        # You can perform any necessary cleanup here.
        logging.warning(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        if platform == 'android':
            close_thread = threading.Thread(target=self.close_sockets)
            close_thread.start()

    def on_request_close(self, *args):
        logging.warning(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        pass

    def close_sockets(self, *args):
        logging.warning(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        for device in self.connected_devices:
            device.bluetooth_socket.close()

    def request_bluetooth_permissions(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        if platform == 'android':
            logging.debug(f'Requesting Bluetooth Permissions')
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
                    logging.debug(f'If statement')
                    bluetooth_dialog = MDDialog(
                        title='Allow Bluetooth access?',
                        text='This app is meant to connect to an ESP32 or other microcontroller via'
                             'Bluetooth. Without Bluetooth permissions it will not function.',
                        buttons=[MDFlatButton(text='OK',
                                              on_release=lambda x:
                                              (request_permissions(permissions,
                                                                   self.request_bluetooth_permissions_callback),
                                               bluetooth_dialog.dismiss())
                                              )
                                 ]
                    )
                    bluetooth_dialog.open()
                else:
                    logging.debug(f'Else statement')
                    self.get_bluetooth_adapter()
            except Exception as e:
                logging.debug(f'Exception occured: {e}')
            else:
                logging.debug(f'No exception occurred while checking permissions.'
                              f'Did pop-up launch?')

    def request_bluetooth_permissions_callback(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        permissions = [Permission.BLUETOOTH_CONNECT,
                       Permission.BLUETOOTH,
                       Permission.BLUETOOTH_ADMIN,
                       Permission.BLUETOOTH_SCAN]
        if not all(check_permission(permission) for permission in permissions):
            bluetooth_dialog = MDDialog(
                title='App is unstable.',
                text='Without Bluetooth permissions this app will crash.',
                buttons=[MDFlatButton(text='Dismiss',
                                      on_release=lambda x: bluetooth_dialog.dismiss()
                                      ),
                         MDFlatButton(text='Allow Bluetooth',
                                      on_release=lambda x:
                                      (request_permissions(permissions,
                                              self.request_bluetooth_permissions_callback),
                                       bluetooth_dialog.dismiss())
                                      )
                         ]
            )
            bluetooth_dialog.open()
        else:
            self.get_bluetooth_adapter()

    def get_bluetooth_adapter(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        context = cast('android.content.Context', mActivity)
        self.bluetooth_manager = context.getSystemService(context.BLUETOOTH_SERVICE)
        self.bluetooth_adapter = self.bluetooth_manager.getAdapter()
        if self.bluetooth_adapter:
            logging.debug(f'Successfully got BluetoothAdapter')
        else:
            logging.debug(f'BluetoothAdapter not found.')

    def find_bluetooth_devices(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        if platform == 'android':
            if self.bluetooth_adapter is None:
                no_bluetooth_dialog = MDDialog(
                    title='Sorry!',
                    text='This device does not appear to have Bluetooth capabilities.'
                )
                no_bluetooth_dialog.open()
            elif self.bluetooth_adapter.isEnabled():
                logging.debug(f'Bluetooth is enabled...')
                Clock.schedule_once(self.get_paired_devices)
            else:
                logging.debug(f'Bluetooth is disabled...')
                Clock.schedule_once(self.enable_bluetooth)
                Clock.schedule_once(self.get_paired_devices)

        if platform == 'linux':
            self.get_paired_devices()

    def enable_bluetooth(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        enabled_bluetooth_intent = Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE)
        # All of the following appear to work:
        # try:
        #     logging.debug(f'Trying android.mActivity.startActivity')
        #     mActivity.startActivity(enabled_bluetooth_intent)
        # except Exception as e:
        #     logging.debug(f'android.mActivity.startActivity failed. Exception: {e}')
        # else:
        #     logging.debug(f'Success: android.mActivity.startActivity')

        try:
            logging.debug(f'Trying PythonActivity.mActivity.startActivity')
            activity = PythonActivity.mActivity
            activity.startActivity(enabled_bluetooth_intent)
        except Exception as e:
            logging.debug(f'PythonActivity.mActivity.startActivity failed. Exception: {e}')
        else:
            logging.debug(f'Success: PythonActivity.mActivity.startActivity')

        # try:
        #     logging.debug(f'Trying android.mActivity.startActivityForResult')
        #     mActivity.startActivityForResult(enabled_bluetooth_intent, 0)
        # except Exception as e:
        #     logging.debug(f'android.mActivity.startActivityForResult failed. Exception: {e}')
        # else:
        #     logging.debug(f'Success: android.mActivity.startActivityForResult')
        #
        # try:
        #     logging.debug(f'Trying PythonActivity.mActivity.startActivityForResult')
        #     activity = PythonActivity.mActivity
        #     activity.startActivityForResult(enabled_bluetooth_intent, 0)
        # except Exception as e:
        #     logging.debug(f'PythonActivity.mActivity.startActivityForResult failed. Exception: {e}')
        # else:
        #     logging.debug(f'Success: PythonActivity.mActivity.startActivityForResult')

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

    # def get_paired_devices(self, *args):
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
    #     asyncio.create_task(self._get_paired_devices())

    def get_paired_devices(self, *args):
        # FindDevicesScreen.paired_devices bound to app.paired_devices
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with {args}')
        if platform == 'linux':
            new_devices = [FakeDevice() for _ in range(10)]
            self.paired_devices[:] = new_devices
        if platform == 'android':
            try:
                paired_devices = self.bluetooth_adapter.getBondedDevices().toArray()
                self.paired_devices = [CustomBluetoothDevice(bluetooth_device=device)
                                       for device in paired_devices]
            except Exception as e:
                logging.debug(f'Exception occured: {e}')
            else:
                logging.debug(f'Paired Devices: {self.paired_devices}')

    def connect_as_client(self, device, button):
        logging.debug(
            f'`{self.__class__.__name__}.{func_name()} called with args: {device, button}`')
        if platform == 'android':
            self._connect_as_client_android(device, button)
        if platform == 'linux':
            self._connect_as_client_linux(device, button)

    def reconnect_as_client(self, *args):
        logging.debug(
            f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        if platform == 'android':
            self._reconnect_as_client_android()
        if platform == 'linux':
            self._reconnect_as_client_linux()

    def _connect_as_client_android(self, device, button):
        logging.debug(
            f'`{self.__class__.__name__}.{func_name()} called with args: {device, button}`')
        for k, v in device.get_device_info().items():
            logging.debug(f'{k}: {v}')
        dcd = DeviceConnectionDialog(
            type='custom',
            content_cls=DialogContent(),
        )
        dcd.content_cls.label.text = 'Connecting to...' + device.name
        dcd.content_cls.dialog = dcd  # back-reference to parent
        dcd.open()
        # Must use separate thread for connecting to Bluetooth device to keep GUI functional.
        t = Thread(target=self._connect_BluetoothSocket, args=[device, dcd])
        t.start()

    def _reconnect_as_client_android(self):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        for device in self.connected_devices:
            self._reconnect_BluetoothSocket(device)

    def _connect_BluetoothSocket(self, device, dcd):
        '''
        Create and open the android.bluetooth.BluetoothSocket connection to the ESP32.
        BluetoothSocket.connect() is a blocking call that stops the main Kivy thread from executing
        and pauses the GUI; execute this function in a separate thread to avoid this problem.
        Conversely, Kivy GUI (graphics) instructions cannot be changed from outside main Kivy
        thread. Use kivy.clock @mainthread decorator on the MDDialog methods that are initiated here
        to keep graphics instructions in the main thread.

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
            device.bluetooth_socket = device.createRfcommSocketToServiceRecord(
                UUID.fromString(esp32_UUID))
            logging.debug(f'BluetoothSocket.connect()')
            device.bluetooth_socket.connect()
            device.recv_stream = device.bluetooth_socket.getInputStream()
            device.send_stream = device.bluetooth_socket.getOutputStream()
        except Exception as e:
            logging.debug(f'Failed to open socket. Exception {e}')
            # Note: @mainthread needed on DeviceConnectionDialog methods to avoid error.
            dcd.content_cls.update_failure(device)
        else:
            logging.debug(f'Successfully opened socket')
            # Note: @mainthread needed on DeviceConnectionDialog methods to avoid error.
            dcd.content_cls.update_success(device)
            self.save_device(device)

    def _reconnect_BluetoothSocket(self, device):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {device}`')
        # if device.isConnected():
        #     dialog = MDDialog(text='Device already connected')
        #     dialog.open()
        #     Clock.schedule_once(dialog.dismiss, 3)
        #     return
        try:
            logging.debug(f'Creating BluetoothSocket')
            UUID = autoclass('java.util.UUID')
            esp32_UUID = '00001101-0000-1000-8000-00805F9B34FB'
            device.bluetooth_socket = device.createRfcommSocketToServiceRecord(
                UUID.fromString(esp32_UUID))
            logging.debug(f'BluetoothSocket.connect()')
            device.bluetooth_socket.connect()
            device.recv_stream = device.bluetooth_socket.getInputStream()
            device.send_stream = device.bluetooth_socket.getOutputStream()
        except Exception as e:
            logging.debug(f'Failed to open socket. Exception {e}')
            logging.debug(f'Retrying...')
            UUID = autoclass('java.util.UUID')
            esp32_UUID = '00001101-0000-1000-8000-00805F9B34FB'
            device.bluetooth_socket = device.createRfcommSocketToServiceRecord(
                UUID.fromString(esp32_UUID))
            logging.debug(f'BluetoothSocket.connect()')
            device.bluetooth_socket.connect()
            device.recv_stream = device.bluetooth_socket.getInputStream()
            device.send_stream = device.bluetooth_socket.getOutputStream()
        else:
            logging.debug(f'Successfully opened socket')

    def _connect_as_client_linux(self, device, button):
        logging.debug(
            f'`{self.__class__.__name__}.{func_name()} called with args: {device, button}`')
        dcd = DeviceConnectionDialog(
            type='custom',
            content_cls=DialogContent(),
        )
        dcd.content_cls.label.text = 'Connecting to...' + device.name
        dcd.content_cls.dialog = dcd  # back-reference to parent
        dcd.open()
        # TODO: Check existing connection (really for android)
        if random.choice([0, 1]):
            dcd.content_cls.update_success(device)
            self.save_device(device)
        else:
            dcd.content_cls.update_failure(device)

    def _reconnect_as_client_linux(self):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        for device in self.connected_devices:
            if random.choice([0, 1, 2, 3, 4]):
                # Green status
                device.connected_status()
            else:
                # Red Status
                device.disconnected_status()

    def load_saved_data(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        if platform == 'android':
            internal_storage_dir = self.user_data_dir
            filename = internal_storage_dir + '/saved_data.json'
            logging.debug(f'Loading saved data on Android.')
            logging.debug(f'\tCurrent working directory: {internal_storage_dir},'
                          f'\tFilename: {filename}')
            self.saved_data = JsonStore(filename)

            loaded_connected_devices = []
            for key in self.saved_data.keys():
                logging.debug(f'Key: {key}\n'
                              f'Value: {self.saved_data[key]}')
                if self.bluetooth_adapter and \
                        self.bluetooth_adapter.checkBluetoothAddress(str(key)):
                    user_assigned_alias = self.saved_data[key]['User Assigned Alias']
                    bluetooth_device = self.bluetooth_adapter.getRemoteDevice(str(key))
                    custom_bluetooth_device = CustomBluetoothDevice(
                        bluetooth_device=bluetooth_device,
                        user_assigned_alias=user_assigned_alias
                    )
                    loaded_connected_devices.append(custom_bluetooth_device)
            # Just change the property once.
            self.connected_devices[:] = loaded_connected_devices

        if platform == 'linux':
            # internal_storage_dir is /home/fourteen/.config/main  ??
            internal_storage_dir = self.user_data_dir
            filename = os.path.join(internal_storage_dir, 'saved_data.json')
            logging.debug(f'Loading saved data on Linux.')
            logging.debug(f'\tCurrent working directory: {internal_storage_dir},'
                          f'\tFilename: {filename}')
            # Create a JsonStore instance with the specified filepath
            self.saved_data = JsonStore(filename)

            loaded_connected_devices = []
            for key in self.saved_data.keys():
                logging.debug(f'Key: {key}\n'
                              f'Value: {self.saved_data[key]}')
                device_info = self.saved_data[key]
                saved_fake_device = FakeDevice(device_info)
                loaded_connected_devices.append(saved_fake_device)
            # Just change the property once.
            self.connected_devices[:] = loaded_connected_devices
        self.reconnect_as_client()

    def clear_saved_data(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        self.saved_data.clear()
        self.load_saved_data()

    def save_device(self, device):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with device {device}')
        device_info = device.get_device_info()
        # Make UUIDs strings
        uuids = [uuid.toString() for uuid in device_info['UUIDs']]
        device_info['UUIDs'] = uuids
        mac_address = device_info['Address']
        self.saved_data[mac_address] = device_info

    def forget_device(self, device):
        device_info = device.get_device_info()
        mac_address = device_info['Address']
        try:
            self.saved_data.delete(mac_address)
        except KeyError as e:
            logging.debug(f'No device with address {mac_address} found in saved data.')
        except Exception as e:
            logging.debug(f'Exception occured while trying to delete '
                          f'{mac_address} from saved data.')
        for i, device in enumerate(self.connected_devices):
            if device_info['Address'] == mac_address:
                del self.connected_devices[i]
                break

    def show_saved_data(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        for key in self.saved_data.keys():
            logging.debug(f'\tKey: {key}'
                          f'\tDevice: {self.saved_data[key]}')


if __name__ == '__main__':
    app = MainApp()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(app.async_run(async_lib='asyncio'))
    app.run()
