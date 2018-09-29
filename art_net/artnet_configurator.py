from pathlib import Path
import yaml
import re
import os
from .artnet_node import ArtNetNode, LEDStrip
from .artnet_node_planboard import ArtNetNodePlanboard
from .artnet_server import ArtNetServer


class ArtNetConfigurator:
    """Used for building an ArtNet Server with Nodes"""

    @staticmethod
    def get_patterns():
        pat_universe = re.compile('^universe_[0-9]+$')
        pat_universe_lines = re.compile('^universe_[0-9]+_lines$')
        return pat_universe, pat_universe_lines

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

        pat_universe, _ = ArtNetConfigurator.get_patterns()

        artnet_server = ArtNetServer(config_artnet['artnet_server']['ip_address'],
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
                    if pat_universe.match(node_option_key):
                        universe_id = node_option_key.split('_')[1]
                        strip_length = int(config_artnet[node_entry][node_option_key])
                        artnet_node.universe[universe_id] = LEDStrip(strip_length)
                    if node_option_key == 'color_history':
                        for color in node_option_val.split(','):
                            artnet_node.color_history.append(color)

                for mapping_entry in config_led_mapping:
                    if mapping_entry.startswith(artnet_node.name):
                        universe = config_led_mapping[mapping_entry]['universe']

                        for slot_entry in config_led_mapping[mapping_entry]:
                            if slot_entry.startswith('slot_'):
                                artnet_node.slots.update({slot_entry: {'universe': universe, 'led':
                                    config_led_mapping[mapping_entry][slot_entry]}})

                artnet_server.art_net_nodes.append(artnet_node)

        return artnet_server

    @staticmethod
    def get_artnet_server_no_slots():
        """:return: ArtNet Server with nodes from the .yml file"""
        pat_universe, pat_universe_lines = ArtNetConfigurator.get_patterns()

        config = ArtNetConfigurator.get_conf()
        artnet_server = ArtNetServer(config['artnet_server']['ip_address'], int(config['artnet_server']['port']))

        # Create ArtNet nodes
        for node_entry in config.keys():
            if node_entry.startswith('artnet_node_'):
                artnet_node = ArtNetNodePlanboard(config[node_entry]['name'], config[node_entry]['ip_address'],
                                         int(config[node_entry]['port']))
                artnet_node.universe = {}
                for (node_option_key, node_option_val) in config.get(node_entry).items():
                    if pat_universe.match(node_option_key):
                        universe_id = node_option_key.split('_')[1]
                        strip_length = int(config[node_entry][node_option_key])
                        artnet_node.universe[universe_id] = LEDStrip(strip_length)
                    if node_option_key == 'color_history':
                        for color in node_option_val.split(','):
                            artnet_node.color_history.append(color)
                    if pat_universe_lines.match(node_option_key):
                        universe_id = node_option_key.split('_')[1]
                        artnet_node.universe_to_lines.update({universe_id: config[node_entry][node_option_key]})

                artnet_server.art_net_nodes.append(artnet_node)

        return artnet_server

    @staticmethod
    def get_conf(config_file_name=None):
        if not config_file_name:
            config_file_name = Path(__file__).absolute().parents[2] / "conf" / "art_net.yml"

        with open(str(config_file_name), 'r') as ymlfile:
            return yaml.load(ymlfile)
