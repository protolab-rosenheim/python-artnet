from time import sleep
import os
import sys
from art_net.artnet_configurator import ArtNetConfigurator

sleep_time = 2
thread_list = []

sample_folder = os.path.dirname(os.path.realpath(sys.argv[0]))

# Starting ArtNetServer
artnet_configurator = ArtNetConfigurator()
artnet_server = artnet_configurator.get_artnet_server(sample_folder + '/artnet_config.yml',
                                                      sample_folder + '/led_mapping.yml')
artnet_server.start_server()
thread_list.append(artnet_server.thread)

# Run till every thread has finished
while thread_list:
    artnet_server.art_net_nodes[0].illuminate_all('green')
    print('green')
    sleep(sleep_time)

    artnet_server.art_net_nodes[0].illuminate_all('red')
    print('red')
    sleep(sleep_time)

    for thread in thread_list:
        if not thread.isAlive():
            thread_list.remove(thread)
