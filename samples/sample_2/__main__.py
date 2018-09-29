import os
import sys
from artnet.artnet_configurator import ArtNetConfigurator
from opcua import ua, Server

sample_folder = os.path.dirname(os.path.realpath(sys.argv[0]))

# Starting ArtNetServer
artnet_configurator = ArtNetConfigurator()
artnet_server = artnet_configurator.get_artnet_server(sample_folder + '/artnet_config.yml',
                                                      sample_folder + '/led_mapping.yml')
artnet_server.start_server()

# Setup and starting OPCUA Server
# Now setup our server
server = Server()
server.set_endpoint('opc.tcp://0.0.0.0:4840/freeopcua/server/')
server.set_server_name('ArtNet OPCUA-Server')

# Setup namespaces
artnet_ns = server.register_namespace('artnet')

if artnet_server:
    artnet_obj = server.nodes.objects.add_object(artnet_ns, 'art_net')

    for node in artnet_server.art_net_nodes:
        # Add method illuminate_slot
        artnet_obj.add_method(artnet_ns,
                              node.name + '_illuminate_slot',
                              node.illuminate_slot_opcua_call,
                              [ua.VariantType.String, ua.VariantType.String],
                              [ua.VariantType.Boolean])

        artnet_obj.add_method(artnet_ns,
                              node.name + '_illuminate_slot_with_history',
                              node.illuminate_slot_with_history_opcua_call,
                              [ua.VariantType.String,ua.VariantType.String, ua.VariantType.UInt64],
                              [ua.VariantType.Boolean])

        artnet_obj.add_method(artnet_ns,
                              node.name + '_illuminate_slot_dont_coll_history',
                              node.illuminate_slot_dont_coll_history_opcua_call,
                              [ua.VariantType.String, ua.VariantType.String],
                              [ua.VariantType.Boolean])

        artnet_obj.add_method(artnet_ns,
                              node.name + '_illuminate_multiple_slots',
                              node.illuminate_multiple_slots_opcua_call,
                              [ua.VariantType.String, ua.VariantType.String],
                              [ua.VariantType.Boolean])

        artnet_obj.add_method(artnet_ns,
                              node.name + '_illuminate_universe',
                              node.illuminate_universe_opcua_call,
                              [ua.VariantType.UInt64, ua.VariantType.String],
                              [ua.VariantType.Boolean])

        artnet_obj.add_method(artnet_ns,
                              node.name + '_illuminate_universe_rgb',
                              node.illuminate_universe_rgb_opcua_call,
                              [ua.VariantType.UInt64, ua.VariantType.UInt64, ua.VariantType.UInt64, ua.VariantType.Int64],
                              [ua.VariantType.Boolean])

        artnet_obj.add_method(artnet_ns,
                              node.name + '_illuminate_all',
                              node.illuminate_all_opcua_call,
                              [ua.VariantType.String],
                              [ua.VariantType.Boolean])

        artnet_obj.add_method(artnet_ns,
                              node.name + '_illuminate_from_to',
                              node.illuminate_from_to_opcua_call,
                              [ua.VariantType.UInt64, ua.VariantType.UInt64, ua.VariantType.UInt64, ua.VariantType.String],
                              [ua.VariantType.Boolean])

        artnet_obj.add_method(artnet_ns,
                              node.name + '_illuminate_from_to_rgb',
                              node.illuminate_from_to_rgb_opcua_call,
                              [ua.VariantType.UInt64, ua.VariantType.UInt64, ua.VariantType.UInt64, ua.VariantType.UInt64, ua.VariantType.UInt64, ua.VariantType.UInt64],
                              [ua.VariantType.Boolean])

        artnet_obj.add_method(artnet_ns,
                              node.name + '_all_off',
                              node.all_off_opcua_call,
                              '',
                              [ua.VariantType.Boolean])

server.start()