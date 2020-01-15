from pathlib import Path
import yaml
import re
import ipaddress

from .artnet_node import ArtNetNode, LEDStrip
from .artnet_node_planboard import ArtNetNodePlanboard
from .artnet_server import ArtNetServer


class ArtNetConfigurator:
    """Used for building an ArtNet Server with Nodes"""
    pat_universe = re.compile('^universe_[0-9]+$')
    pat_universe_lines = re.compile('^universe_[0-9]+_lines$')

    @staticmethod
    def get_artnet_server(config_artnet=None, config_led_mapping=None):
        if config_artnet:
            config_artnet = ArtNetConfigurator.get_conf(config_artnet)
        else:
            raise FileNotFoundError('Please specify a file for config_artnet')

        if config_artnet:
            config_led_mapping = ArtNetConfigurator.get_conf(config_led_mapping)
        else:
            raise FileNotFoundError('Please specify a file for config_led_mapping')

        artnet_server = ArtNetServer(config_artnet['artnet_server']['ip_address'],
                                     ArtNetConfigurator.get_broadcast_addr(config_artnet),
                                     int(config_artnet['artnet_server']['port']))

        # Create ArtNet nodes
        for node_entry in config_artnet:
            if node_entry.startswith('artnet_node_'):
                artnet_node = ArtNetNode(config_artnet[node_entry]['name'],
                                         config_artnet[node_entry]['ip_address'],
                                         int(config_artnet[node_entry]['port']),
                                         int(config_artnet[node_entry]['max_history_size']))
                artnet_node.universe = {}
                for (node_option_key, node_option_val) in config_artnet[node_entry].items():
                    if ArtNetConfigurator.pat_universe.match(node_option_key):
                        universe_id = node_option_key.split('_')[1]
                        strip_length = int(config_artnet[node_entry][node_option_key])
                        artnet_node.universe[universe_id] = LEDStrip(strip_length)
                    if node_option_key == 'color_history':
                            artnet_node.color_history = config_artnet[node_entry][node_option_key]

                for mapping_entry in config_led_mapping:
                    if mapping_entry.startswith(artnet_node.name):
                        universe = config_led_mapping[mapping_entry]['universe']

                        for slot_entry in config_led_mapping[mapping_entry]:
                            if slot_entry.startswith('slot_'):
                                artnet_node.slots.update({int(slot_entry.split('_')[1]): {'universe': universe,
                                                                       'led': config_led_mapping[mapping_entry][slot_entry]}})

                artnet_server.art_net_nodes.append(artnet_node)

        return artnet_server

    @staticmethod
    def get_artnet_server_no_slots(config_artnet=None):
        """:return: ArtNet Server with nodes from the .yml file"""

        config = ArtNetConfigurator.get_conf(config_artnet)
        artnet_server = ArtNetServer(config['artnet_server']['ip_address'],
                                     ArtNetConfigurator.get_broadcast_addr(config_artnet),
                                     int(config['artnet_server']['port']))

        # Create ArtNet nodes
        for node_entry in config.keys():
            if node_entry.startswith('artnet_node_'):
                artnet_node = ArtNetNodePlanboard(config[node_entry]['name'], config[node_entry]['ip_address'],
                                                  int(config[node_entry]['port']))
                artnet_node.universe = {}
                for (node_option_key, node_option_val) in config.get(node_entry).items():
                    if ArtNetConfigurator.pat_universe.match(node_option_key):
                        universe_id = node_option_key.split('_')[1]
                        strip_length = int(config[node_entry][node_option_key])
                        artnet_node.universe[universe_id] = LEDStrip(strip_length)
                    if node_option_key == 'color_history':
                        for color in node_option_val.split(','):
                            artnet_node.color_history.append(color)
                    if ArtNetConfigurator.pat_universe_lines.match(node_option_key):
                        universe_id = node_option_key.split('_')[1]
                        artnet_node.universe_to_lines.update({universe_id: config[node_entry][node_option_key]})

                artnet_server.art_net_nodes.append(artnet_node)

        return artnet_server

    @staticmethod
    def get_conf(config_file_name=None):
        if not config_file_name:
            config_file_name = Path(__file__).absolute().parents[2] / "conf" / "artnet.yml"

        with open(str(config_file_name), 'r') as ymlfile:
            return yaml.load(ymlfile)

    @staticmethod
    def get_broadcast_addr(config_artnet):
        return str(ipaddress.IPv4Network(config_artnet['artnet_server']['ip_address'] + '/' +
                                         config_artnet['artnet_server']['netmask'], False).broadcast_address)
