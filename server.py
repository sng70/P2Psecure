import socket
import threading
import time

from chatroom import Chatroom


class Server:
    def __init__(self, ip, port):
        self.chatrooms = {}
        self.ip = ip
        self.port = port

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

    def handle_client(self, client_socket):
        self.write("Fuck you", client_socket)
        time.sleep(10)
        self.write(
            "Welcome to the chat server! Do you want to create or join a chatroom? (create/join) ",
            client_socket
        )
        choice = self.receive(client_socket)
        print(choice)

        if choice == "create":
            self.write("Enter chatroom name: ", client_socket)
            chatroom_name = self.receive(client_socket)

            P = "12345678901234567890123456789012"
            G = "2"

            chatroom = self.create_chatroom(chatroom_name, client_socket, P, G)
            self.write(f"Chatroom '{chatroom_name}' created", client_socket)
            chatroom.run()
        elif choice.lower() == "join":
            self.chatroom_list(client_socket)
            self.write("Enter the name of the chatroom you want to join: ", client_socket)
            chatroom_name = self.receive(client_socket)

            if chatroom_name in self.chatrooms:
                chatroom = self.chatrooms[chatroom_name]

                if chatroom.joining_client is not None:
                    chatroom.joining_client = client_socket
                    chatroom.clients[1] = client_socket
                    self.write(f"Joined {chatroom_name}", client_socket)
                else:
                    self.write("Failed to connect", client_socket)
            else:
                self.write(f"Chatroom '{chatroom_name}' does not exist.", client_socket)
        else:
            self.write("Invalid choice", client_socket)

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.port))
        server_socket.listen(5)

        print("Server is waiting.... :3")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connected from {addr}")

            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()


Server("localhost", 9090).start()
