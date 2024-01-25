import socket
import threading
import time

from chatroom import Chatroom


class Server:
    def __init__(self, ip, port):
        self.chatrooms = {}
        self.ip = ip
        self.port = port

        self.P = 321
        self.G = 2

    def receive(self, client):
        message_len = int(client.recv(5).decode("utf-8"))
        message = client.recv(message_len)

        if len(message) != message_len:
            self.write("Error while receiving the message", client)
        else:
            return message.decode("utf-8").strip("\n")

    def create_header(self, message):
        header = f"{len(message):<5}"
        return header

    def write(self, message, client):
        message += '\n'
        header = self.create_header(message)

        client.send(header.encode('utf-8'))
        client.send(message.encode('utf-8'))

    def create_chatroom(self, chatroom_name, host_client, P, G):
        chatroom = Chatroom(chatroom_name, host_client, P, G)
        self.chatrooms[chatroom_name] = chatroom
        return chatroom

    def chatroom_list(self, client):
        chatroom_names = list(self.chatrooms.keys())
        for chatroom in chatroom_names:
            self.write(chatroom, client)

    def pass_message(self, message, client):
        pass

    def handle_client(self, client):
        time.sleep(10)
        self.write("Welcome to the chat server! Do you want to create or join a chatroom? (create/join) ", client)
        choice = self.receive(client)

        if choice.lower() == "create":
            self.write("Enter chatroom name: ", client)
            chatroom_name = self.receive(client)

            chatroom = self.create_chatroom(chatroom_name, client, self.P, self.G)
            self.write(f"Chatroom '{chatroom_name}' created", client)
            chatroom.run()

        elif choice.lower() == "join":
            self.chatroom_list(client)
            self.write("Enter the name of the chatroom you want to join: ", client)
            chatroom_name = self.receive(client)

            if chatroom_name in self.chatrooms:
                chatroom = self.chatrooms[chatroom_name]

                if chatroom.joining_client is None:
                    chatroom.joining_client = client
                    chatroom.clients[1] = client
                    self.write(f"Joined {chatroom_name}", client)
                else:
                    self.write("Failed to connect chatroom is full", client)
            else:
                self.write(f"Chatroom '{chatroom_name}' does not exist.", client)
        else:
            self.write("Invalid choice", client)

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.port))
        server_socket.listen(10)

        print("Server is waiting.... :3")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connected from {addr}")

            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()