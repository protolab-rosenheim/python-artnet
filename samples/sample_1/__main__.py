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
        artnet_server.art_net_nodes[0].illuminate_all('green')
        print('green')
        sleep(sleep_time)

        artnet_server.art_net_nodes[0].illuminate_all('red')
        print('red')
        sleep(sleep_time)

        artnet_server.art_net_nodes[0].illuminate_slot('3.1', 'red', 0, False)
        print('partly red')
        sleep(sleep_time)

    except KeyboardInterrupt:
        artnet_server.stop_server()
