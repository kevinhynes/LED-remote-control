import logging
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivymd.uix.screen import MDScreen
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty
from kivymd.uix.widget import MDWidget
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList
from kivy.uix.screenmanager import SlideTransition

from kivy_gradient import Gradient

from troubleshooting import func_name
import palettes
from bluetooth_helpers import Command


class PaletteControls(MDRelativeLayout):
    palette_widget = ObjectProperty()
    palette_controller = ObjectProperty()

    def toggle_blend(self, *args):
        self.palette_widget.is_blended = not self.palette_widget.is_blended

    def toggle_swap(self, *args):
        self.palette_widget.is_swapped = not self.palette_widget.is_swapped

    def toggle_mirror(self, *args):
        self.palette_widget.is_mirrored = not self.palette_widget.is_mirrored

    def toggle_select(self, *args):
        self.palette_widget.is_selected = not self.palette_widget.is_selected

    def send_palette(self, *args):
        self.palette_controller.save_to_animation()
        self.palette_controller.send_palette()

    def save_to_animation(self, *args):
        self.palette_controller.save_to_animation()


class PaletteWidget(MDBoxLayout):
    is_mirrored = BooleanProperty(False)
    is_swapped = BooleanProperty(False)
    is_blended = BooleanProperty(False)

    def __init__(self, hex_colors=None, **kwargs):
        # PaletteWidget's BooleanProperties will be updated by buttons in PaletteControls
        super().__init__(**kwargs)
        # Right now only works for hex values in string form
        if not hex_colors:
            # Default widget for when Animation's ControlPanel is first instantiated.
            hex_colors = list(palettes.palettes[0].values())[0].values()
            # Also need to change size_hint_x like for clone.
            Clock.schedule_once(self.initialize_default_widget)
        self.hex_colors = [str(hex_color) for hex_color in hex_colors]
        self.display_colors = [str(hex_color) for hex_color in hex_colors]
        self.shadow = RoundedRectangle()
        self.gradient = RoundedRectangle()
        self.bind(pos=self.update_palette,
                  size=self.update_palette,
                  is_mirrored=self.update_palette,
                  is_swapped=self.update_palette,
                  is_blended=self.update_palette)
        self.ripple_graphics = None

    def initialize_default_widget(self, *args):
        self.size_hint_x = 1

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            # self.do_ripple(touch)
            pass

    # Now that PaletteWidget is used in AnimationExpansionPanel this breaks.
    # def on_touch_up(self, touch):
    #     if self.collide_point(touch.x, touch.y):
    #         self.parent.send_palette()

    # def do_ripple(self, touch=None):
    #     # Adding my own ripple because Kivy is dumb!!!
    #     if self.ripple_graphics is None:
    #         with self.canvas.after:
    #             Color(1, 1, 1, 0.25)
    #             self.ripple_graphics = RoundedRectangle(pos=(touch.x, touch.y), size=(1, 1))
    #         Clock.schedule_once(self.do_ripple)
    #     elif self.ripple_graphics.size[0] < self.width:
    #         self.canvas.after.clear()
    #         with self.canvas.after:
    #             Color(1, 1, 1, 0.25)
    #             x_step = dp(25)
    #             y_step = dp(10)
    #             x, y = self.ripple_graphics.pos
    #             nx = max(self.x, x - x_step)
    #             ny = max(self.y, y - y_step)
    #             w, h = self.ripple_graphics.size[0], self.ripple_graphics.size[1]
    #             nw = min(2 * x_step + w, self.right - nx)
    #             nh = min(2 * y_step + h, self.top - ny)
    #             self.ripple_graphics = RoundedRectangle(pos=(nx, ny), size=(nw, nh))
    #         Clock.schedule_once(self.do_ripple)
    #     else:
    #         self.canvas.after.clear()
    #         self.ripple_graphics = None

    def update_palette(self, *args):
        # logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.update_shadow()
        self.children[:] = []
        hex_colors = []
        if self.is_swapped:
            hex_colors[:] = self.hex_colors[::-1]
        else:
            hex_colors[:] = self.hex_colors[:]
        if self.is_mirrored:
            hex_colors[:] = hex_colors[:] + hex_colors[::-1]
        self.display_colors[:] = hex_colors
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

    def create_clone(self):
        clone = PaletteWidget(hex_colors=self.hex_colors, is_mirrored=self.is_mirrored,
                              is_blended=self.is_blended, is_swapped=self.is_swapped)
        # Cloned PaletteWidgets go into an AnimationExpansionPanel.ControlPanelTray.ControlPanel -
        # adjusting look to fit its place in the GUI
        clone.size_hint_x = 1
        return clone


class PaletteController(MDCard):

    def __init__(self, hex_colors, **kwargs):
        super().__init__(**kwargs)
        self.hex_colors = list(hex_colors)  # was dict values object
        self.palette_widget = PaletteWidget(hex_colors)
        self.controls = PaletteControls(palette_controller=self, palette_widget=self.palette_widget)
        self.add_widget(self.palette_widget)
        self.add_widget(self.controls)

    def send_palette(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        hex_colors = self.hex_colors[::-1] if self.palette_widget.is_swapped else self.hex_colors
        command = Command(mode=3,
                          hex_colors=hex_colors,
                          is_mirrored=self.palette_widget.is_mirrored,
                          is_blended=self.palette_widget.is_blended)
        palettes_screen = MDApp.get_running_app().root_screen.screen_manager.get_screen('palettes')
        palettes_screen.device_controller.send_command(command)

    def save_to_animation(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        palettes_screen = MDApp.get_running_app().root_screen.screen_manager.get_screen('palettes')
        pw_clone = self.palette_widget.create_clone()
        palettes_screen.client_animation_control_panel.update_palette_widget(pw_clone)


class PalettesList(MDList):

    def __init__(self, **kwargs):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        super().__init__(**kwargs)
        # Reduce palettes to their hex values.
        self.palettes = []
        for named_palette in palettes.palettes:
            for palette_name in named_palette.keys():
                self.palettes.append(named_palette[palette_name].values())
        for palette in self.palettes:
            self.add_widget(PaletteController(hex_colors=palette))


class PalettesScreen(MDScreen):
    device_controller = ObjectProperty()
    client_animation_control_panel = ObjectProperty()

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
