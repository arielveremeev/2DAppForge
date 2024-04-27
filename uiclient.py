import tkinter as tk
from tkinter import messagebox
import socket
import ipaddress
import ssl
import json
import threading

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

        self.create_widgets()
    
    def create_widgets(self):
        # Navigation bar
        self.nav_bar = tk.Frame(self)
        self.nav_bar.pack(side=tk.TOP, fill=tk.X)

        self.login_btn = tk.Button(self.nav_bar, text="login", command=self.open_login_dialog)
        self.login_btn.pack(side=tk.LEFT)

        self.disconnect_btn = tk.Button(self.nav_bar, text="Disconnect", command=self.disconnect_from_server)
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
        pass

    def disconnect_from_server(self):
        pass

    def load_file(self):
        pass

    def save_file(self):
        pass

    def send_command(self):
        pass

if __name__ == "__main__":
    app = GUI()
    app.mainloop()
