import customtkinter
from server import Server

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.geometry("500x500")
root.title("Server setup")

def popup(text):
    popup = customtkinter.CTk()
    popup.geometry("200x50")
    popup.title(text)

    label = customtkinter.CTkLabel(master=popup, text=text, font=("Arial", 15))
    label.pack(pady=10, padx=5)

    popup.mainloop()

def server_setup():
    try:
        Server(entry1.get(), int(entry2.get())).start()
        popup("Server started")
    except:
        popup("Error while starting server")


frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

label = customtkinter.CTkLabel(master=frame, text="Server setup", font=("Arial", 20))
label.pack(pady=15, padx=20)

entry1 = customtkinter.CTkEntry(master=frame, placeholder_text="Enter server IP address", font=("Arial", 15))
entry1.pack(pady=12, padx=10)

entry2 = customtkinter.CTkEntry(master=frame, placeholder_text="Enter server Port", font=("Arial", 15))
entry2.pack(pady=12, padx=10)

button = customtkinter.CTkButton(master=frame, text="Start server", font=("Arial", 15), command=server_setup)
button.pack(pady=12, padx=10)

root.mainloop()
