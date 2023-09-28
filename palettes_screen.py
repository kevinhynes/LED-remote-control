import logging
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.properties import NumericProperty, ListProperty, ObjectProperty, BooleanProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.uix.screenmanager import SlideTransition

from kivy.graphics import Color
from kivy_gradient import Gradient

from kivy.graphics import RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.metrics import dp

from bluetooth_helpers import Command
import palettes
from troubleshooting import func_name


########## Palettes Screen ##########
class PaletteWidgetControls(MDGridLayout):
    pass

class GradientWidget(MDFlatButton):
    mirrored = BooleanProperty(True)

    def __init__(self, colors, **kwargs):
        super().__init__(**kwargs)
        # Right now only works for hex values in string form
        self.colors = [str(color) for color in colors]
        self.mirrored_colors = self.colors + self.colors[::-1]
        self.gradient = RoundedRectangle()
        gradient_texture = Gradient.horizontal(*[get_color_from_hex(color) for color in colors])
        with self.canvas:
            Color(1, 1, 1)  # Set color to white, not sure why this is necessary.
            self.gradient = RoundedRectangle(size=self.size, pos=self.pos,
                                             radius=(dp(15), dp(15)), texture=gradient_texture)
            self.bind(pos=self.update_gradient, size=self.update_gradient)

    def update_gradient(self, *args):
        self.gradient.pos = self.pos
        self.gradient.size = self.size

    def on_mirrored(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.canvas.clear()
        if self.mirrored:
            gradient_texture = Gradient.horizontal(
                *[get_color_from_hex(color) for color in self.mirrored_colors])
            with self.canvas:
                Color(1, 1, 1)  # Set color to white, not sure why this is necessary.
                self.gradient = RoundedRectangle(size=self.size, pos=self.pos,
                                                 radius=(dp(15), dp(15)), texture=gradient_texture)
                self.bind(pos=self.update_gradient, size=self.update_gradient)
        else:
            gradient_texture = Gradient.horizontal(
                *[get_color_from_hex(color) for color in self.colors])
            with self.canvas:
                Color(1, 1, 1)  # Set color to white, not sure why this is necessary.
                self.gradient = RoundedRectangle(size=self.size, pos=self.pos,
                                                 radius=(dp(15), dp(15)), texture=gradient_texture)
                self.bind(pos=self.update_gradient, size=self.update_gradient)

    def change_mirror(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`called with {args}')
        self.mirrored = not self.mirrored


class PaletteWidget(MDCard):

    def __init__(self, device_controller, hex_colors, **kwargs):
        super().__init__(**kwargs)
        self.device_controller = device_controller
        self.hex_colors = hex_colors
        self.gradient_widget = GradientWidget(hex_colors)
        self.gradient_widget.bind(on_press=self.send_palette)
        self.controls = PaletteWidgetControls()
        self.add_widget(self.gradient_widget)
        self.add_widget(self.controls)

    def send_palette(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        command = Command(mode=3, hex_colors=self.hex_colors)
        self.device_controller.send_command(command)


class PalettesScreen(MDScreen):
    grid = ObjectProperty()
    device_controller = ObjectProperty()

    def __init__(self, **kwargs):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        super().__init__(**kwargs)
        # Reduce palettes to their hex values.
        self.palettes = []
        for named_palette in palettes.palettes:
            for palette_name in named_palette.keys():
                self.palettes.append(named_palette[palette_name].values())

    def on_pre_enter(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        app = MDApp.get_running_app()
        app.root_screen.ids._top_app_bar.left_action_items = [['arrow-left-bold', self.go_back]]
        for palette_widget in self.ids.grid_.children:
            palette_widget.device_controller = self.device_controller

    def on_kv_post(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        for palette in self.palettes:
            self.ids.grid_.add_widget(PaletteWidget(
                device_controller=self.device_controller,
                hex_colors=palette))

    def go_back(self, *args):
        app = MDApp.get_running_app()
        slide_right = SlideTransition(direction='right')
        app.root_screen.screen_manager.transition = slide_right
        app.root_screen.screen_manager.current = 'controllers'
        open_nav_menu = lambda x: app.root_screen.ids._nav_drawer.set_state('open')
        app.root_screen.ids._top_app_bar.left_action_items = [['menu', open_nav_menu]]
