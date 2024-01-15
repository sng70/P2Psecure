class Chatroom:
    def __init__(self):
        clients = self.clients
        key = self.key

    def brodcast(self, message):
        for client in clients:
            client.send(message)
