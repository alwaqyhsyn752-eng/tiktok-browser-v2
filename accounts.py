import json
from pathlib import Path

class AccountStore:
    def __init__(self, path="accounts.json"):
        self.path = Path(path)
        self.data = {}
        if self.path.exists():
            try:
                parsed = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(parsed, dict):
                    self.data = parsed
            except json.JSONDecodeError:
                self.data = {}

    def save(self, name, cookie_str):
        if not name or not cookie_str:
            raise ValueError("اسم أو كوكيز فارغة")
        self.data[name] = {"cookies": cookie_str}
        self._persist()

    def load(self, name):
        if name not in self.data:
            raise KeyError(name)
        return self.data[name]["cookies"]

    def names(self):
        return list(self.data.keys())

    def remove(self, name):
        if name in self.data:
            del self.data[name]
            self._persist()
            return True
        return False

    def _persist(self):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        tmp.replace(self.path)
