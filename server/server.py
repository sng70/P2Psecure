import socket
import threading
import time

from chatroom import Chatroom


class Server:
    def __init__(self, ip, port):
        self.chatrooms = {}
        self.ip = ip
        self.port = port

        self.P = 27777429566373324587264087881787744635148847837947480265503504392131230442085943091117462374042472351645725953762454843569398261639383028505573699606810253824585125479836591327666957349446110212135244959712004228201218454416852949570387131172573093777126418032329157955486358123199448465056197387962471540492125795323510417772286740451800566510613528534449126199972603888561933440004979792491365754836149741356084713755418090606249294667516993484001943287067450611428391345613890960878844348688550642531356077565139744934294677382089271043243165372762615339004964647202051592157533456445170384743445885973175897281077
        self.G = 6960309791228771387482348131365428561376786321843013461991848453878667267791308326230224780897195448428330870174033742333622275038476042037159851284601835051034114119882086730057240391106065275833019914191804974933185214407469756775110830900386470582731501629008211413795981079191803165043647422706932081492781534246098501748354210388108857361607183141538621206508604041787256014947208637968134541819698343272864043622509404022566936566721588810581732868423147107876893350330329579623021463172447552493637286063433979489669515370171579902514966537105942425093172408020466778558478904854385257912648376128363141508157

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

    def handle_client(self, client):
        time.sleep(10)
        self.write("Welcome to the chat server! Do you want to create or join a chatroom? (create/join) ", client)
        choice = self.receive(client)

        if choice.lower() == "create":
            self.write("Enter chatroom name: ", client)
            chatroom_name = self.receive(client)

            chatroom = self.create_chatroom(chatroom_name, client, self.P, self.G)
            self.write(f"Chatroom '{chatroom_name}' created", client)
            chatroom.start_chatroom_logic()

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