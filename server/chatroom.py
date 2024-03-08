import socket

import threading


class Chatroom:
    def __init__(self, chatroom_name, P, G, host_client):
        self.chatroom_name = chatroom_name

        self.host_client = host_client
        self.joining_client = None
        self.clients = [self.host_client, self.joining_client]

        self.P = str(P)
        self.G = str(G)

        self.keys_exchanged = False

    """
    Chatroom message handling methods
    """

    def receive_message(self, client):
        message_len = int(client.recv(5).decode("utf-8"))
        message = client.recv(message_len)

        if len(message) != message_len:
            self.send_message("Error while receiving the message", client)
        else:
            return message.decode("utf-8")

    def create_header(self, message):
        header = f"{len(message):<5}"
        return header

    def send_message(self, message, client):
        header = self.create_header(message)

        client.send(header.encode('utf-8'))
        client.send(message.encode('utf-8'))

    def broadcast_message(self, message):
        for client in self.clients:
            self.send_message(message, client)

    """
    Chatroom key exchange logic
    """

    def key_exchange(self):
        self.broadcast_message("Key exchange started")

        self.broadcast_message(self.P)
        self.broadcast_message(self.G)

        host_message = self.receive_message(self.host_client)
        joining_message = self.receive_message(self.joining_client)

        self.host_client.send(joining_message)
        self.joining_client.send(host_message)

        self.broadcast_message("Key exchange ended")

    """
    Chatroom client handling logic
    """

    def handle_client(self):
        while True:
            for client in self.clients:
                try:
                    message = self.receive_message(client)
                    self.broadcast_message(message)
                except:
                    if client == self.host_client:
                        self.clients.remove(client)
                        self.host_client = None
                    elif client == self.joining_client:
                        self.clients.remove(client)
                        self.joining_client = None

    def start_chatroom_logic(self):
        while True:
            if self.joining_client is not None and self.keys_exchanged is False:
                self.key_exchange()
                self.keys_exchanged = True
            else:
                self.handle_client()
