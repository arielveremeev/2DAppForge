import tkinter as tk
from tkinter import messagebox, simpledialog
import socket
import ipaddress
import ssl
import json
import threading

class ConnectDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)

        self.callback = callback

        self.title("Connect to Server")

        # Get the main window position
        parent_pos_x = parent.winfo_rootx()
        parent_pos_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        # Calculate the position of the dialog to be in the center of the main window
        dialog_width = 200
        dialog_height = 150
        dialog_pos_x = parent_pos_x + (parent_width - dialog_width) // 2
        dialog_pos_y = parent_pos_y + (parent_height - dialog_height) // 2

        # Set the geometry of the dialog to be in the center of the main window
        self.geometry(f"{dialog_width}x{dialog_height}+{dialog_pos_x}+{dialog_pos_y}")

        self.server_ip_label = tk.Label(self, text="Server IP:")
        self.server_ip_label.grid(row=0, column=0, padx=5, pady=5)
        self.server_ip_entry = tk.Entry(self)
        self.server_ip_entry.grid(row=0, column=1, padx=5, pady=5)

        self.username_label = tk.Label(self, text="Username:")
        self.username_label.grid(row=1, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)

        self.password_label = tk.Label(self, text="Password:")
        self.password_label.grid(row=2, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)

        self.ok_button = tk.Button(self, text="OK", command=self.on_ok)
        self.ok_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        self.cancel_button = tk.Button(self, text="Cancel", command=self.on_cancel)
        self.cancel_button.grid(row=3, column=1, columnspan=2, padx=5, pady=5)

        self.result = None
        self.ok_clicked = False
        #self.center_window()


    def on_ok(self):
        server_ip = self.server_ip_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if server_ip and username and password:
            self.result = (server_ip, username, password)
            self.ok_clicked = True
            self.callback(self.result)
            self.destroy()

    def on_cancel(self):
        self.destroy()


class SessionListFrame(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self, parent)
        self.label=tk.Label(self,text="session list")
        self.label.pack(side=tk.TOP)
        
        self.listbox=tk.Listbox(self)
        self.listbox.pack(expand=True,fill=tk.BOTH)

        self.leave_btn=tk.Button(self,text="leave",command=self.Leave_Sess)
        self.leave_btn.pack(side=tk.BOTTOM)

        self.join_btn=tk.Button(self,text="join",command=self.Join_Sess)
        self.join_btn.pack(side=tk.BOTTOM)

        self.create_btn=tk.Button(self,text="create",command=self.Create_Sess)
        self.create_btn.pack(side=tk.BOTTOM)


    def Leave_Sess(self):
        pass
    def Join_Sess(self):
        pass
    def Create_Sess(self):
        pass


class DrawCanvas(tk.Canvas):
    def __init__(self,parent):
        tk.Canvas.__init__(self,parent,bg="white")

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("2DAppForge")
        self.geometry("800x600")

        self.threads=[]

        self.create_widgets()
    
    def create_widgets(self):
        # Navigation bar
        self.nav_bar = tk.Frame(self)
        self.nav_bar.pack(side=tk.TOP, fill=tk.X)

        self.login_btn = tk.Button(self.nav_bar, text="login", command=self.open_login_dialog)
        self.login_btn.pack(side=tk.LEFT)

        self.disconnect_btn = tk.Button(self.nav_bar, text="Disconnect", command=self.disconnect_from_server)
        self.disconnect_btn.configure(state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT)

        self.load_btn = tk.Button(self.nav_bar, text="Load File", command=self.load_file)
        self.load_btn.pack(side=tk.RIGHT)

        self.save_btn = tk.Button(self.nav_bar, text="Save File", command=self.save_file)
        self.save_btn.pack(side=tk.RIGHT)

        # Main frame divided into three areas
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        self.main_left_frame=tk.Frame(self.main_frame)
        self.user_list_label=tk.Label(self.main_left_frame,text="user list")
        self.user_list_label.pack(side=tk.TOP)
        self.user_list=tk.Listbox(self.main_left_frame)
        self.user_list.pack(expand=True,fill=tk.BOTH)
        self.main_left_frame.pack(side=tk.LEFT,expand=True,fill=tk.Y)

        self.main_center_frame=tk.Frame(self.main_frame)
        self.canvas=DrawCanvas(self.main_center_frame)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.main_center_frame.pack(expand=True,fill=tk.BOTH)

        self.main_right_frame=tk.Frame(self.main_frame)
        self.session_list_widget=SessionListFrame(self.main_right_frame)
        self.session_list_widget.pack(expand=True, fill=tk.BOTH)
        self.main_right_frame.pack(side=tk.RIGHT,expand=True,fill=tk.Y)

        # Command prompt
        self.command_frame = tk.Frame(self)
        self.command_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.response_log=tk.Text(self.command_frame , state="disabled" , wrap="word",height=5)
        self.response_log.pack(fill="x",expand=True)

        self.command_label = tk.Label(self.command_frame, text="Command:")
        self.command_label.pack(side=tk.LEFT)

        self.command_entry = tk.Entry(self.command_frame)
        self.command_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.send_btn = tk.Button(self.command_frame, text="Send", command=self.send_command)
        self.send_btn.pack(side=tk.LEFT)

    def open_login_dialog(self):
        dialog = ConnectDialog(self, self.on_connect)
        dialog.grab_set()  # Make the dialog modal
        self.wait_window(dialog)
        if dialog.ok_clicked:
            self.login_btn.configure(state=tk.DISABLED)
            self.disconnect_btn.configure(state=tk.ACTIVE)
        else:
            self.login_btn.configure(state=tk.NORMAL)
            self.disconnect_btn.configure(state=tk.DISABLED)

    def on_connect(self, credentials):
        if credentials:
            server_ip, username, password = credentials
            
            port=1234

            if(server_ip is not None):
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE

                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((str(server_ip), port))
                self.client_socket =  context.wrap_socket(client_socket, server_hostname=str(server_ip))

                event=threading.Event()

                receive_thread = threading.Thread(target=self.receive_messages, args=(event,))
                receive_thread.start()
                self.threads.append(receive_thread)

                message=','.join(["login",str(username),str(password)])
                self.client_socket.send(message.encode('utf-8'))
            #messagebox.showinfo("Connect", f"Connecting to server {server_ip} as {username} with password {password}")
            # Here you can add the code to connect to the server with the provided credentials
        else:
            messagebox.showinfo("Connect", "Connection cancelled")

    def disconnect_from_server(self):
        self.disconnect_btn.configure(state=tk.DISABLED)
        self.login_btn.configure(state=tk.ACTIVE)

    def load_file(self):
        pass

    def save_file(self):
        pass

    def send_command(self):
        pass

    def log_message(self,message):
        self.response_log.configure(state="normal")
        self.response_log.insert(tk.END, message + "\n")
        # Automatically scroll to the bottom
        self.response_log.see(tk.END)
        self.response_log.configure(state="disabled")

    def receive_messages(self,event):
        while True:
            try:
                # Receive message from server
                jMessage = self.client_socket.recv(1024).decode('utf-8')
                if jMessage:
                    message=json.loads(jMessage)
                    self.log_message(message["message"])
                    if message["data"] is not None:
                        if(type(message["data"]) is dict):
                            for index in message["data"]:
                                data=message["data"][index]
                                self.log_message(f"[{index}]:{data}")
                        else:
                            for data in message["data"]:
                                self.log_message(data)

            except Exception as e:
                print("Error receiving message:", e)
                break


if __name__ == "__main__":
    app = GUI()
    app.mainloop()
