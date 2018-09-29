from unittest import TestCase
from artnet.color import Color


class TestColor(TestCase):
    def test_set_color(self):
        col = Color(0, 255, 255)
        self.assertEqual(col.red, 0)
        self.assertEqual(col.green, 255)
        self.assertEqual(col.blue, 255)

        col.set_color("orange")  # orange: [50, 25, 0]
        self.assertEqual(col.red, 50)
        self.assertEqual(col.green, 25)
        self.assertEqual(col.blue, 0)

    def test_value_error(self):
        """
        Expects a ValueError
        """
        with self.assertRaises(ValueError):
            Color(256, 0, 0)
