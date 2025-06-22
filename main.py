from kivy.app import App
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout  # ✅ Add this
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.animation import Animation
from reportlab.pdfgen import canvas
from android.permissions import request_permissions, Permission
from android.storage import primary_external_storage_path
from jnius import autoclass, cast
import shutil

from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.core.window import Window

from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
from kivy.uix.widget import Widget
from kivy.graphics.texture import Texture

import time

import io


def show_toast(message):
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Toast = autoclass('android.widget.Toast')
    String = autoclass('java.lang.String')
    context = PythonActivity.mActivity

    Toast.makeText(context, String(message), Toast.LENGTH_SHORT).show()

from android.storage import primary_external_storage_path

import os
import json
import webbrowser
from android import mActivity



from utils import (
    get_word_count, get_grammar_tips, generate_outline,
    save_draft, load_draft, list_drafts, load_dictionary
)

# Set Android or Desktop file save path
try:
    from android.storage import primary_external_storage_path
    save_path = primary_external_storage_path() + "/Download/betawrite"
except ImportError:
    save_path = "./"

# Files & folders
USERS_FILE = "users.json"
ESSAY_DIR = "saved_essays"
if not os.path.exists(ESSAY_DIR):
    os.makedirs(ESSAY_DIR)

# Load users
users = json.load(open(USERS_FILE)) if os.path.exists(USERS_FILE) else {}
current_user = {"username": ""}


# ===== Screens =====
class SplashScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.switch_to_login, 2)

    def switch_to_login(self, dt):
        self.manager.current = 'login'


class LoginScreen(Screen):
    def login(self):
        username = self.ids.login_username.text.strip()
        password = self.ids.login_password.text.strip()
        if username in users and users[username] == password:
            current_user["username"] = username
            self.manager.current = 'home'
        else:
            self.ids.login_status.text = "Invalid credentials!"


class RegisterScreen(Screen):
    def register(self):
        username = self.ids.reg_username.text.strip()
        password = self.ids.reg_password.text.strip()
        if username and password:
            if username in users:
                self.ids.register_status.text = "Username already exists!"
            else:
                users[username] = password
                with open(USERS_FILE, "w") as f:
                    json.dump(users, f)
                self.ids.register_status.text = "Registered successfully!"
        else:
            self.ids.register_status.text = "Enter valid details!"


class HomeScreen(Screen):
    pass



class ModelEssayScreen(Screen):
    def load_essay(self, essay_type):
        path = f"assets/model_essays/{essay_type}.txt"
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.ids.essay_view.text = f.read()
        else:
            self.ids.essay_view.text = "Essay not found."


class DictionaryScreen(Screen):
    def on_pre_enter(self):
        dict_file = "assets/dictionary.txt"
        self.dictionary = load_dictionary(dict_file)
        self.ids.result_label.text = ""

    def search_word(self):
        word = self.ids.dict_input.text.strip().lower()
        meaning = self.dictionary.get(word, "Definition not found.")
        self.ids.result_label.text = f"{word}:\n{meaning}"

class WriteEssayScreen(Screen):
    def load_template(self, template_type):
        path = f"assets/templates/{template_type}_template.txt"
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.ids.essay_input.text = f.read()
        else:
            self.ids.essay_input.text = "Template not found."
        self.update_info()

    def save_essay(self):
        text = self.ids.essay_input.text
        username = current_user.get("username", "default")
        path = os.path.join(ESSAY_DIR, f"{username}_essay.txt")
        with open(path, "w") as f:
            f.write(text)
        Popup(title='Saved',
              content=Label(text='Essay saved!'),
              size_hint=(None, None), size=(300, 150)).open()

    def generate_outline(self):
        template_type = self.ids.template_spinner.text
        outline = generate_outline(template_type)
        self.ids.essay_input.text = outline
        self.update_info()

    def export_pdf(self):
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            text = self.ids.essay_input.text
            username = current_user.get("username", "user")
            pdf_path = os.path.join(save_path, f"{username}_essay.pdf")
            c = canvas.Canvas(pdf_path, pagesize=letter)
            width, height = letter
            y = height - 50
            for line in text.split("\n"):
                c.drawString(50, y, line)
                y -= 15
                if y < 50:
                    c.showPage()
                    y = height - 50
            c.save()
            Popup(title='PDF Exported',
                  content=Label(text='Saved to Downloads!'),
                  size_hint=(None, None), size=(300, 150)).open()
        except Exception as e:
            Popup(title='Error', content=Label(text=str(e)),
                  size_hint=(None, None), size=(300, 150)).open()

    def save_draft(self):
        title = self.ids.draft_title.text.strip()
        text = self.ids.essay_input.text
        if title:
            save_draft(current_user["username"], title, text)
            self.ids.draft_status.text = "Draft saved."
        else:
            self.ids.draft_status.text = "Enter draft title."

    def load_draft(self):
        title = self.ids.draft_title.text.strip()
        if title:
            text = load_draft(current_user["username"], title)
            self.ids.essay_input.text = text
            self.ids.draft_status.text = f"Loaded '{title}'."
        else:
            self.ids.draft_status.text = "Enter draft title."

    def update_info(self):
        text = self.ids.essay_input.text
        wc = get_word_count(text)
        tips = get_grammar_tips(text)
        self.ids.word_count.text = f"Word Count: {wc}"
        self.ids.grammar_tips.text = "Tips: " + "; ".join(tips if tips else ["None"])

class RubricScreen(Screen):
    def load_rubric(self, rubric_type):
        rubrics = {
            'Narrative': "Narrative Rubric:\n- Creativity\n- Plot Development\n- Grammar\n- Vocabulary",
            'Article': "Article Rubric:\n- Clarity\n- Logical Flow\n- Tone and Audience\n- Grammar",
            'Formal Letter': "Formal Letter Rubric:\n- Format\n- Content\n- Language Use\n- Punctuation",
            'Speech': "Speech Rubric:\n- Structure\n- Persuasiveness\n- Language and Delivery"
        }
        self.ids.rubric_text.text = rubrics.get(rubric_type, "Rubric not available.")


class ImagePageViewerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.page_images = []
        self.page_index = 0
        self.last_touch_time = 0

    def on_pre_enter(self):
        self.load_pages()
        self.show_page(0)

    def load_pages(self):
        folder = "assets/model_pages/"
        self.page_images = sorted(
            [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".png")]
        )

    def show_page(self, index):
        if 0 <= index < len(self.page_images):
            self.page_index = index
            self.ids.image_widget.source = self.page_images[index]
            self.ids.page_label.text = f"Page {index + 1} of {len(self.page_images)}"
            self.reset_zoom()

    def reset_zoom(self):
        scatter = self.ids.scatter
        scatter.scale = 1
        scatter.pos = (0, 0)
        scatter.center = self.center

    def next_page(self):
        if self.page_index < len(self.page_images) - 1:
            self.show_page(self.page_index + 1)

    def prev_page(self):
        if self.page_index > 0:
            self.show_page(self.page_index - 1)

    def on_touch_down(self, touch):
        self.touch_start_x = touch.x
        current_time = time.time()
        if current_time - self.last_touch_time < 0.3:
            self.reset_zoom()
        self.last_touch_time = current_time
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        dx = touch.x - self.touch_start_x
        if abs(dx) > 50:
            if dx < 0:
                self.next_page()
            else:
                self.prev_page()
        return super().on_touch_up(touch)

class SplashScreen(Screen):
    def on_enter(self):
        from kivy.clock import Clock
        from kivy.animation import Animation
        Clock.schedule_once(self.fade_out, 10)

    def fade_out(self, dt):
        anim = Animation(opacity=0, duration=1)
        anim.bind(on_complete=self.switch_to_login)
        anim.start(self)

    def switch_to_login(self, *args):
        self.manager.current = 'login'



# ===== App Loader =====
class EssayApp(App):
    def build(self):
        sm = Builder.load_file('essay_writer.kv')
        sm.current = 'splash'
        return sm

Builder.load_file("essay_writer.kv")

if __name__ == '__main__':
    EssayApp().run()