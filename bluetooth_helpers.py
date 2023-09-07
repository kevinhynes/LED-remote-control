class Command:
    '''
    Template for any possible command that can be sent from app to ESP32.
    An instance of this class is given to DeviceController.send_command().
    '''

    def __init__(self, mode, red=None, green=None, blue=None, dimmer_val=None,
                 num_leds=None, max_brightness=None, color_correction_key=None,
                 color_temperature_correction_key=None):
        self.mode = mode
        self.red = red
        self.green = green
        self.blue = blue
        self.dimmer_val = dimmer_val
        self.num_leds = num_leds
        self.max_brightness = max_brightness
        self.color_correction_key = color_correction_key
        self.color_temperature_correction_key = color_temperature_correction_key