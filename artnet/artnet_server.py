from threading import Thread
import socket
from queue import Queue
import logging
from datetime import datetime


class ArtNetServer:
    """Sends and receives ArtNet packets"""

    def __init__(self, host='',  port=6454, broadcast_addr=None):
        self.thread_run_ok = True
        self.send_queue = Queue()
        self.thread = Thread(target=self.server, args=())
        self.host = host
        self.art_net_nodes = []

        if port not in range(65536):
            raise ValueError('Only values between 0-65535 are valid for ports')
        self.port = port

        self.broadcast_addr = broadcast_addr
        if not self.broadcast_addr:
            self.broadcast_addr = self.host

    def server(self):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind((self.broadcast_addr, self.port))
            # Switch receiving broadcast packages to ON
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            server_socket.settimeout(0.2)
            logging.info("Started ArtNet server")
        except OSError as e:
            logging.critical("OS error: {0}".format(e))
        else:
            while self.thread_run_ok:
                try:
                    _, addr = server_socket.recvfrom(1024)
                    if len(addr[0]) > 0 and len(self.art_net_nodes) > 0:
                        for node in self.art_net_nodes:
                            if node.ip_address == addr[0]:
                                node.device_last_seen = datetime.now()

                except Exception as e:
                    if e.__str__() != 'timed out':
                        logging.error('ArtNet Server error: {}').format(e)

                for node in self.art_net_nodes:
                    if node.send_queue:
                        packet = node.send_queue.pop()
                        server_socket.sendto(packet, (node.ip_address, node.port))
                        server_socket.sendto(packet, (node.ip_address, node.port))

            server_socket.close()

    def start_server(self):
        self.thread_run_ok = True
        self.thread.start()

    def stop_server(self):
        self.thread_run_ok = False
