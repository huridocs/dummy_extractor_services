"""Deterministic stubs for sync POST /translate (Uwazi translationService)."""

from __future__ import annotations

SUPPORTED_LANGUAGES = ("en", "fr", "es", "ru", "ar")

# Exact source phrases (normalized: strip + lower) → per-target translations.
TRANSLATION_STUBS: dict[str, dict[str, str]] = {
    "hola que tal": {
        "en": "Hello, how are you?",
        "es": "Hola, ¿qué tal?",
        "fr": "Salut, ça va ?",
        "ru": "Привет, как дела?",
        "ar": "مرحبا، كيف حالك؟",
    },
    "this is a test string": {
        "en": "This is a test string",
        "es": "Esta es una cadena de prueba",
        "fr": "Ceci est une chaîne de test",
        "ru": "Это тестовая строка",
        "ar": "هذه سلسلة اختبار",
    },
    "this value will be translated": {
        "en": "This value will be translated",
        "es": "Este valor será traducido",
        "fr": "Cette valeur sera traduite",
        "ru": "Это значение будет переведено",
        "ar": "سيتم ترجمة هذه القيمة",
    },
}


def normalize_text(text: str) -> str:
    return " ".join(text.strip().split()).lower()


def get_translated_text(text: str, language_from: str, language_to: str) -> str:
    language_from = language_from.lower()[:2]
    language_to = language_to.lower()[:2]

    if language_from == language_to:
        return text

    stub = TRANSLATION_STUBS.get(normalize_text(text))
    if stub and language_to in stub:
        return stub[language_to]

    return f"[translation for {language_to}] {text}"
