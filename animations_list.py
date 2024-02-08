import logging
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.properties import NumericProperty, ObjectProperty, StringProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList
from kivymd.uix.card import MDCard
from kivy.uix.screenmanager import SlideTransition

from kivy.metrics import dp

from bluetooth_helpers import Command
from troubleshooting import func_name


class Animation:

    def __init__(self, name='', icon_filepath='', animation_id=-1, variables=(), control_panel=None,
                 **kwargs):
        self.name = name
        self.icon_filepath = icon_filepath
        self.animation_id = animation_id
        self.variables = variables
        self.control_panel = control_panel


class AnimationsList(MDList):
    """
    AnimationsList class stores all AnimationDrawers and provides interlocking functionality.
    """
    device_controller = ObjectProperty()

    def __init__(self, **kwargs):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        super().__init__(**kwargs)

    def close_all_drawers(self):
        for animation_drawer in self.children:
            animation_drawer.close_drawer()


class AnimationDrawer(MDRelativeLayout):
    """
    AnimationDrawer class with drop-down and interlocked functionality.

    AnimationDrawer holds a ControlPanel for a specific LED animation. Only one LED animation can be
    active at a time, so only one ControlPanel should be shown at a time.  AnimationDrawers are
    interlocked so that only one can be opened at a time; any AnimationDrawer's opening will trigger
    AnimationDrawer's parent - AnimationList - to close all drawers.
    """
    device_controller = ObjectProperty()
    anm_list = ObjectProperty()
    control_panel = ObjectProperty()
    header_panel = ObjectProperty()
    is_open = BooleanProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_open = False

    def toggle_interlocked_drawer(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        if self.is_open:
            self.close_drawer()
        else:
            self.open_interlocked_drawer()

    def open_interlocked_drawer(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.anm_list.close_all_drawers()
        self.height = self.control_panel.height + self.header_panel.height
        self.control_panel.x = dp(0)
        self.header_panel.ids.toggle_drawer_btn_.icon = 'chevron-up'
        self.is_open = True
        self.control_panel.send_palette_animation()

    def close_drawer(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        self.height = self.header_panel.height
        self.control_panel.x = Window.width
        self.header_panel.ids.toggle_drawer_btn_.icon = 'chevron-down'
        self.is_open = False


class HeaderPanel(MDCard):
    """
    HeaderPanel class acts as "top layer" of AnimationDrawer.
    """
    name = StringProperty()
    icon_filepath = StringProperty()


class BreatheDrawer(AnimationDrawer):
    pass


class BreezeDrawer(AnimationDrawer):
    pass


class SplatterDrawer(AnimationDrawer):
    pass


class TwinkleDrawer(AnimationDrawer):
    pass


class CometDrawer(AnimationDrawer):
    pass


class ControlPanel(MDBoxLayout):
    """
    ControlPanel class holds PaletteWidget and a set of widgets specific to an LED palette
    animation.  Widgets in the ControlPanel use its attached DeviceController to update variable
    values running on the microcontroller.
    """
    device_controller = ObjectProperty()
    animation_id = NumericProperty()

    def __init__(self, **kwargs):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        super().__init__(**kwargs)

    def on_kv_post(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
        self.ids.animation_speed_slider_.bind(value=self.send_animation)

    def update_animation_speed(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')

    def open_palettes_screen(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')
        app = MDApp.get_running_app()
        palettes_screen = app.root_screen.screen_manager.get_screen('palettes')
        palettes_screen.device_controller = self.device_controller
        palettes_screen.client_animation_control_panel = self
        slide_left = SlideTransition(direction='left')
        app.root_screen.screen_manager.transition = slide_left
        app.root_screen.screen_manager.current = 'palettes'

    def update_palette_widget(self, pw, *args):
        self.ids.palette_container_.clear_widgets()
        self.ids.palette_container_.add_widget(pw)

    def send_palette_animation(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.send_palette()
        self.send_animation()

    def send_palette(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        palette_widget = self.ids.palette_container_.children[0]
        hex_colors = palette_widget.hex_colors[::-1] \
            if palette_widget.is_swapped else palette_widget.hex_colors
        command = Command(mode=3,
                          hex_colors=hex_colors,
                          is_mirrored=palette_widget.is_mirrored,
                          is_blended=palette_widget.is_blended)
        self.device_controller.send_command(command)

    def send_animation(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        speed = 100 - self.ids.animation_speed_slider_.value
        command = Command(mode=4, animation_id=self.animation_id, animation_speed=speed)
        self.device_controller.send_command(command)


class BreatheControls(ControlPanel):
    pass

    # def on_kv_post(self, *args):
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
    #     self.ids.animation_speed_slider_.bind(value=self.send_animation)

    # def send_animation(self, *args):
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
    #     speed = 100 - self.ids.animation_speed_slider_.value
    #     command = Command(mode=4, animation_id=1, animation_speed=speed)
    #     self.device_controller.send_command(command)
    #     logging.debug(f'\tBreathe animation sent...')
    #     logging.debug(f'\t\t speed: {speed}')


class BreezeControls(ControlPanel):
    pass

    # def on_kv_post(self, *args):
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
    #     self.ids.animation_speed_slider_.bind(value=self.send_animation)

    # def send_animation(self, *args):
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
    #     speed = 100 - self.ids.animation_speed_slider_.value
    #     command = Command(mode=4, animation_id=2, animation_speed=speed)
    #     self.device_controller.send_command(command)
    #     logging.debug(f'\tBreeze animation sent...')
    #     logging.debug(f'\t\t speed: {speed}')


class SplatterControls(ControlPanel):
    pass

    # def on_kv_post(self, *args):
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
    #     self.ids.animation_speed_slider_.bind(value=self.send_animation)

    # def send_animation(self, *args):
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
    #     speed = 100 - self.ids.animation_speed_slider_.value
    #     command = Command(mode=4, animation_id=3, animation_speed=speed)
    #     self.device_controller.send_command(command)
    #     logging.debug(f'\tSplatter animation sent...')
    #     logging.debug(f'\t\t speed: {speed}')


class TwinkleControls(ControlPanel):
    pass

    # def send_animation(self, *args):
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')


class CometControls(ControlPanel):
    pass

    # def on_kv_post(self, *args):
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
    #     self.ids.animation_speed_slider_.bind(value=self.send_animation)
    #     self.ids.trail_length_.bind(value=self.send_animation)
    #     self.ids.num_comets_.bind(value=self.send_animation)
    #
    # def send_animation(self, *args):
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
    #     speed = self.ids.animation_speed_slider_.value
    #     trail_length = self.ids.trail_length_.value
    #     num_comets = self.ids.num_comets_.value
    #     command = Command(mode=4, animation_id=9, animation_speed=speed, trail_length=trail_length,
    #                       num_comets=num_comets)
    #     self.device_controller.send_command(command)
    #     logging.debug(f'\tComet animation sent...')
    #     logging.debug(f'\t\t speed: {speed} trail length: {trail_length} num_comets: {num_comets}')
