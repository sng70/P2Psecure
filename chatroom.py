import random

class Chatroom:
    def __init__(self, chatroom_name, host_client, P, G):
        self.chatroom_name = chatroom_name

        self.host_client = host_client
        self.joining_client = None
        self.clients = [self.host_client, self.joining_client]

        self.P = P
        self.G = G

    def broadcast(self, message):
        for client in self.clients:
            client.send(message)

    def key_exchange(self, clients):
        self.broadcast(self.P.encode("utf-8"))
        self.broadcast(self.G.encode("utf-8"))

        host_message = clients[0].receive()
        joining_message = clients[1].receive()

        clients[0].send(joining_message)
        clients[1].send(host_message)

    def handle(self):
        while True:
            for client in self.clients:
                try:
                    message_len = client.recv(10).decode("utf-8")
                    message = client.recv(message_len)

                    if len(message) != message_len:
                        break
                    else:
                        self.broadcast(message)
                except:
                    if client == self.host_client:
                        self.clients.remove(client)
                        self.host_client = None
                    elif client == self.joining_client:
                        self.clients.remove(client)
                        self.joining_client = None

    def reveive(self):
        while True:
            if self.joining_client is not None:
                self.key_exchange(self.clients)
            else:
                self.handle()