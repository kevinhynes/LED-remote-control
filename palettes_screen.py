import logging
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.screen import MDScreen
from kivy.properties import NumericProperty, ListProperty, ObjectProperty, BooleanProperty
from kivymd.uix.button import MDFlatButton
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.widget import MDWidget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.uix.screenmanager import SlideTransition


from kivy_gradient import Gradient

from bluetooth_helpers import Command
import palettes
from troubleshooting import func_name


class PaletteControls(MDGridLayout):
    palette_widget = ObjectProperty()
    mirror_btn = ObjectProperty()
    blend_btn = ObjectProperty()
    select_btn = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mirror_btns = ('crop-square', 'data/flip.png', 'data/fliprev.png')
        self.mirror_idx = 1
        self.blend_btns = ( 'blur-linear', 'dots-grid',)
        self.blend_idx = 0
        self.select_btns = ('checkbox-blank-outline', 'checkbox-marked-outline')
        self.select_idx = 0

    def update_mirroring(self, *args):
        self.palette_widget.update_mirror_idx(self.mirror_idx)
        self.mirror_idx = (self.mirror_idx + 1) % 3
        self.mirror_btn.icon = self.mirror_btns[self.mirror_idx]

    def update_blended(self, *args):
        self.blend_idx = (self.blend_idx + 1) % 2
        self.palette_widget.update_is_blended(self.blend_idx)
        self.blend_btn.icon = self.blend_btns[self.blend_idx]

    def update_selected(self, *args):
        self.palette_widget.update_is_selected(self.select_idx)
        self.select_idx = (self.select_idx + 1) % 2
        self.select_btn.icon = self.select_btns[self.select_idx]


class PaletteWidget(MDBoxLayout):

    def __init__(self, colors, **kwargs):
        # Right now only works for hex values in string form
        self.mirror_idx = 0
        self.is_blended = 0
        self.is_selected = 0
        self.colors = [str(color) for color in colors]
        self.display_colors = [str(color) for color in colors]
        self.shadow = RoundedRectangle()
        self.gradient = RoundedRectangle()
        super().__init__(**kwargs)
        self.bind(pos=self.update_palette, size=self.update_palette)
        # self.bind(pos=self.update_gradient, size=self.update_gradient)
        # Clock.schedule_once(self.update_palette, 2)

    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y):
            logging.debug(f'\tPaletteWidget')
            self.parent.send_palette()

    def update_mirror_idx(self, mirror_idx, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.mirror_idx = mirror_idx
        self.update_palette()

    def update_is_blended(self, is_blended, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.is_blended = is_blended
        self.update_palette()

    def update_is_selected(self, is_selected, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.is_selected = is_selected

    def update_palette(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.canvas.before.clear()
        self.canvas.clear()
        self.children[:] = []
        colors = []
        if self.mirror_idx == 0:
            colors[:] = self.colors
        elif self.mirror_idx == 1:
            colors[:] = self.colors + self.colors[::-1]
        else:
            colors[:] = self.colors[::-1] + self.colors
        self.display_colors[:] = colors
        if self.is_blended:
            self.update_gradient()
        else:
            for i, clr in enumerate(self.display_colors):
                self.add_widget(MDWidget(md_bg_color=clr))
        self.update_shadow()

    def update_gradient(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.canvas.clear()
        gradient_texture = Gradient.horizontal(
            *[get_color_from_hex(color) for color in self.display_colors])
        with self.canvas:
            Color(1, 1, 1)  # Set color to white, not sure why this is necessary.
            self.gradient = RoundedRectangle(size=self.size, pos=self.pos,
                                             radius=(dp(15), dp(15)), texture=gradient_texture)
        self.gradient.pos = self.pos
        self.gradient.size = self.size

    def update_shadow(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
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

    def __init__(self, device_controller, hex_colors, **kwargs):
        super().__init__(**kwargs)
        self.device_controller = device_controller
        self.hex_colors = hex_colors
        self.palette_widget = PaletteWidget(hex_colors)
        self.controls = PaletteControls(palette_widget=self.palette_widget)
        # self.palette_widget.bind(on_touch_up=self.send_palette)
        self.add_widget(self.palette_widget)
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
        app.root_screen.ids.top_app_bar_.left_action_items = [['arrow-left-bold', self.go_back]]
        for palette_widget in self.ids.grid_.children:
            palette_widget.device_controller = self.device_controller

    def on_kv_post(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        for palette in self.palettes:
            self.ids.grid_.add_widget(PaletteController(
                device_controller=self.device_controller,
                hex_colors=palette))

    def go_back(self, *args):
        app = MDApp.get_running_app()
        slide_right = SlideTransition(direction='right')
        app.root_screen.screen_manager.transition = slide_right
        app.root_screen.screen_manager.current = 'controllers'
        open_nav_menu = lambda x: app.root_screen.ids.nav_drawer_.set_state('open')
        app.root_screen.ids.top_app_bar_.left_action_items = [['menu', open_nav_menu]]
