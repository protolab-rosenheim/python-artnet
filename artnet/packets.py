from enum import Enum


class ArtNetPacket(object):
    # Contains the ASCII string Art-Net\0
    ID_FIELD = bytearray([65, 114, 116, 45, 78, 101, 116, 0])
    # contains protocol version
    PROTOCOL_VERSION = bytearray.fromhex('00 0e')

    def __init__(self, packet_type):
        self.packet_type = packet_type


class PacketType(Enum):
    ART_POLL = bytearray.fromhex('00 20')
    ART_POLL_REPLY = bytearray.fromhex('00 21')
    ART_DMX = bytearray.fromhex('00 50')


class ArtNetDMXPacket(ArtNetPacket):
    def __init__(self, packet_type, sequence, physical_input_port, universe, data):
        super().__init__(packet_type)

        if sequence not in range(256):
            raise ValueError("Only values between 0-255 are valid")
        self.sequence = sequence
        self.physical_input_port = physical_input_port

        if universe not in range(65536):
            raise ValueError("Only values between 0-65535 are valid")
        universe_1, universe_2 = (universe & 0xFFFFFFFF).to_bytes(2, 'big')
        self.universe = bytearray([universe_2, universe_1])
        self.data = data

    def packet_to_byte_array(self):
        packet = bytearray(self.ID_FIELD)
        packet.extend(self.packet_type.value)
        packet.extend(self.PROTOCOL_VERSION)
        packet.append(self.sequence)
        packet.append(self.physical_input_port)
        packet.extend(self.universe)
        len_1, len_2 = (len(self.data) & 0xFFFFFFFF).to_bytes(2, 'big')
        packet.extend([len_1, len_2])
        packet.extend(self.data)

        return packet

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.packet_to_byte_array() == other.packet_to_byte_array():
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
