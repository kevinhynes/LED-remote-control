from math import pi, sin, trunc
import logging
import colorsys
from typing import List
from threading import Thread
from jnius import cast, autoclass
from functools import partial
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.clock import mainthread
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty
from kivy.metrics import dp, sp
from kivy.graphics import Color, Line, Rectangle
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.button import MDIconButton, MDRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import BaseListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.selectioncontrol import MDCheckbox

from device_connection_dialog import DeviceConnectionDialog, DialogContent
from troubleshooting import func_name
from bluetooth_helpers import Command


class Drawer(MDRelativeLayout):
    # control_panel should point to the instance's "control panel" in .kv rule.
    control_panel = ObjectProperty()

    def open_drawer(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.height = self.control_panel.height + dp(20)
        self.control_panel.x = dp(0)

    def close_drawer(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.height = dp(20)
        self.control_panel.x = Window.width

    def toggle_drawer(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        if self.height == dp(20):
            self.open_drawer()
        else:
            self.close_drawer()


class RGBDrawer(Drawer):
    device_controller = ObjectProperty()
    red_slider = ObjectProperty()
    green_slider = ObjectProperty()
    blue_slider = ObjectProperty()
    presets = ObjectProperty()


class Presets(MDBoxLayout):
    pass


class ColorPresets(MDGridLayout):
    device_controller = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_device_controller(self, *args):
        num_buttons = 20
        hue_step = 255 / num_buttons
        for i in range(0, num_buttons):
            hue = i * hue_step
            hsv = [hue / 255, 1, 1]
            rgb = colorsys.hsv_to_rgb(*hsv)
            color_preset_btn = ColorPresetButton(
                md_bg_color=rgb,
            )
            color_preset_btn.bind(on_release=partial(self.device_controller.update_rgb_sliders,
                                                     color_preset_btn.md_bg_color))
            self.add_widget(color_preset_btn)


class WhitePresets(MDGridLayout):
    device_controller = ObjectProperty()

    def on_device_controller(self, *args):
        for i in range(4):
            rgb = (1, 1, (255 - i * 30) / 255)
            color_preset_btn = ColorPresetButton(
                md_bg_color=rgb,
            )
            color_preset_btn.bind(on_release=partial(self.device_controller.update_rgb_sliders,
                                                     color_preset_btn.md_bg_color))
            self.add_widget(color_preset_btn)


class ColorPresetButton(MDRoundFlatButton):
    pass


class WaveDrawer(Drawer):
    device_controller = ObjectProperty()
    frequency = NumericProperty(10)
    range_min = NumericProperty(0)
    range_max = NumericProperty(255)
    speed = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._animation = None
        self._phase_offset = 0
        self._active_wave_option = 'hue'
        self._active_strip_option = 'strip'
        self.wave_debounce = False
        self.strip_debounce = False

    def close_drawer(self, *args):
        super().close_drawer()
        self.ids.graph_.canvas.before.clear()

    def open_drawer(self, *args):
        super().open_drawer()
        Clock.schedule_once(self.draw_wave)

    def on_kv_post(self, *args):
        mac_address = self.device_controller.device.getAddress()
        for box in self.ids.wave_options_.children:
            for child in box.children:
                if isinstance(child, WaveOptionRadioButton):
                    child.group = mac_address + '1'
        for box in self.ids.strip_options_.children:
            for child in box.children:
                if isinstance(child, WaveOptionRadioButton):
                    child.group = mac_address + '2'
        self.ids.animate_button_.group = mac_address + '3'

    def on_frequency(self, *args):
        self.draw_wave()

    def on_range_min(self, *args):
        self.draw_wave()

    def on_range_max(self, *args):
        self.draw_wave()

    def on_speed(self, *args):
        if self._animation:
            self.draw_wave()

    def draw_wave(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.ids.graph_.canvas.before.clear()
        points = []
        wave_height = self.ids.graph_.height - dp(30)  # Adds vertical 'padding' for labels
        amplitude = abs(self.range_max - self.range_min)
        normalized_amplitude = (amplitude / 255) * (wave_height / 2)
        x0, y0 = self.ids.graph_.pos
        xi = trunc(self.ids.graph_.width)
        range_midpoint = (self.range_max + self.range_min) / 2
        ym = y0 + (range_midpoint / 255) * wave_height + dp(15)
        self.ids.x_axis_lbl_.center_y = ym - self.ids.wave_options_.height - dp(20)
        self.ids.x_axis_lbl_.text = str(range_midpoint) + ' '
        _frame_offset = 0.5 * pi * (self.speed/100)  # when new frame value == pi it just flip flops
        self._phase_offset = (self._phase_offset + _frame_offset) % (2 * pi)
        for x in range(xi):
            points.append(x0 + x)
            points.append(sin(self.frequency * (x / xi) + self._phase_offset) * normalized_amplitude + ym)
        with self.ids.graph_.canvas.before:
            # Sin Wave
            Color(1, 0, 0, 1)
            Line(points=points)
            # Background
            Color(1, 1, 1, 0.1)
            Rectangle(pos=self.ids.graph_.pos, size=self.ids.graph_.size)
            # X-Axis
            Color(0, 0, 0, 1)
            Line(points=(x0, ym, xi + x0, ym))

    def on_wave_option_active(self, radio_button):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` \t '
                      f'{radio_button.state, radio_button.active, radio_button.value}')
        if self.wave_debounce:
            self.wave_debounce = False
            return
        if radio_button.value == self._active_wave_option:
            radio_button.active = True
            self.wave_debounce = True
        else:
            self._active_wave_option = radio_button.value

    def on_strip_option_active(self, radio_button):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` \t '
                      f'{radio_button.state, radio_button.active, radio_button.value}')
        if self.strip_debounce:
            self.strip_debounce = False
            return
        if radio_button.value == self._active_strip_option:
            radio_button.active = True
            self.strip_debounce = True
        else:
            self._active_strip_option = radio_button.value

    def on_animation_active(self, radio_button):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` \t '
                      f'{radio_button.state, radio_button.active, radio_button.value}')
        if radio_button.active:
            self._animation = Clock.schedule_interval(self.draw_wave, 0.05)
        else:
            self._animation.cancel()
            self._animation = None


class WaveOptionRadioButton(MDCheckbox):
    pass


class PaletteDrawer(Drawer):
    device_controller = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def close_drawer(self, *args):
        super().close_drawer()
        self.control_panel.unbind(height=self._update_height)

    def open_drawer(self, *args):
        super().open_drawer()
        self.control_panel.bind(height=self._update_height)

    def _update_height(self, *args):
        # PaletteDrawer contains the AnimationsList, which can also grow in height when its
        # AnimationExpansionPanels have been expanded.  In that case, PaletteDrawer should also
        # grow in height to visually contain the AnimationsList.  Previously this was done in .kv
        # (height: palette_cp_.height + dp(20)) but requires closing the drawer on start-up.
        self.height = self.control_panel.height + dp(20)
