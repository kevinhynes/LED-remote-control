from kivy.app import App
from kivy.uix.button import Button
from jnius import autoclass

# Trying to get past permissions issue.
from kivy import platform
from android.permissions import request_permissions, Permission
request_permissions([Permission.BLUETOOTH_CONNECT, Permission.BLUETOOTH,
                     Permission.BLUETOOTH_ADMIN, Permission.BLUETOOTH_SCAN])


class BluetoothApp(App):
    def build(self):
        self.bluetooth_adapter = autoclass('android.bluetooth.BluetoothAdapter')
        self.bluetooth_device = autoclass('android.bluetooth.BluetoothDevice')
        self.bluetooth_socket = autoclass('android.bluetooth.BluetoothSocket')

        self.adapter = self.bluetooth_adapter.getDefaultAdapter()
        self.paired_devices = self.adapter.getBondedDevices().toArray()

        for device in self.paired_devices:
            if device.getName() == "ESP32":
                self.esp32 = device
                break
        else:
            self.esp32 = None

        button = Button(text="Connect to ESP32 via pyjnuis")
        button.bind(on_press=self.connect_to_esp32)
        return button

    def connect_to_esp32(self, instance):
        if self.esp32 is None:
            print("ESP32 not found.")
            return

        try:
            self.socket = self.esp32.createRfcommSocketToServiceRecord(
                self.bluetooth_device.Serial_UUID)
            self.socket.connect()
            print("Connected to ESP32.")
        except Exception as e:
            print("Failed to connect:", e)

if __name__ == "__main__":
    BluetoothApp().run()