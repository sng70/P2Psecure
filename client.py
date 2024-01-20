import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog

import cryptography.hazmat.primitives.ciphers
from cryptography.hazmat.primitives.asymmetric import dh

import os

HOST = "127.0.0.1"
PORT = 9090


class Client:

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        msg = tkinter.Tk()
        msg.withdraw()

        self.nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg)
        self.private_key = dh.generate_parameters(generator=2, key_size=2048).generate_private_key()
        self.shared_secret = None
        self.keys_exchanged = False

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="black")

        self.chat_label = tkinter.Label(self.win, bg="black", fg="red", font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win, bg="black", fg="green", font=("Arial", 12))
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.msg_label = tkinter.Label(self.win, bg="black", fg="white", font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3, bg="black", fg="green", font=("Arial", 12))
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write, bg="black", fg="green", font=("Arial", 15))
        self.send_button.pack(padx=20, pady=5)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def create_header(self, message):
        header = f"{len(message):<5}"
        return header

    def generate_iv(self):
        return os.urandom(16)

    def receive_message(self):
        message_len = int(self.sock.recv(5).decode("utf-8"))
        message = self.sock.recv(message_len)

        if len(message) != message_len:
            self.sock.send("Error while receiving the message".encode('utf-8'))
        else:
            if self.keys_exchanged:
                iv = message[:16]
                message = message[16:]
                self.decrypt_message(message, self.shared_secret) #3rd argument = iv

                return message.decode('utf-8')

            return message.decode("utf-8")

    def encrypt_message(self, message, key):
        key = key.encode('utf-8')
        message = message.encode('utf-8')

        cipher = cryptography.hazmat.primitives.ciphers.Cipher(cryptography.hazmat.primitives.ciphers.algorithms.AES(key), cryptography.hazmat.primitives.ciphers.modes.CFB8())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(message) + encryptor.finalize()

        return ciphertext

    def decrypt_message(self, message, key):
        key = key.encode('utf-8')

        cipher = cryptography.hazmat.primitives.ciphers.Cipher(cryptography.hazmat.primitives.ciphers.algorithms.AES(key), cryptography.hazmat.primitives.ciphers.modes.CFB8())
        decryptor = cipher.decryptor()

        try:
            decrypted_message = decryptor.update(message) + decryptor.finalize()
            return decrypted_message.decode('utf-8')
        except:
            return "Decryption failed"

    def write(self):
        message = f"{self.input_area.get('1.0', 'end')}"

        if self.keys_exchanged:
            message = f"{self.nickname}: + {message}".encode('utf-8')
            iv = self.generate_iv()
            message = iv + message

            header = self.create_header(message)

            self.sock.send(header.encode('utf-8'))
            self.sock.send(self.encrypt_message(message.encode('utf-8'), self.shared_secret) + iv)
        else:
            header = self.create_header(message)

            self.sock.send(header.encode('utf-8'))
            self.sock.send(message.encode('utf-8'))

        self.input_area.delete('1.0', 'end')

    def write_message(self, message):
        header = self.create_header(message)

        self.sock.send(header.encode('utf-8'))
        self.sock.send(message.encode('utf-8'))

    def key_exchange(self):
        P = self.receive_message()
        G = self.receive_message()

        public_key = pow(int(G), int(self.private_key), int(P))
        self.write_message(str(public_key))

        bob_key = int(self.receive_message())

        self.shared_secret = pow(bob_key, int(self.private_key), int(P))


    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        while self.running:
            try:
                message = self.receive_message()

                if message == "Diffie-Helman":
                    self.key_exchange()
                    self.keys_exchanged = True
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message)
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except Exception as e:
                print(f"Error: {e}")
                self.sock.send("Connection ended".encode('utf-8'))
                self.sock.close()
                break


client = Client(HOST, PORT)