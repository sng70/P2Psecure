class Chatroom:
    def __init__(self, chatroom_name, host_client, P, G):
        self.chatroom_name = chatroom_name

        self.host_client = host_client
        self.joining_client = None
        self.clients = [self.host_client, self.joining_client]

        self.P = str(P)
        self.G = str(G)

        self.keys_exchanged = False

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
        message = client.recv(message_len).strip("\n")


        if len(message) != message_len:
            client.send("Error while receiving the message")
        else:
            return message.decode("utf-8")

    def key_exchange(self):
        self.broadcast("Diffie-Helman")

        self.broadcast(self.P)
        self.broadcast(self.G)
        print(self.P, self.G)

        host_message = self.receive(self.host_client)
        print(host_message)
        joining_message = self.receive(self.joining_client)
        print(joining_message)

        self.host_client.send(joining_message)
        self.joining_client.send(host_message)

        self.broadcast("Key exchange ended")

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
            if self.joining_client is not None and self.keys_exchanged is False:
                self.key_exchange()
                self.keys_exchanged = True
            else:
                self.handle()