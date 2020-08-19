from time import sleep
import os
import sys
from artnet.artnet_configurator import ArtNetConfigurator

sleep_time = 2
sample_folder = os.path.dirname(os.path.realpath(sys.argv[0]))

# Starting ArtNetServer
artnet_configurator = ArtNetConfigurator()
artnet_server = artnet_configurator.get_artnet_server(sample_folder + '/artnet_config.yml',
                                                      sample_folder + '/led_mapping.yml')
artnet_server.start_server()

# Run till thread has stopped
while artnet_server.thread.isAlive():
    try:
        artnet_server.art_net_nodes[0].flush_slot_history()
        print('flush history')
        sleep(sleep_time)

        artnet_server.art_net_nodes[0].illuminate_all('green')
        print('green')
        sleep(sleep_time)

        artnet_server.art_net_nodes[0].illuminate_all('red')
        print('red')
        sleep(sleep_time)

        artnet_server.art_net_nodes[0].illuminate_slot('3.1', 'red', 3, True)
        print('slot 3.1')
        sleep(sleep_time)

        artnet_server.art_net_nodes[0].illuminate_slot('9.2', 'red', 3, True)
        print('slot 9.2')
        sleep(sleep_time)

        artnet_server.art_net_nodes[0].illuminate_slot('1.1', 'red', 3, True)
        print('slot 1.1')
        sleep(sleep_time)

        artnet_server.art_net_nodes[0].illuminate_multiple_slots('6.1;6.2;6.3;6.4;7.1;7.2;7.3;7.4', 'magenta')
        print('slot 6.1;6.2;6.3;6.4;7.1;7.2;7.3;7.4')
        sleep(sleep_time)

        artnet_server.art_net_nodes[0].flush_slot_history()
        print('flush history')
        sleep(sleep_time)

        artnet_server.art_net_nodes[0].illuminate_slot('2.1', 'magenta', 3, True)
        print('slot 2.1')
        sleep(sleep_time)
        sleep(sleep_time)

    except KeyboardInterrupt:
        artnet_server.art_net_nodes[0].all_off()
        artnet_server.stop_server()
