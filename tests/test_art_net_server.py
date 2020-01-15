from unittest import TestCase
from artnet.artnet_server import ArtNetServer


class TestArtNetServer(TestCase):
    def test_value_error(self):
        with self.assertRaises(ValueError):
            ArtNetServer('127.0.0.1', '255.255.255.255', port=65536)

    def test_port(self):
        ans = ArtNetServer('127.0.0.1', '255.255.255.255', port=65535)
        self.assertEqual(ans.port, 65535)
