import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync_wordpress_published.py"
spec = importlib.util.spec_from_file_location("sync_wordpress_published", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class SyncParserTests(unittest.TestCase):
    def test_extracts_external_https_source_and_text(self):
        parser = mod.BodyParser()
        parser.feed('<p>বাংলা প্রতিবেদনের একটি দীর্ঘ অনুচ্ছেদ।</p><p><strong>তথ্যসূত্র:</strong> <a href="https://example.org/report">Example News</a></p>')
        self.assertIn("বাংলা প্রতিবেদনের", parser.markdown())
        self.assertNotIn("তথ্যসূত্র", parser.markdown())
        self.assertEqual(parser.links, [("https://example.org/report", ["Example News"][0])])

    def test_omits_images_and_figcaptions(self):
        parser = mod.BodyParser()
        parser.feed('<figure><img src="https://news.reazromen.com/media/test.svg"><figcaption>ক্যাপশন</figcaption></figure><p>মূল লেখা</p>')
        self.assertEqual(parser.markdown(), "মূল লেখা")

    def test_yaml_escaping(self):
        self.assertEqual(mod.safe_yaml('A "quoted" title'), '"A \\\"quoted\\\" title"')

    def test_slug_rules_reject_encoded_bangla_slug(self):
        import re
        self.assertRegex("valid-news-slug", r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertIsNone(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", "%e0%a6%ac"))

if __name__ == "__main__":
    unittest.main()
