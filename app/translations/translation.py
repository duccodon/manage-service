import importlib
from typing import Any, Dict

"""
mã language code theo https: // en.wikipedia.org/wiki/List_of_ISO_639_language_codes
"""


class Translator:
    _instances: Dict[str, "Translator"] = {}

    def __new__(cls, lang: str) -> "Translator":
        if lang not in cls._instances:
            cls._instances[lang] = super(Translator, cls).__new__(cls)
        return cls._instances[lang]

    def __init__(self, lang: str):
        self.lang = lang

    def t(self, key: str, **kwargs: Dict[str, Any]) -> str:
        try:
            translation_keys = key.split(".")

            locale_module = importlib.import_module(f"app.locales.{self.lang}.messages")

            translation = locale_module.locale
            for translation_key in translation_keys:
                translation = translation.get(translation_key, None)
                if translation is None:
                    return key
            if kwargs.keys():
                translation = translation.format(**kwargs)
            return translation
        except:
            return key


def parse_accept_language(language: str) -> str | None:
    if not language:
        return None

    # Tách chuỗi thành danh sách các ngôn ngữ
    languages = []
    for l in language.split(","):
        parts = l.split(";q=")
        lang = parts[0].strip().split("-")[0]  # Lấy phần ngôn ngữ
        # Nếu có q-value thì chuyển nó thành số float, nếu không thì đặt mặc định là 1.0
        quality = float(parts[1]) if len(parts) > 1 else 1.0
        languages.append({"language": lang, "quality": quality})

    # Sắp xếp theo quality giảm dần
    languages = sorted(languages, key=lambda x: x["quality"], reverse=True)

    value = map(lambda x: x.get("language"), languages)

    return list(value)[0]


class TranslatorException:
    def __init__(self, message: str, **params: Dict[str, Any]):
        self.message = message  # Thông điệp lỗi
        self.params = params  # Các tham số bổ sung

    def __str__(self):
        # Trả về chuỗi mô tả lỗi
        param_str = ", ".join(f"{key}: {value}" for key, value in self.params.items())
        return f"key: {self.message} | Params: {param_str}"
