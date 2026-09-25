import unittest

from sync_translate import get_translated_text, normalize_text


class SyncTranslateTests(unittest.TestCase):
    def test_normalize_collapses_whitespace(self):
        self.assertEqual(normalize_text("  hola   que  tal "), "hola que tal")

    def test_known_phrase_es_to_en(self):
        self.assertEqual(get_translated_text("hola que tal", "es", "en"), "Hello, how are you?")

    def test_known_phrase_en_to_es(self):
        self.assertEqual(
            get_translated_text("this is a test string", "en", "es"),
            "Esta es una cadena de prueba",
        )

    def test_known_phrase_en_to_fr(self):
        self.assertEqual(
            get_translated_text("this value will be translated", "en", "fr"),
            "Cette valeur sera traduite",
        )

    def test_same_language_returns_original(self):
        self.assertEqual(get_translated_text("hola que tal", "es", "es"), "hola que tal")

    def test_unknown_phrase_fallback(self):
        self.assertEqual(
            get_translated_text("custom text", "en", "fr"),
            "[translation for fr] custom text",
        )


if __name__ == "__main__":
    unittest.main()
