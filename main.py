from kivy.app import App
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.colorpicker import ColorPicker

Config.set('graphics', 'width', 325)
Config.set('graphics', 'height', 600)


from jnius import autoclass
# BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')


class CornerLightMenu(BoxLayout):
    pass


class CornerLightApp(App):
    def build(self):
        return CornerLightMenu()


if __name__ == "__main__":
    CornerLightApp().run()
