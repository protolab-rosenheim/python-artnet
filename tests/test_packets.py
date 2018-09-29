from unittest import TestCase
from artnet.packets import ArtNetDMXPacket


class DummyPacket(object):
    def __init__(self, packet):
        self._packet = packet

    @property
    def value(self):
        return self._packet


class TestArtNetDMXPacket(TestCase):
    def test_packet_to_byte_array(self):
        test_andp = ArtNetDMXPacket(packet_type=DummyPacket([1, 42, 222]),
                                    sequence=255,
                                    physical_input_port=20,
                                    universe=65535,
                                    data=b'HalloWelt')
        self.assertEqual(test_andp.packet_to_byte_array(),
                         bytearray(b'Art-Net\x00\x01*\xde\x00\x0e\xff\x14\xff\xff\x00\tHalloWelt'))
