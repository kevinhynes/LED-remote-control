from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
import pygatt

class MyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        self.label = Label(text='Disconnected')
        layout.add_widget(self.label)

        self.adapter = None
        self.device = None

        connect_button = Button(text='Connect')
        connect_button.bind(on_press=self.connect)
        layout.add_widget(connect_button)

        send_button = Button(text='Send')
        send_button.bind(on_press=self.send_data)
        layout.add_widget(send_button)

        return layout

    def connect(self, instance):
        if self.device:
            self.device.disconnect()
            self.label.text = 'Disconnected'
            self.device = None
        else:
            # Replace '00:11:22:33:44:55' with the MAC address of your ESP32
            try:
                self.adapter = pygatt.GATTToolBackend()
                self.adapter.start()
                self.device = self.adapter.connect('00:11:22:33:44:55')
                self.label.text = 'Connected'
            except Exception as e:
                self.label.text = 'Device not found'
                self.device = None

    def send_data(self, instance):
        if self.device:
            # replace 'handle' with the handle of the characteristic you want to write to
            self.device.char_write(handle, b'Hello, ESP32!')

if __name__ == '__main__':
    MyApp().run()
