import logging
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import CircularRippleBehavior, RectangularRippleBehavior
from kivy.uix.stencilview import StencilView
from kivymd.uix.screen import MDScreen
from kivy.properties import NumericProperty, ListProperty, ObjectProperty, BooleanProperty
from kivymd.uix.widget import MDWidget
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.uix.screenmanager import SlideTransition

from kivy_gradient import Gradient

from bluetooth_helpers import Command
import palettes
from troubleshooting import func_name


class PaletteControls(MDGridLayout):
    palette_widget = ObjectProperty()

    def toggle_blend(self, *args):
        self.palette_widget.is_blended = not self.palette_widget.is_blended

    def toggle_swap(self, *args):
        self.palette_widget.is_swapped = not self.palette_widget.is_swapped

    def toggle_mirror(self, *args):
        self.palette_widget.is_mirrored = not self.palette_widget.is_mirrored

    def toggle_select(self, *args):
        self.palette_widget.is_selected = not self.palette_widget.is_selected


class PaletteWidget(MDBoxLayout):
    is_mirrored = BooleanProperty(False)
    is_swapped = BooleanProperty(False)
    is_blended = BooleanProperty(False)
    is_selected = BooleanProperty(False)

    def __init__(self, colors, **kwargs):
        # PaletteWidget's BooleanProperties will be updated by buttons in PaletteControls
        super().__init__(**kwargs)
        # Right now only works for hex values in string form
        self.colors = [str(color) for color in colors]
        self.display_colors = [str(color) for color in colors]
        self.shadow = RoundedRectangle()
        self.gradient = RoundedRectangle()
        self.bind(pos=self.update_palette,
                  size=self.update_palette,
                  is_mirrored=self.update_palette,
                  is_swapped=self.update_palette,
                  is_blended=self.update_palette)
        self.ripple_graphics = None

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            # Adding my own ripple because Kivy is dumb!!!
            self.do_ripple(touch)

    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.parent.send_palette()

    def do_ripple(self, touch=None):
        if self.ripple_graphics is None:
            with self.canvas.after:
                Color(1, 1, 1, 0.25)
                self.ripple_graphics = RoundedRectangle(pos=(touch.x, touch.y), size=(1, 1))
            Clock.schedule_once(self.do_ripple)
        elif self.ripple_graphics.size[0] < self.width:
            self.canvas.after.clear()
            with self.canvas.after:
                Color(1, 1, 1, 0.25)
                x_step = dp(25)
                y_step = dp(10)
                x, y = self.ripple_graphics.pos
                nx = max(self.x, x - x_step)
                ny = max(self.y, y - y_step)
                w, h = self.ripple_graphics.size[0], self.ripple_graphics.size[1]
                nw = min(2 * x_step + w, self.right - nx)
                nh = min(2 * y_step + h, self.top - ny)
                self.ripple_graphics = RoundedRectangle(pos=(nx, ny), size=(nw, nh))
            Clock.schedule_once(self.do_ripple)
        else:
            self.canvas.after.clear()
            self.ripple_graphics = None

    def update_palette(self, *args):
        # logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.update_shadow()
        self.children[:] = []
        colors = []
        if self.is_swapped:
            colors[:] = self.colors[::-1]
        else:
            colors[:] = self.colors[:]
        if self.is_mirrored:
            colors[:] = colors[:] + colors[::-1]
        self.display_colors[:] = colors
        if self.is_blended:
            self.update_gradient()
        else:
            self.canvas.clear()
            for i, clr in enumerate(self.display_colors):
                self.add_widget(MDWidget(md_bg_color=clr))

    def update_gradient(self, *args):
        # logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.canvas.clear()
        gradient_texture = Gradient.horizontal(
            *[get_color_from_hex(color) for color in self.display_colors])
        with self.canvas.before:
            Color(1, 1, 1)  # Set color to white, not sure why this is necessary.
            self.gradient = RoundedRectangle(size=self.size, pos=self.pos,
                                             radius=(dp(15), dp(15)), texture=gradient_texture)

    def update_shadow(self, *args):
        # logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.canvas.before.clear()
        if self.is_blended:
            with self.canvas.before:
                Color(0, 0, 0, 0.2)
                self.shadow = RoundedRectangle(size=self.size, pos=(self.x + dp(4), self.y - dp(3)),
                                               radius=(dp(15), dp(15)))
        else:
            with self.canvas.before:
                Color(0, 0, 0, 0.2)
                self.shadow = RoundedRectangle(size=self.size, pos=(self.x + dp(4), self.y - dp(3)),
                                               radius=(dp(1), dp(1)))


class PaletteController(MDCard):

    def __init__(self, hex_colors, **kwargs):
        super().__init__(**kwargs)
        self.hex_colors = hex_colors
        self.palette_widget = PaletteWidget(hex_colors)
        self.controls = PaletteControls(palette_widget=self.palette_widget)
        self.add_widget(self.palette_widget)
        self.add_widget(self.controls)

    def send_palette(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        command = Command(mode=3, hex_colors=self.hex_colors)
        self.parent.device_controller.send_command(command)


class PalettesList(MDList):
    device_controller = ObjectProperty()

    def __init__(self, **kwargs):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        super().__init__(**kwargs)
        # Reduce palettes to their hex values.
        self.palettes = []
        for named_palette in palettes.palettes:
            for palette_name in named_palette.keys():
                self.palettes.append(named_palette[palette_name].values())

    def on_kv_post(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        for palette in self.palettes:
            self.add_widget(PaletteController(hex_colors=palette))

    def connect_device_controller(self, device_controller, *args):
        self.device_controller = device_controller


class PalettesScreen(MDScreen):
    grid = ObjectProperty()
    device_controller = ObjectProperty()

    def on_pre_enter(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        app = MDApp.get_running_app()
        app.root_screen.ids.top_app_bar_.left_action_items = [['arrow-left-bold', self.go_back]]

    def go_back(self, *args):
        app = MDApp.get_running_app()
        slide_right = SlideTransition(direction='right')
        app.root_screen.screen_manager.transition = slide_right
        app.root_screen.screen_manager.current = 'controllers'
        open_nav_menu = lambda x: app.root_screen.ids.nav_drawer_.set_state('open')
        app.root_screen.ids.top_app_bar_.left_action_items = [['menu', open_nav_menu]]

    def on_device_controller(self, *args):
        # DeviceController given to screen when the open_palettes_screen button is clicked,
        # PaletteController needs access.  Because PalettesList holds all PaletteControllers,
        # just have PaletteController use its parent attribute for access to DeviceController to
        # save memory (bush vs tree compared w/ animations_screen.py).
        self.ids.palettes_list_.connect_device_controller(self.device_controller)
