import asyncio
import os
import struct
import jnius
import logging
import threading
from jnius import autoclass, cast, java_method
from threading import Thread
from kivy.config import Config
from kivy.lang import Builder
from kivymd.theming import ThemeManager
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.button import MDFlatButton
from screens import *
import atexit

logging.basicConfig(level=logging.DEBUG)

# Developer Mode:
# Config.set('kivy', 'log_level', 'debug')

# Needed for Python code to communicate with Android operating system, sensors, etc.
if platform == 'android':
    from android import mActivity
    from android.permissions import Permission, request_permissions, check_permission
    from android.broadcast import BroadcastReceiver

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
    UUID = autoclass('java.util.UUID')
    Settings = autoclass('android.provider.Settings')

if platform == 'linux':
    from kivy.core.window import Window
    Window.size = (330, 600)


class MainApp(MDApp):
    theme_cls = ThemeManager()
    available_devices = ListProperty()
    paired_devices = ListProperty()
    loaded_devices = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bluetooth_manager = None
        self.bluetooth_adapter = None
        self.permissions = [Permission.BLUETOOTH,
                            Permission.BLUETOOTH_ADMIN,
                            Permission.BLUETOOTH_CONNECT,
                            Permission.BLUETOOTH_SCAN] if platform == 'android' else []
        self.broadcast_receiver = self._get_broadcast_receiver() if platform == 'android' else None
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
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')

    def on_resume(self, *args):
        # This method is called when the application is resumed after being paused or stopped.
        # You can register listeners or start services here.
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')

    def on_pause(self, *args):
        # This method is called when the application is paused (e.g., when the home button is pressed).
        # You can save application state or perform any necessary cleanup here.
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        # if platform == 'android':
        #     close_thread = threading.Thread(target=self.close_sockets)
        #     close_thread.start()
        return True

    def on_stop(self, *args):
        # This method is supposed to be called when the application is stopped (e.g., when the app
        # is closed) but it doesn't appear to ever get called.
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        if platform == 'android':
            close_thread = threading.Thread(target=self.close_sockets)
            close_thread.start()

    def close_sockets(self, *args):
        logging.warning(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        for device in self.loaded_devices:
            if device.bluetooth_socket:
                device.bluetooth_socket.close()

    def close_socket(self, address):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` was called with address {address}')
        for device in self.loaded_devices:
            if device.getAddress() == address and device.bluetooth_socket:
                logging.debug(f'Found saved device with matching address,'
                              f'closing BluetoothSocket...')
                device.bluetooth_socket.close()
                break

    def _get_broadcast_receiver(self):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        actions = [BluetoothDevice.ACTION_ACL_CONNECTED,
                   BluetoothDevice.ACTION_ACL_DISCONNECTED,
                   BluetoothDevice.ACTION_ACL_DISCONNECT_REQUESTED,
                   BluetoothAdapter.ACTION_CONNECTION_STATE_CHANGED,
                   BluetoothAdapter.ACTION_STATE_CHANGED,]
        br = BroadcastReceiver(self.on_broadcast_received, actions)
        br.start()
        return br

    def on_broadcast_received(self, context, intent):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with context, intent: '
                      f'{context, intent}')
        try:
            logging.debug(f'Getting action...')
            action = intent.getAction()
        except Exception as e:
            logging.debug(f'Exception occurred trying to read device or action from intent: {e}')
        else:
            logging.debug(f'Successfully got action: {action}')
        try:
            if action == BluetoothDevice.ACTION_ACL_DISCONNECTED:
                device = cast(BluetoothDevice, intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE))
                logging.debug(f'{device.getName(), device.getAddress()} disconnected')
                # If this device is saved / connected, need to get the CustomBluetoothDevice
                # instance to get the BluetoothSocket and close it.  Here `device` is an
                # Android BluetoothDevice - it does not hold a reference to the BluetoothSocket.
                self.close_socket(device.getAddress())
                controllers_screen = self.root_screen.screen_manager.get_screen('controllers')
                controllers_screen.update_controller_connection_status(device.getAddress(), False)

            elif action == BluetoothDevice.ACTION_ACL_DISCONNECT_REQUESTED:
                device = cast(BluetoothDevice, intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE))
                logging.debug(f'{device.getName(), device.getAddress()} disconnect requested')
            elif action == BluetoothDevice.ACTION_ACL_CONNECTED:
                device = cast(BluetoothDevice, intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE))
                logging.debug(f'{device.getName(), device.getAddress()} connected')
                controllers_screen = self.root_screen.screen_manager.get_screen('controllers')
                controllers_screen.update_controller_connection_status(device.getAddress(), True)

        except Exception as e:
            logging.debug(f'Exception occurred reading a BluetoothDevice broadcast: {e}')
        else:
            logging.debug(f'Successfully read a BluetoothDevice broadcast.')

        try:
            if action == BluetoothAdapter.ACTION_CONNECTION_STATE_CHANGED:
                state = intent.getIntExtra(BluetoothAdapter.EXTRA_CONNECTION_STATE, -1)
                if state == BluetoothAdapter.STATE_CONNECTED:
                    logging.debug(f'BluetoothAdapter connected state')
                elif state == BluetoothAdapter.STATE_DISCONNECTED:
                    logging.debug(f'BluetoothAdapter disconnected state')
                    self.close_sockets()
            elif action == BluetoothAdapter.ACTION_STATE_CHANGED:
                state = intent.getIntExtra(BluetoothAdapter.EXTRA_STATE,
                                           BluetoothAdapter.STATE_OFF)
                if state == BluetoothAdapter.STATE_ON:
                    logging.debug(f'Bluetooth enabled broadcast received, getting paired devices...')
                    self.get_paired_devices()
                elif state == BluetoothAdapter.STATE_OFF:
                    logging.debug(f'Bluetooth disabled broadcast received...')
        except Exception as e:
            logging.debug(f'Exception occurred reading a BluetoothAdapter broadcast: {e}')
        else:
            logging.debug(f'Successfully read a BluetoothAdapter broadcast.')

    # def start_discovery(self, *args):
    #     # No longer needed, not doing Bluetooth scanning to avoid unnecessary permissions.
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
    #     if platform == 'linux':
    #         new_devices = [FakeDevice() for _ in range(10)]
    #         self.available_devices[:] = new_devices
    #     if platform == 'android':
    #         try:
    #             print('In try block')
    #             # This is kind of working?
    #             actions = [BluetoothDevice.ACTION_FOUND,
    #                        BluetoothAdapter.ACTION_DISCOVERY_STARTED,
    #                        BluetoothAdapter.ACTION_DISCOVERY_FINISHED]
    #             self.broadcast_receiver = BroadcastReceiver(self.on_broadcast_received,
    #                                                         actions=actions)
    #             self.broadcast_receiver.start()
    #             activity = PythonActivity.mActivity
    #             intent_filter = IntentFilter()
    #             intent_filter.addAction(BluetoothDevice.ACTION_FOUND)
    #             activity.registerReceiver(self.bluetooth_discovery_receiver, intent_filter)
    #             if not self.bluetooth_adapter.startDiscovery():
    #                 logging.debug(f'Bluetooth scan failed...')
    #             # Wait for discovery to complete...
    #             activity.unregisterReceiver(self.bluetooth_discovery_receiver)
    #         except Exception as e:
    #             print(f'BroadcastReceiver failed with Exception: {e}')
    #         else:
    #             print(f'BroadcastReceiver success')
    #
    # def on_broadcast_received(self, context, intent):
    #     # No longer needed, not doing Bluetooth scanning to avoid unnecessary permissions.
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
    #     logging.debug(f'Conext: {context}, Intent: {intent}')
    #     action = intent.getAction()
    #     if BluetoothDevice.ACTION_FOUND == action:
    #         device = cast(BluetoothDevice, intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE))
    #         logging.debug(f'Found device: {device.getName()} {device.getAddress()}')

    def request_bluetooth_permissions(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        if platform == 'android':
            logging.debug(f'Requesting Bluetooth Permissions')
            try:
                logging.debug(f'Attempting checking permissions as objects')
                if not all(check_permission(permission) for permission in self.permissions):
                    bluetooth_dialog = MDDialog(
                        title='Allow Bluetooth access?',
                        text='This app is meant to connect to an ESP32 or other microcontroller via'
                             'Bluetooth. Without Bluetooth permissions it will not function.',
                        buttons=[MDFlatButton(text='OK',
                                              on_release=lambda x:
                                              (request_permissions(self.permissions,
                                                                   self.request_bluetooth_permissions_callback),
                                               bluetooth_dialog.dismiss())
                                              )
                                 ]
                    )
                    bluetooth_dialog.open()
                else:
                    self.get_bluetooth_adapter()
            except Exception as e:
                logging.debug(f'Exception occured: {e}')
            else:
                logging.debug(f'No exception occurred while checking permissions.'
                              f'Did pop-up launch?')

    @mainthread
    def request_bluetooth_permissions_callback(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        # Needs @mainthread because this callback is executed outside of the main thread,
        # but creates a pop-up window (GUI instructions must be within the main thread).
        if not all(check_permission(permission) for permission in self.permissions):
            bluetooth_dialog = MDDialog(
                title='App is unstable',
                text='Without Bluetooth permissions this app will likely crash. To enable later, '
                     'give this app "Nearby devices" permission in your app settings.',
                buttons=[MDFlatButton(text='Dismiss',
                                      on_release=lambda x: bluetooth_dialog.dismiss()
                                      ),
                         MDFlatButton(text='Allow Bluetooth',
                                      on_release=lambda x:
                                      (request_permissions(self.permissions,
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

    def get_paired_devices(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        if platform == 'android':
            if self.bluetooth_adapter is None:
                no_bluetooth_dialog = MDDialog(
                    title='Sorry!',
                    text='This device does not appear to have Bluetooth capabilities.'
                )
                no_bluetooth_dialog.open()
            elif not self.bluetooth_adapter.isEnabled():
                logging.debug(f'Bluetooth is disabled...')
                self.enable_bluetooth()
            else:
                logging.debug(f'Bluetooth is enabled...')
            try:
                paired_devices = self.bluetooth_adapter.getBondedDevices().toArray()
                saved_device_addresses = {device.getAddress() for device in self.loaded_devices}
                self.paired_devices = [CustomBluetoothDevice(bluetooth_device=device)
                                       for device in paired_devices
                                       if not device.getAddress() in saved_device_addresses]
            except Exception as e:
                logging.debug(f'Exception occured: {e}')
            else:
                logging.debug(f'Paired Devices: {self.paired_devices}')
        if platform == 'linux':
            new_devices = [FakeDevice() for _ in range(10)]
            self.paired_devices[:] = new_devices

    def enable_bluetooth(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        enable_bluetooth = Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE)
        try:
            logging.debug(f'Enabling Bluetooth with PythonActivity.mActivity.startActivity')
            activity = PythonActivity.mActivity
            activity.startActivity(enable_bluetooth)
        except Exception as e:
            logging.debug(f'Enabling Bluetooth with PythonActivity.mActivity.startActivity failed. '
                          f'Exception: {e}')
        else:
            logging.debug(f'Successfully enabled Bluetooth with '
                          f'PythonActivity.mActivity.startActivity')

    def open_bluetooth_settings(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` was called with {args}')
        # Called from FindDevicesScreen PairedDevicesHeader's info button
        # Both of these work:
        # try:
        #     logging.debug(f'Open Bluetooth Settings attempt number one')
        #     intent = Intent(Intent.ACTION_MAIN)
        #     intent.setClassName('com.android.settings', 'com.android.settings.Settings$BluetoothSettingsActivity')
        #     activity = PythonActivity.mActivity
        #     activity.startActivity(intent)
        # except Exception as e:
        #     logging.debug(f'Exception on attempt number one. Exception: {e}')
        # else:
        #     logging.debug(f'Success on attempt number one')
        try:
            logging.debug(f'Open Bluetooth Settings attempt number two')
            open_bluetooth_settings = Intent(Settings.ACTION_BLUETOOTH_SETTINGS)
            activity = PythonActivity.mActivity
            activity.startActivity(open_bluetooth_settings)
        except Exception as e:
            logging.debug(f'Exception on attempt number two. Exception: {e}')
        else:
            logging.debug(f'Success on attempt number two')

    def connect_as_client(self, device, button):
        logging.debug(
            f'`{self.__class__.__name__}.{func_name()} called with args: {device, button}`')
        if platform == 'android':
            self._connect_as_client_android(device, button)
        if platform == 'linux':
            self._connect_as_client_linux(device, button)

    # def _check_overwrite(self, device):
    #     for saved_device in self.loaded_devices:
    #         if device.getAddress() == saved_device.getAddress():
    #             # 1. User attempting to re-connect a device's BluetoothSocket connection from the
    #             # Maybe the device's BluetoothSocket has become disconnected.
    #             d = MDDialog(title='Overwrite saved device?',
    #                          text=f'A device with a matching MAC address has already been saved.\n'
    #                               f'Saved device:\n'
    #                               f'\tAddress: {saved_device.getAddress()}\n'
    #                               f'\tName: {saved_device.getName()}\n'
    #                               f'\tNickname: {saved_device.nickname}\n'
    #                               f'This device:\n'
    #                               f'\tAddress: {device.getAddress()}\n'
    #                               f'\tName: {device.getName()}\n'
    #                               f'\tNickname: {device.nickname}\n',
    #                          buttons=[MDFlatButton(text='Cancel',
    #                                                on_release=lambda x: d.dismiss()),
    #                                   MDFlatButton(text='Overwrite',
    #                                                on_release=lambda x: d.dismiss())]
    #                  )

    def _connect_as_client_android(self, device, button=None):
        logging.debug(
            f'`{self.__class__.__name__}.{func_name()} called with args: {device, button}`')
        dcd = DeviceConnectionDialog(
            type='custom',
            content_cls=DialogContent(),
        )
        dcd.content_cls.label.text = 'Connecting to... ' + device.name
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
            logging.debug(f'Creating BluetoothSocket')
            esp32_UUID = '00001101-0000-1000-8000-00805F9B34FB'
            device.bluetooth_socket = device.createRfcommSocketToServiceRecord(
                UUID.fromString(esp32_UUID))
            device.bluetooth_socket.connect()
            device.recv_stream = device.bluetooth_socket.getInputStream()
            device.send_stream = device.bluetooth_socket.getOutputStream()
        except Exception as e:
            logging.debug(f'Failed to open socket in MainApp._connect_BluetoothSocket.'
                          f'Exception {e}')
            # NOTE: @mainthread needed on DeviceConnectionDialog methods to avoid error.
            dcd.content_cls.update_failure(device)
        else:
            logging.debug(f'Successfully opened socket')
            # NOTE: @mainthread needed on DeviceConnectionDialog methods to avoid error.
            dcd.content_cls.update_success(device)
            self._add_new_connected_device(device)

    @mainthread
    def _add_new_connected_device(self, device):
        # Needs @mainthread because calling function is outside of main thread.
        self.save_device(device)
        self.root_screen.screen_manager.current = 'controllers'

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

    # def reconnect_as_client(self, *args):
    #     logging.debug(
    #         f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
    #     if platform == 'android':
    #         self._reconnect_as_client_android()
    #     if platform == 'linux':
    #         self._reconnect_as_client_linux()
    #
    # def _reconnect_as_client_android(self):
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
    #     for device in self.loaded_devices:
    #         self._reconnect_BluetoothSocket(device)

    # def _reconnect_BluetoothSocket(self, device):
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {device}`')
    #     if device.isConnected():
    #         dialog = MDDialog(text='Device already connected')
    #         dialog.open()
    #         Clock.schedule_once(dialog.dismiss, 3)
    #         # return
    #     try:
    #         logging.debug(f'Creating BluetoothSocket')
    #         UUID = autoclass('java.util.UUID')
    #         esp32_UUID = '00001101-0000-1000-8000-00805F9B34FB'
    #         device.bluetooth_socket = device.createRfcommSocketToServiceRecord(
    #             UUID.fromString(esp32_UUID))
    #         logging.debug(f'BluetoothSocket.connect()')
    #         device.bluetooth_socket.connect()
    #         device.recv_stream = device.bluetooth_socket.getInputStream()
    #         device.send_stream = device.bluetooth_socket.getOutputStream()
    #     except Exception as e:
    #         logging.debug(f'Failed to open socket. Exception {e}')
    #         logging.debug(f'Retrying...')
    #         self._retry_BluetoothSocket(device)
    #     else:
    #         logging.debug(f'Successfully opened socket')

    # def _retry_BluetoothSocket(self, device):
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {device}`')
    #     try:
    #         logging.debug(f'Retrying to create BluetoothSocket')
    #         UUID = autoclass('java.util.UUID')
    #         esp32_UUID = '00001101-0000-1000-8000-00805F9B34FB'
    #         device.bluetooth_socket = device.createRfcommSocketToServiceRecord(
    #             UUID.fromString(esp32_UUID))
    #         logging.debug(f'BluetoothSocket.connect()')
    #         device.bluetooth_socket.connect()
    #         device.recv_stream = device.bluetooth_socket.getInputStream()
    #         device.send_stream = device.bluetooth_socket.getOutputStream()
    #     except Exception as e:
    #         logging.debug(f'Failed to open socket. Exception {e}')
    #         if device.isConnected():
    #             dialog = MDDialog(text='Device off or out of range.')
    #             dialog.open()
    #             Clock.schedule_once(dialog.dismiss, 3)
    #     else:
    #         logging.debug(f'Successfully opened socket on retry.')

    def _reconnect_as_client_linux(self):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        for device in self.loaded_devices:
            if random.choice([0, 1, 2, 3, 4]):
                # Green status
                device.connected_status()
            else:
                # Red Status
                device.disconnected_status()

    def load_saved_data(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        if platform == 'android':
            # This should help app function, causes error. App should have bluetooth_adapter at this
            # point but doesn't...
            # if not self.bluetooth_adapter.isEnabled():
            #     self.enable_bluetooth()
            internal_storage_dir = self.user_data_dir
            filename = internal_storage_dir + '/saved_data.json'
            logging.debug(f'\tLoading saved data on Android...')
            logging.debug(f'\tCurrent working directory: {internal_storage_dir},'
                          f'\tFilename: {filename}')
            self.saved_data = JsonStore(filename)

            loaded_devices = []
            for key in self.saved_data.keys():
                logging.debug(f'\tKey: {key}\n'
                              f'\tValue: {self.saved_data[key]}')
                if self.bluetooth_adapter and \
                        self.bluetooth_adapter.checkBluetoothAddress(str(key)):
                    bluetooth_device = self.bluetooth_adapter.getRemoteDevice(str(key))
                    custom_bluetooth_device = CustomBluetoothDevice(
                        bluetooth_device=bluetooth_device,
                        name=self.saved_data[key]['Name'],
                        address=self.saved_data[key]['Address'],
                        nickname=self.saved_data[key]['Nickname']
                    )
                    logging.debug(f'CustomBluetoothDevice.bluetooth_device: {bluetooth_device}')
                    loaded_devices.append(custom_bluetooth_device)
            # Just change the property once.
            self.loaded_devices[:] = loaded_devices
            logging.debug(f'\tDone loading saved data on Android with BluetoothAdapter: '
                          f'{self.bluetooth_adapter}')
            logging.debug(f'\tSaved Devices: {self.loaded_devices}')

        if platform == 'linux':
            # internal_storage_dir is /home/fourteen/.config/main  ??
            internal_storage_dir = self.user_data_dir
            filename = os.path.join(internal_storage_dir, 'saved_data.json')
            logging.debug(f'Loading saved data on Linux.')
            logging.debug(f'\tCurrent working directory: {internal_storage_dir},'
                          f'\tFilename: {filename}')
            # Create a JsonStore instance with the specified filepath
            self.saved_data = JsonStore(filename)

            loaded_devices = []
            for key in self.saved_data.keys():
                logging.debug(f'Key: {key}\n'
                              f'Value: {self.saved_data[key]}')
                device_info = self.saved_data[key]
                saved_fake_device = FakeDevice(device_info)
                loaded_devices.append(saved_fake_device)
            # Just change the property once.
            self.loaded_devices[:] = loaded_devices

    def clear_saved_data(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        self.saved_data.clear()
        self.load_saved_data()

    def save_device(self, device):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with device {device}')
        # Save to database.
        device_info = device.get_device_info()
        # -make UUIDs strings to save them
        uuids = [uuid.toString() for uuid in device_info['UUIDs']]
        device_info['UUIDs'] = uuids
        mac_address = device_info['Address']
        self.saved_data[mac_address] = device_info

        # If device was renamed, overwrite it.
        for i, saved_device in enumerate(self.loaded_devices):
            if saved_device.getAddress() == device.getAddress():
                self.loaded_devices[i] = device
                return
        # Update paired and saved device lists.
        self.loaded_devices.append(device)
        paired_addresses = {device.getAddress() for device in self.paired_devices}
        for i, device in enumerate(self.paired_devices):
            if device.getAddress() in paired_addresses:
                del self.paired_devices[i]
                break

    def forget_device(self, device):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with: {device}`')
        # Delete from database, close BluetoothSocket, move back to paired_devices.
        device_info = device.get_device_info()
        mac_address = device_info['Address']
        try:
            self.saved_data.delete(mac_address)
        except KeyError as e:
            logging.debug(f'No device with address {mac_address} found in saved data.')
        except Exception as e:
            logging.debug(f'Exception occured while trying to delete '
                          f'{mac_address} from saved data.')
        for i, device in enumerate(self.loaded_devices):
            if device_info['Address'] == mac_address:
                if platform == 'android':
                    self.paired_devices.append(self.loaded_devices[i])
                    self.close_socket(mac_address)
                del self.loaded_devices[i]
                break

    def show_saved_data(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()} called with args: {args}`')
        for key in self.saved_data.keys():
            logging.debug(f'\tKey: {key}'
                          f'\tDevice: {self.saved_data[key]}')


if __name__ == '__main__':
    app = MainApp()

    # Kivy's on_stop method does not get called. Need to shut down the app gracefully.
    if platform == 'android':
        atexit.register(app.close_sockets)
        # close_thread = threading.Thread(target=app.close_sockets)
        # close_thread.start()
    app.run()
    logging.debug(f'MainApp.run() has ended. Shutting down...')
