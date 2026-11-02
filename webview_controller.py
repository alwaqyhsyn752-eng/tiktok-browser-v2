from jnius import autoclass, PythonJavaClass, java_method
from android.runnable import run_on_ui_thread
from kivy.clock import Clock

WebView = autoclass("android.webkit.WebView")
WebViewClient = autoclass("android.webkit.WebViewClient")
WebChromeClient = autoclass("android.webkit.WebChromeClient")
Activity = autoclass("org.kivy.android.PythonActivity")
LayoutParams = autoclass("android.view.ViewGroup$LayoutParams")
CookieManager = autoclass("android.webkit.CookieManager")
View = autoclass("android.view.View")

class _JsCallback(PythonJavaClass):
    __javainterfaces__ = ["android/webkit/ValueCallback"]
    __javacontext__ = "app"

    def __init__(self, cb):
        super().__init__()
        self.cb = cb

    @java_method("(Ljava/lang/Object;)V")
    def onReceiveValue(self, value):
        try:
            self.cb(value)
        except Exception:
            pass

class WebViewController:
    def __init__(self):
        self._wv = None
        self._ready = False

    @run_on_ui_thread
    def _ensure_ready(self):
        if self._ready:
            return
        activity = Activity.mActivity
        wv = WebView(activity)
        settings = wv.getSettings()
        settings.setJavaScriptEnabled(True)
        settings.setDomStorageEnabled(True)
        settings.setDatabaseEnabled(True)
        settings.setMediaPlaybackRequiresUserGesture(False)
        settings.setMixedContentMode(0)
        settings.setUserAgentString(
            "Mozilla/5.0 (Linux; Android 13; SM-S918B) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Mobile Safari/537.36"
        )
        wv.setWebViewClient(WebViewClient())
        wv.setWebChromeClient(WebChromeClient())
        cm = CookieManager.getInstance()
        cm.setAcceptCookie(True)
        cm.setAcceptThirdPartyCookies(wv, True)
        self._wv = wv
        self._ready = True

    @run_on_ui_thread
    def _load_ui(self, url):
        activity = Activity.mActivity
        self._wv.loadUrl(url)
        if self._wv.getParent() is None:
            activity.addContentView(self._wv, LayoutParams(-1, -1))
        self._wv.setVisibility(View.VISIBLE)
        self._wv.bringToFront()

    @run_on_ui_thread
    def _hide_ui(self):
        if self._wv is not None:
            self._wv.setVisibility(View.GONE)

    @run_on_ui_thread
    def _eval_ui(self, js, callback):
        self._wv.evaluateJavascript(js, _JsCallback(callback))

    @run_on_ui_thread
    def _get_cookies_ui(self, url, callback):
        cm = CookieManager.getInstance()
        cm.flush()
        value = cm.getCookie(url)
        Clock.schedule_once(lambda dt: callback(value), 0)

    @run_on_ui_thread
    def _set_cookies_ui(self, url, cookie_str, callback):
        cm = CookieManager.getInstance()
        if cookie_str:
            for pair in cookie_str.split(";"):
                p = pair.strip()
                if "=" in p:
                    cm.setCookie(url, p)
        cm.flush()
        Clock.schedule_once(lambda dt: callback(True), 0)

    @run_on_ui_thread
    def _clear_cookies_ui(self, callback):
        cm = CookieManager.getInstance()
        cm.removeAllCookies(None)
        cm.flush()
        Clock.schedule_once(lambda dt: callback(True), 0)

    def open(self, url):
        self._ensure_ready()
        self._load_ui(url)

    def hide(self):
        self._hide_ui()

    def evaluate(self, js, callback):
        self._eval_ui(js, callback)

    def get_cookies(self, url, callback):
        self._get_cookies_ui(url, callback)

    def set_cookies(self, url, cookie_str, callback):
        self._set_cookies_ui(url, cookie_str, callback)

    def clear_cookies(self, callback):
        self._clear_cookies_ui(callback)
