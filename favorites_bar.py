import logging
from kivy.properties import NumericProperty, ObjectProperty, DictProperty
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRoundFlatButton
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from troubleshooting import func_name
from kivy.graphics import Color, Ellipse
from kivy_gradient import Gradient
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from bluetooth_helpers import Command


class FavoritesBar(MDBoxLayout):
    device_controller = ObjectProperty()
    max_favorites = 7

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = MDDialog()

    def add_favorite(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` {args}')
        if len(self.ids.favorites_.children) == self.max_favorites:
            self.dialog = MDDialog(
                title="Too many favorites!",
                text="You can delete favorites by long pressing",
                buttons=[
                    MDFlatButton(
                        text="DISMISS",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=self.dismiss
                    ),
                ],
            )
            self.dialog.open()
        elif 1 not in self.device_controller.last_commands.keys() or \
                'last' not in self.device_controller.last_commands.keys():
            self.dialog = MDDialog(
                title="Can't add empty favorite!",
                text="Turn on the LEDs first ya dummy!",
                buttons=[
                    MDFlatButton(
                        text="DISMISS",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=self.dismiss
                    ),
                ],
            )
            self.dialog.open()
        elif self.device_controller.last_commands['last'] == 'palette':
            commands_dict = {1: self.device_controller.last_commands[1],
                             3: self.device_controller.last_commands[3],
                             4: self.device_controller.last_commands[4]}
            fav_idx = len(self.ids.favorites_.children)
            self.device_controller.save_device_favorite(fav_idx, commands_dict)

            fav_btn = FavoriteButton(favorites_bar=self,
                                     commands_dict=commands_dict)
            self.ids.favorites_.add_widget(fav_btn)
        elif self.device_controller.last_commands['last'] == 'rgb':
            commands_dict = {1: self.device_controller.last_commands[1],
                             2: self.device_controller.last_commands[2]}
            fav_idx = len(self.ids.favorites_.children)
            self.device_controller.save_device_favorite(fav_idx, commands_dict)

            fav_btn = FavoriteButton(favorites_bar=self,
                                     commands_dict=commands_dict)
            self.ids.favorites_.add_widget(fav_btn)
        else:
            logging.debug(f'Error adding FavoriteButton.')

    def load_favorites(self, favorites_dict):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        favorites = sorted(list(favorites_dict.items()))
        # Each button
        for (fav_idx, loaded_commands_dict) in favorites:
            # Take the saved JSON version of the commands, and turn them back into Command objects.
            logging.debug(f'fav_idx: {fav_idx}, loaded_command_dict: {loaded_commands_dict}')
            commands_dict = {}
            for mode, command_as_dict in loaded_commands_dict.items():
                commands_dict[int(mode)] = Command.load_from_dict(command_as_dict)
            logging.debug(f'commands_dict: {commands_dict.items()}')
            fav_btn = FavoriteButton(favorites_bar=self,
                                     commands_dict=commands_dict)
            self.ids.favorites_.add_widget(fav_btn)

    def delete_favorite(self, fav_btn):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.ids.favorites_.remove_widget(fav_btn)

    def dismiss(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` {args}')
        self.dialog.dismiss()


class AddFavoriteButton(MDIconButton):
    pass


class FavoriteButton(MDRoundFlatButton):
    favorites_bar = ObjectProperty()
    commands_dict = DictProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._long_press_event = Clock.schedule_once(lambda x: 0, 0)
        self.long_press_time = 0.5
        self.dialog = MDDialog()
        self.dialog_open = False
        self.gradient = Ellipse()
        self.shadow = Ellipse()
        self.bind(pos=self.update_shadow, size=self.update_shadow)
        self.bind(pos=self.update_gradient_or_color, size=self.update_gradient_or_color)

    def on_state(self, instance, state):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` state: {state}')
        if state == 'down':
            # Start timer for long press
            lpt = self.long_press_time
            self._long_press_event = Clock.schedule_once(self.long_press, lpt)
        if state == 'normal':
            if not self.dialog_open:
                # 1. Short press - send favorite information to microcontroller
                self._long_press_event.cancel()
                self.send_command()
            else:
                # 2. Long press - dialog has been opened
                pass

    def long_press(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.dialog = MDDialog(
            title="Delete favorite?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_press=self.dismiss
                ),
                MDFlatButton(
                    text="DELETE",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_press=self.delete
                ),
            ],
        )
        self.dialog.bind(on_dismiss=self.update_dialog_status)
        self.dialog_open = True
        self.dialog.open()

    def dismiss(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` {args}')
        self.dialog.dismiss()

    def delete(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` {args}')
        self.dialog.dismiss()
        self.favorites_bar.delete_favorite(self)

    def update_dialog_status(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` {args}')
        self.dialog_open = False

    def update_shadow(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0, 0, 0.2)
            self.shadow = Ellipse(size=self.size, pos=(self.x + dp(2), self.y - dp(2)))

    def update_gradient_or_color(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}`')
        self.canvas.clear()

        # FavoriteButton holds an RGB favorite.
        if 2 in self.commands_dict:
            logging.debug(f'\tFavoriteButton updating color as RGB')
            r = self.commands_dict[2].red / 255
            g = self.commands_dict[2].green / 255
            b = self.commands_dict[2].blue / 255
            with self.canvas:
                Color(r, g, b, 1)
                self.gradient = Ellipse(size=self.size, pos=self.pos)
                Color(0, 0, 0, 0.2)
                self.gradient = Ellipse(size=self.size, pos=self.pos)
                Color(r, g, b, 1)
                self.gradient = Ellipse(size=(self.width - dp(3), self.height - dp(3)),
                                        pos=(self.x, self.y + dp(3)))

        # FavoriteButton holds a palette animation favorite.
        if 3 in self.commands_dict:
            logging.debug(f'\tFavoriteButton updating color as Palette Gradient')
            hex_colors = [str(color) for color in self.commands_dict[3].hex_colors]
            gradient_texture = Gradient.horizontal(
                *[get_color_from_hex(color) for color in hex_colors])
            with self.canvas:
                Color(1, 1, 1)  # Set color to white, not sure why this is necessary.
                self.gradient = Ellipse(size=self.size, pos=self.pos, texture=gradient_texture)
                Color(0, 0, 0, 0.2)
                self.gradient = Ellipse(size=self.size, pos=self.pos)
                Color(1, 1, 1)
                self.gradient = Ellipse(size=(self.width - dp(2), self.height - dp(2)),
                                        pos=(self.x, self.y + dp(2)), texture=gradient_texture)

    def send_command(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` {args}')
        for command in self.commands_dict.values():
            self.favorites_bar.device_controller.send_command(command)
