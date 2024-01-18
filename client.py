import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog


HOST = "127.0.0.1"
PORT = 9090

class Client:

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        msg = tkinter.Tk()
        msg.withdraw()

        self.nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg)
        self.private_key = simpledialog.askstring("Private_key", "Please insert your private key", parent=msg)

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="black")

        # Chat label
        self.chat_label = tkinter.Label(self.win, bg="black", fg="red", font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        # ScrolledText for chat messages
        self.text_area = tkinter.scrolledtext.ScrolledText(self.win, bg="black", fg="green", font=("Arial", 12))
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        # Message label
        self.msg_label = tkinter.Label(self.win, bg="black", fg="white", font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        # Text area for user input
        self.input_area = tkinter.Text(self.win, height=3, bg="black", fg="green", font=("Arial", 12))
        self.input_area.pack(padx=20, pady=5)

        # Send button
        self.send_button = tkinter.Button(self.win, text="Send", command=self.write, bg="black", fg="green", font=("Arial", 15))
        self.send_button.pack(padx=20, pady=5)

        self.gui_done = True

        # Set protocol for closing window
        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def create_header(self, message):
        header = f"{len(message):<5}"
        return header

    def encrypt_message(self, message, key):
        #AES(message, key)
        pass

    def decrypt_message(self, message, key):
        pass

    def write(self):
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"

        header = self.create_header(message)

        self.sock.send(header.encode('utf-8'))
        self.sock.send(message.encode('utf-8'))

        self.input_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024)
                if message.decode('utf-8') == 'NICK':
                    self.sock.send(self.nickname.encode('utf-8'))
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message.decode('utf-8'))
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except Exception as e:
                print(f"Error: {e}")
                self.socket.send("Connection ended".encode('utf-8'))
                self.sock.close()
                break

client = Client(HOST, PORT)