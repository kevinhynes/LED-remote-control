import logging
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
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


class ControlPanel(MDBoxLayout):
    device_controller = ObjectProperty()
    palette_widget = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')

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
        widgets_to_remove = self.ids.palette_container_.children
        for child in widgets_to_remove:
            self.ids.palette_container_.remove_widget(child)
        self.ids.palette_container_.add_widget(pw)

    def update_animation_speed(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args: {args}')


class BreatheControls(ControlPanel):

    def on_kv_post(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
        self.ids.animation_speed_slider_.bind(value=self.send_animation)

    def send_animation(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
        speed = 100 - self.ids.animation_speed_slider_.value
        command = Command(mode=4, animation_id=1, animation_speed=speed)
        self.device_controller.send_command(command)
        logging.debug(f'\tBreathe animation sent...')
        logging.debug(f'\t\t speed: {speed}')


class BreezeControls(ControlPanel):

    def on_kv_post(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
        self.ids.animation_speed_slider_.bind(value=self.send_animation)

    def send_animation(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
        speed = 100 - self.ids.animation_speed_slider_.value
        command = Command(mode=4, animation_id=2, animation_speed=speed)
        self.device_controller.send_command(command)
        logging.debug(f'\tBreeze animation sent...')
        logging.debug(f'\t\t speed: {speed}')


class SplatterControls(ControlPanel):

    def on_kv_post(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
        self.ids.animation_speed_slider_.bind(value=self.send_animation)

    def send_animation(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
        speed = 100 - self.ids.animation_speed_slider_.value
        command = Command(mode=4, animation_id=3, animation_speed=speed)
        self.device_controller.send_command(command)
        logging.debug(f'\tSplatter animation sent...')
        logging.debug(f'\t\t speed: {speed}')


class CometControls(ControlPanel):

    def on_kv_post(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
        self.ids.animation_speed_slider_.bind(value=self.send_animation)
        self.ids.trail_length_.bind(value=self.send_animation)
        self.ids.num_comets_.bind(value=self.send_animation)

    def send_animation(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
        speed = self.ids.animation_speed_slider_.value
        trail_length = self.ids.trail_length_.value
        num_comets = self.ids.num_comets_.value
        command = Command(mode=4, animation_id=9, animation_speed=speed, trail_length=trail_length,
                          num_comets=num_comets)
        self.device_controller.send_command(command)
        logging.debug(f'\tComet animation sent...')
        logging.debug(f'\t\t speed: {speed} trail length: {trail_length} num_comets: {num_comets}')


class TwinkleControls(ControlPanel):
    pass


class TopPanel(MDCard):
    panel = ObjectProperty()


class ControlPanelTray(MDRelativeLayout):

    def __init__(self, **kwargs):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        super().__init__(**kwargs)
        self.expanded_height = 0
        self.control_panel = None

    def add_control_panel(self, control_panel):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.expanded_height = control_panel.height
        self.control_panel = control_panel
        self.add_widget(self.control_panel)
        self.unmount_control_panel()

    def unmount_control_panel(self):
        self.control_panel.x = Window.width

    def mount_control_panel(self):
        self.control_panel.x = self.x
        # Send animation when the AnimationExpansionPanel is expanded
        self.control_panel.send_animation()


class AnimationExpansionPanel(MDCard):
    top_panel = ObjectProperty()
    control_panel_tray = ObjectProperty()
    test_name = StringProperty()
    test_icon_filepath = StringProperty()
    test_control_panel = ObjectProperty()

    def __init__(self, name, icon_filepath, control_panel, **kwargs):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.is_expanded = False
        self.expanded_height = dp(50) + control_panel.height
        self.name = name
        self.icon_filepath = icon_filepath
        self.control_panel = control_panel
        super().__init__(**kwargs)
        self.top_panel.name_lbl.text = self.name
        self.top_panel.anim_icon.icon = self.icon_filepath
        self.control_panel_tray.add_control_panel(self.control_panel)

    def on_size(self, *args):
        # Because of ControlPanel's adaptive_height: True, seems control_panel.height is not figured
        # out until later so expanded_height is wrong upon instantiation.
        self.expanded_height = dp(50) + self.control_panel.height

    # def on_kv_post(self, *args):
    #     self.top_panel.anim_icon.icon = self.icon_filepath
    #     self.top_panel.name_lbl.text = self.name
    #     self.control_panel_tray.add_control_panel(self.control_panel)
    #
    def expand(self, *args):
        self.parent.contract_all()
        self.height = self.expanded_height
        self.control_panel_tray.mount_control_panel()
        self.top_panel.ids.toggle_expansion_btn_.icon = 'chevron-up'
        self.is_expanded = True

    def contract(self, *args):
        self.height = dp(50)
        self.control_panel_tray.unmount_control_panel()
        self.top_panel.ids.toggle_expansion_btn_.icon = 'chevron-down'
        self.is_expanded = False

    # def on_top_panel(self, *args):
    #     self.top_panel.name_lbl.txt = self.test_name


class AnimationsList(MDList):
    device_controller = ObjectProperty()

    def __init__(self, **kwargs):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        super().__init__(**kwargs)
        animation_attrs = [
            ('Breathe', 'data/wind3.png', 1, [], BreatheControls()),
            ('Breeze', 'data/breeze.png', 2, [], BreezeControls()),
            ('Splatter', 'data/paint.png', 3, [], SplatterControls()),
            ('Twinkle', 'data/star.png', 4, [], TwinkleControls()),
            ('Comet', 'data/comet.png', 5, [], CometControls()),
        ]
        animations = []
        for attrs in animation_attrs:
            animations.append(Animation(name=attrs[0],
                                        icon_filepath=attrs[1],
                                        animation_id=attrs[2],
                                        variables=attrs[3],
                                        control_panel=attrs[4]))
        self.animations = animations
        for i, anim in enumerate(self.animations):
            panel = AnimationExpansionPanel(name=anim.name,
                                            icon_filepath=anim.icon_filepath,
                                            control_panel=anim.control_panel)
            # self.add_widget(panel)

    # def on_kv_post(self, *args):
    #     logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
    #     for i, anim in enumerate(self.animations):
    #         panel = AnimationExpansionPanel(name=anim.name,
    #                                         icon_filepath=anim.icon_filepath,
    #                                         control_panel=anim.control_panel)
    #         self.add_widget(panel)

    # def on_device_controller(self, *args):
    #     self.activate_control_panels(self.device_controller)

    def activate_control_panels(self, device_controller, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` called with args {args}')
        for control_panel in [animation.control_panel for animation in self.animations]:
            control_panel.device_controller = device_controller

    def contract_all(self, *args):
        for panel in self.children:
            if panel.is_expanded:
                panel.contract()


# class AnimationsScreen(MDScreen):
#     device_controller = ObjectProperty()
#
#     def on_pre_enter(self, *args):
#         logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
#         app = MDApp.get_running_app()
#         app.root_screen.ids.top_app_bar_.left_action_items = [['arrow-left-bold', self.go_back]]
#
#     def go_back(self, *args):
#         app = MDApp.get_running_app()
#         slide_right = SlideTransition(direction='right')
#         app.root_screen.screen_manager.transition = slide_right
#         app.root_screen.screen_manager.current = 'controllers'
#         open_nav_menu = lambda x: app.root_screen.ids.nav_drawer_.set_state('open')
#         app.root_screen.ids.top_app_bar_.left_action_items = [['menu', open_nav_menu]]
#
#     def on_device_controller(self, *args):
#         # DeviceController given to screen when the open_animation_screen button is clicked,
#         # ControlPanel needs access. Because this is many widget-tree levels deep, it makes sense
#         # to do it this way (I think).
#         self.ids.anm_list_.activate_control_panels(self.device_controller)