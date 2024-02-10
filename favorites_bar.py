import logging
from kivy.properties import NumericProperty, ObjectProperty
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRoundFlatButton
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from bluetooth_helpers import Command
from troubleshooting import func_name


class FavoritesBar(MDBoxLayout):

    def add_favorite(self, *args):
        fav_btn = FavoriteButton(favorites_bar=self)
        self.ids.favorites_.add_widget(fav_btn)

    def delete_favorite(self, fav_btn):
        self.ids.favorites_.remove_widget(fav_btn)


class AddFavoriteButton(MDIconButton):
    pass


class FavoriteButton(MDRoundFlatButton):
    favorites_bar = ObjectProperty()
    long_press_time = NumericProperty(0.5)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._long_press_event = Clock.schedule_once(lambda x: 0, 0)
        self.dialog = MDDialog()
        self.dialog_open = False

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

    def send_command(self, *args):
        logging.debug(f'`{self.__class__.__name__}.{func_name()}` {args}')
