from unittest import TestCase
from artnet.artnet_node import LEDStrip, ArtNetNode
from artnet.color import Color


class TestLEDStrip(TestCase):
    def test_value_error(self):
        with self.assertRaises(ValueError):
            LEDStrip(-1)

    def test_preinit_strip(self):
        leds = LEDStrip(2)
        self.assertEqual(leds.led_strip,
                         [Color(0, 0, 0), Color(0, 0, 0)])

    def test_to_bytearray(self):
        leds = LEDStrip(1)
        self.assertEqual(leds.to_byte_array(),
                         bytearray(b'\x00\x00\x00'))


class TestArtNetNode(TestCase):
    def test_value_error(self):
        with self.assertRaises(ValueError):
            ArtNetNode(name='Node',
                       ip_address='192.168.0.1',
                       port=65536)

    def test_value_error_history(self):
        with self.assertRaises(ValueError):
            ArtNetNode(name='Node',
                       ip_address='192.168.0.1',
                       port=65535,
                       max_history_size=101)
