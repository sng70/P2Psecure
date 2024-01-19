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
            self.write(message, client)

    def create_header(self, message):
        header = f"{len(message):<5}"
        return header

    def write(self, message, client):
        header = self.create_header(message)

        client.send(header.encode('utf-8'))
        client.send(message.encode('utf-8'))


    def receive(self, client):
        message_len = int(client.recv(5).decode("utf-8"))
        message = client.recv(message_len)

        if len(message) != message_len:
            client.send("Error while receiving the message")
        else:
            return message.decode("utf-8")

    def key_exchange(self, clients):
        self.broadcast("Diffie-Helman")

        self.broadcast(self.P)
        self.broadcast(self.G)

        host_message = self.receive(self.host_client)
        joining_message = self.receive(self.joining_client)

        clients[0].send(joining_message)
        clients[1].send(host_message)

    def handle(self):
        while True:
            for client in self.clients:
                try:
                    message = self.receive(client)
                    self.broadcast(message)
                except:
                    if client == self.host_client:
                        self.clients.remove(client)
                        self.host_client = None
                    elif client == self.joining_client:
                        self.clients.remove(client)
                        self.joining_client = None

    def run(self):
        while True:
            if self.joining_client is not None:
                self.key_exchange(self.clients)
            else:
                self.handle()