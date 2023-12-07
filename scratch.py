from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.list import OneLineListItem
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField

KV = '''
BoxLayout:
    orientation: 'vertical'
    
    MDToolbar:
        title: 'To-Do List'
        left_action_items: [['menu', lambda x: app.callback()]]
    
    ScrollView:
        MDList:
            id: todo_list
            
    BoxLayout:
        size_hint_y: None
        height: "48dp"
        
        MDTextField:
            id: task_input
            hint_text: "Enter task"
            helper_text: "Press 'Enter' to add task"
            on_text_validate: app.add_task()
        
        MDRaisedButton:
            text: "Add Task"
            on_release: app.add_task()
'''


class TodoListApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def add_task(self):
        task_text = self.root.ids.task_input.text
        if task_text:
            self.root.ids.todo_list.add_widget(OneLineListItem(text=task_text))
            self.root.ids.task_input.text = ""

    def callback(self):
        print("Menu button pressed")


if __name__ == "__main__":
    TodoListApp().run()