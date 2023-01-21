import asyncio
from bleak import discover
from bleak import BleakClient
from kivy.app import App
from kivy.uix.button import Button


class BluetoothApp(App):
    def build(self):
        self.esp32 = None
        button = Button(text="Connect to ESP32")
        button.bind(on_press=self.connect_to_esp32)
        return button

    async def connect_to_esp32(self, instance):
        devices = await discover()
        for device in devices:
            if device.name == "ESP32":
                self.esp32 = device
                break
        else:
            self.esp32 = None

        if self.esp32 is None:
            print("ESP32 not found.")
            return

        async with BleakClient(self.esp32.address) as client:
            print("Connected to ESP32.")

if __name__ == "__main__":
    BluetoothApp().run()