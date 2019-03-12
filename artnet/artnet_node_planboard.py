import copy
import logging

from .artnet_node import ArtNetNode, ArtNetDMXPacket, PacketType


class ArtNetNodePlanboard(ArtNetNode):
    def __init__(self, name, ip_address, port=6454):
        ArtNetNode.__init__(self, name, ip_address, port, max_history_size=5)
        # Contains a dict with universes and a list of their lines. E.g.: {1: [0, 1], 3: [2, 3]}
        self.universe_to_lines = {}

    def set_led_strip(self, extracted_lines):
        logging.debug(self.universe_to_lines)
        for universe, lines in self.universe_to_lines.items():
            tmp_led_strip = copy.deepcopy(self.universe[universe])
            logging.debug(tmp_led_strip)
            board_coordinates = []
            
            for line in lines:
                sorted_columns = sorted(extracted_lines[line], key=lambda column: column['column_id'], reverse=True)
                sorted_columns.pop(0)
                board_coordinates.extend(sorted_columns)

            for counter, color in enumerate(tmp_led_strip.led_strip):
                if not board_coordinates[counter]['led_color']:
                    color.set_color('black')
                else:
                    color.set_color(board_coordinates[counter]['led_color'], True)

            self.send_queue.append(ArtNetDMXPacket(PacketType.ART_DMX,
                                                   self.sequence,
                                                   0,
                                                   int(universe),
                                                   tmp_led_strip.to_byte_array()).packet_to_byte_array())
