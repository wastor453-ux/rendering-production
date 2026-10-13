"""
test_typography_roles.py — Semantic typography role regression tests.

Canonical values from src/light/tokens.ts.
"""
import unittest

TYPE = {
    "hook": {"min": 52, "max": 76, "weight": 700},
    "heading": {"min": 30, "max": 42, "weight": 600},
    "cardTitle": {"min": 22, "max": 28, "weight": 600},
    "body": {"min": 18, "max": 22, "weight": 400},
    "axis": {"min": 16, "max": 18, "weight": 500},
    "caption": {"min": 14, "max": 16, "weight": 400},
}

def in_range(role, size):
    spec = TYPE[role]
    return spec["min"] <= size <= spec["max"]

class TestTypographyRoles(unittest.TestCase):
    # Hook boundaries
    def test_hook_min(self):
        self.assertTrue(in_range("hook", 52))
    def test_hook_max(self):
        self.assertTrue(in_range("hook", 76))
    def test_hook_undersized(self):
        self.assertFalse(in_range("hook", 51))
    def test_hook_oversized(self):
        self.assertFalse(in_range("hook", 77))
    
    # Heading boundaries
    def test_heading_min(self):
        self.assertTrue(in_range("heading", 30))
    def test_heading_max(self):
        self.assertTrue(in_range("heading", 42))
    def test_heading_undersized(self):
        self.assertFalse(in_range("heading", 29))
    
    # CardTitle boundaries
    def test_cardtitle_min(self):
        self.assertTrue(in_range("cardTitle", 22))
    def test_cardtitle_max(self):
        self.assertTrue(in_range("cardTitle", 28))
    
    # Body boundaries
    def test_body_min(self):
        self.assertTrue(in_range("body", 18))
    def test_body_max(self):
        self.assertTrue(in_range("body", 22))
    def test_body_oversized(self):
        self.assertFalse(in_range("body", 23))
    
    # Axis boundaries
    def test_axis_min(self):
        self.assertTrue(in_range("axis", 16))
    def test_axis_max(self):
        self.assertTrue(in_range("axis", 18))
    
    # Caption boundaries
    def test_caption_min(self):
        self.assertTrue(in_range("caption", 14))
    def test_caption_max(self):
        self.assertTrue(in_range("caption", 16))
    def test_caption_oversized(self):
        self.assertFalse(in_range("caption", 17))
    
    # Incorrect role assignment: 24px is valid for cardTitle but NOT heading
    def test_incorrect_role_heading_vs_cardtitle(self):
        size = 24
        self.assertTrue(in_range("cardTitle", size))
        self.assertFalse(in_range("heading", size))
    
    # Unknown role
    def test_unknown_role(self):
        self.assertNotIn("subtitle", TYPE)
        self.assertNotIn("footnote", TYPE)
    
    # Explicit roles used in EventDrivenVideo
    def test_explicit_roles_used(self):
        with open("src/light/EventDrivenVideo.tsx") as f:
            content = f.read()
        self.assertIn('from "./Typography"', content)
        has_role = any(f"<{r}" in content for r in ["Hook", "Heading", "CardTitle", "Body", "Axis", "Caption"])
        self.assertTrue(has_role)

if __name__ == "__main__":
    unittest.main()
