import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.logger import Logger

from webview_controller import WebViewController
from accounts import AccountStore
from engagement_js import JS_LIKE, JS_COMMENT_TEMPLATE, JS_PAGE_DIAGNOSTICS

TIKTOK_HOME = "https://www.tiktok.com/"
VIEW_SECONDS = 30

class MainScreen(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", padding=10, spacing=6, **kw)
        self.wv = WebViewController()
        self.store = AccountStore()
        self._build_ui()

    def _build_ui(self):
        self.add_widget(Label(text="TikTok Browser Automation", size_hint_y=0.06))
        self.status_label = Label(text="جاهز", size_hint_y=0.06)
        self.add_widget(self.status_label)
        self.name_input = TextInput(hint_text="اسم حساب احتياطي", size_hint_y=0.06, multiline=False)
        self.add_widget(self.name_input)

        row = BoxLayout(size_hint_y=0.07, spacing=4)
        row.add_widget(Button(text="افتح TikTok", on_release=self.open_tiktok))
        row.add_widget(Button(text="رجوع", on_release=self.hide_webview))
        self.add_widget(row)

        row2 = BoxLayout(size_hint_y=0.07, spacing=4)
        row2.add_widget(Button(text="حفظ الحساب", on_release=self.save_account))
        row2.add_widget(Button(text="تحميل حساب", on_release=self.load_account))
        self.add_widget(row2)

        row3 = BoxLayout(size_hint_y=0.07, spacing=4)
        self.acc_spinner = Spinner(text="اختر حساباً", values=self.store.names())
        row3.add_widget(self.acc_spinner)
        row3.add_widget(Button(text="حذف", size_hint_x=0.25, on_release=self.delete_account))
        self.add_widget(row3)

        self.url_input = TextInput(hint_text="رابط الفيديو", size_hint_y=0.06, multiline=False)
        self.add_widget(self.url_input)

        row4 = BoxLayout(size_hint_y=0.07, spacing=4)
        row4.add_widget(Button(text="تشخيص", on_release=self.diagnose))
        row4.add_widget(Button(text="إعجاب", on_release=self.do_like))
        row4.add_widget(Button(text="مشاهدة", on_release=self.do_view))
        self.add_widget(row4)

        row5 = BoxLayout(size_hint_y=0.07, spacing=4)
        self.comment_input = TextInput(hint_text="نص التعليق", multiline=False)
        row5.add_widget(self.comment_input)
        row5.add_widget(Button(text="تعليق", size_hint_x=0.3, on_release=self.do_comment))
        self.add_widget(row5)

        scroll = ScrollView(size_hint_y=0.2)
        self.log_label = Label(text="", size_hint_y=None, halign="left", valign="top", text_size=(self.width, None))
        self.log_label.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
        self.log_label.bind(texture_size=lambda inst, s: setattr(inst, "height", s[1]))
        scroll.add_widget(self.log_label)
        self.add_widget(scroll)

    def log(self, msg):
        Logger.info(f"TikTokApp: {msg}")
        self.status_label.text = msg
        self.log_label.text += "\n" + msg

    def open_tiktok(self, *a):
        url = self.url_input.text.strip() or TIKTOK_HOME
        self.wv.open(url)
        self.log(f"فتح: {url}")

    def hide_webview(self, *a):
        self.wv.hide()
        self.log("تم الإخفاء")

    def save_account(self, *a):
        name = self.name_input.text.strip()
        if not name:
            self.log("أدخل اسماً")
            return
        def _cb(cookies):
            if not cookies:
                self.log("لا كوكيز")
                return
            try:
                self.store.save(name, cookies)
                self.acc_spinner.values = self.store.names()
                self.log(f"حُفظ: {name}")
            except ValueError as e:
                self.log(f"خطأ: {e}")
        self.wv.get_cookies(TIKTOK_HOME, _cb)

    def load_account(self, *a):
        name = self.acc_spinner.text
        if name == "اختر حساباً" or not name:
            return
        try:
            cookie_str = self.store.load(name)
        except KeyError:
            self.log("غير موجود")
            return
        def _after_set(ok):
            self.wv.open(TIKTOK_HOME)
            self.log(f"حُمّل: {name}")
        def _after_clear(ok):
            self.wv.set_cookies(TIKTOK_HOME, cookie_str, _after_set)
        self.wv.clear_cookies(_after_clear)

    def delete_account(self, *a):
        name = self.acc_spinner.text
        if name == "اختر حساباً" or not name:
            return
        if self.store.remove(name):
            self.acc_spinner.values = self.store.names()
            self.acc_spinner.text = "اختر حساباً"
            self.log(f"حُذف: {name}")

    def _require_url(self):
        url = self.url_input.text.strip()
        if not url:
            self.log("أدخل رابط")
            return None
        return url

    def diagnose(self, *a):
        url = self._require_url()
        if not url: return
        self.wv.open(url)
        def _run(dt):
            def _cb(result):
                self.log(f"تشخيص: {result}")
            self.wv.evaluate(JS_PAGE_DIAGNOSTICS, _cb)
        Clock.schedule_once(_run, 8)

    def do_like(self, *a):
        url = self._require_url()
        if not url: return
        self.wv.open(url)
        def _run(dt):
            def _cb(result):
                self.log(f"إعجاب: {result}")
            self.wv.evaluate(JS_LIKE, _cb)
        Clock.schedule_once(_run, 8)

    def do_comment(self, *a):
        url = self._require_url()
        text = self.comment_input.text.strip()
        if not url or not text: return
        self.wv.open(url)
        js = JS_COMMENT_TEMPLATE.replace("%%TEXT%%", json.dumps(text))
        def _run(dt):
            def _cb(result):
                self.log(f"تعليق: {result}")
            self.wv.evaluate(js, _cb)
        Clock.schedule_once(_run, 8)

    def do_view(self, *a):
        url = self._require_url()
        if not url: return
        self.wv.open(url)
        self.log(f"مشاهدة {VIEW_SECONDS} ث...")
        Clock.schedule_once(lambda dt: self.log("انتهت"), VIEW_SECONDS)

class TikTokBrowserApp(App):
    def build(self):
        return MainScreen()

if __name__ == "__main__":
    TikTokBrowserApp().run()
