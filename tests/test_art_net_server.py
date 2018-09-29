from unittest import TestCase
from artnet.artnet_server import ArtNetServer


class TestArtNetServer(TestCase):
    def test_value_error(self):
        with self.assertRaises(ValueError):
            ArtNetServer(port=65536)

    def test_port(self):
        ans = ArtNetServer(port=65535)
        self.assertEqual(ans.port, 65535)
