import tkinter as tk
from tkinter import messagebox, simpledialog
import socket
import ipaddress
import ssl
import json
import threading
import queue

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
        self.server_ip_text = tk.StringVar() 
        self.server_ip_text.set("192.168.0.204") 
        self.server_ip_entry = tk.Entry(self,textvariable=self.server_ip_text)
        self.server_ip_entry.grid(row=0, column=1, padx=5, pady=5)

        self.username_label = tk.Label(self, text="Username:")
        self.username_label.grid(row=1, column=0, padx=5, pady=5)
        self.username_text = tk.StringVar() 
        self.username_text.set("ariel") 
        self.username_entry = tk.Entry(self,textvariable=self.username_text)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)

        self.password_label = tk.Label(self, text="Password:")
        self.password_label.grid(row=2, column=0, padx=5, pady=5)
        self.password_text = tk.StringVar() 
        self.password_text.set("1234")
        self.password_entry = tk.Entry(self, show="*",textvariable=self.password_text)
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

        self.nav_bar = tk.Frame(self)
        self.nav_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.leave_btn=tk.Button(self.nav_bar,text="leave",command=self.Leave_Sess)
        self.leave_btn.pack(side=tk.LEFT)

        self.join_btn=tk.Button(self.nav_bar,text="join",command=self.Join_Sess)
        self.join_btn.pack(side=tk.RIGHT)

        self.create_btn=tk.Button(self.nav_bar,text="create",command=self.Create_Sess)
        self.create_btn.pack(side=tk.RIGHT)

    def Update_list(self,sList:dict):
        self.listbox.delete(0,tk.END)
        for item in sList:
            session=','.join([str(item[0]),str(item[1])])
            self.listbox.insert(tk.END,session)

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
        self.client_socket=None

        self.CustomEventsHandlers = {
            "event_wait":None,
            "user_list": self.update_user_list,
            "session_list": self.update_session_list,
            "shape_list": self.update_shape_list,
            "echo_text":self.update_echo_text
        }
        # Queue for inter-thread communication
        self.msg_queue = queue.Queue()
        self.bind("<<Messages2Queue>>",self.ProcessMessagesFromQueue)
        self.create_widgets()
        self.log_message("Welcome")
        self.protocol("WM_DELETE_WINDOW", self.close_window)
    
    def close_window(self):
        if self.client_socket is not None:
            self.client_socket.close()
        self.quit()

    def create_widgets(self):
        # Navigation bar
        self.nav_bar = tk.Frame(self)
        
        self.login_btn = tk.Button(self.nav_bar, text="login", command=self.open_login_dialog)
        self.login_btn.pack(side=tk.LEFT)

        self.disconnect_btn = tk.Button(self.nav_bar, text="Disconnect", command=self.disconnect_from_server)
        self.disconnect_btn.configure(state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT)

        self.load_btn = tk.Button(self.nav_bar, text="Load File", command=self.load_file)
        self.load_btn.pack(side=tk.RIGHT)

        self.save_btn = tk.Button(self.nav_bar, text="Save File", command=self.save_file)
        self.save_btn.pack(side=tk.RIGHT)
        self.nav_bar.pack(side=tk.TOP, fill=tk.X)


        # Main frame divided into three areas
        self.main_frame = tk.Frame(self)#,borderwidth = 10, relief = 'ridge')
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        self.main_left_frame=tk.Frame(self.main_frame)#, borderwidth = 10, relief = 'ridge')
        self.user_list_label=tk.Label(self.main_left_frame,text="user list")
        self.user_list_label.pack(side=tk.TOP)
        self.user_list=tk.Listbox(self.main_left_frame)
        self.user_list.pack(expand=True,fill=tk.BOTH)
        self.main_left_frame.pack(side=tk.LEFT,fill=tk.Y)
        
        self.main_right_frame=tk.Frame(self.main_frame)#, borderwidth = 10, relief = 'ridge')
        self.session_list_widget=SessionListFrame(self.main_right_frame)
        self.session_list_widget.pack(expand=True, fill=tk.BOTH)
        self.main_right_frame.pack(side=tk.RIGHT,fill=tk.Y)

        self.main_center_frame=tk.Frame(self.main_frame)#, borderwidth = 10, relief = 'ridge')
        self.main_center_frame.pack(expand=True,fill=tk.BOTH)
        self.canvas=DrawCanvas(self.main_center_frame)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        

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

    def update_user_list(self,user_list:dict):
        pass
    def update_session_list(self,session_list:dict):
        self.session_list_widget.Update_list(session_list)
    def update_shape_list(self,shape_list:dict):
        pass
    def update_echo_text(self,echo_text:str):
        self.log_message(echo_text)
        pass

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

                self.response_event=threading.Event()

                receive_thread = threading.Thread(target=self.receive_messages)
                self.threads.append(receive_thread)
                receive_thread.start()
                
                message=','.join(["login",str(username),str(password)])
                self.CustomEventsHandlers["event_wait"] = self.getsessionList
                self.client_socket.send(message.encode('utf-8'))
                
        else:
            messagebox.showinfo("Connect", "Connection cancelled")

    def getsessionList(self,dummy_data):
        self.CustomEventsHandlers["event_wait"]=None
        message="print_sessions"
        print("send print_session")
        self.client_socket.send(message.encode('utf-8'))
    def getuserList(self,dummy_data):
        self.CustomEventsHandlers["event_wait"]=None        
        message="print_users"
        print("send print_users")
        self.client_socket.send(message.encode('utf-8'))

    def disconnect_from_server(self):
        if self.client_socket is not None:
            self.client_socket.close()
        self.disconnect_btn.configure(state=tk.DISABLED)
        self.login_btn.configure(state=tk.ACTIVE)

    def load_file(self):
        pass

    def save_file(self):
        pass

    def send_command(self):
        pass

    def event_wait(self):
        pass
    def ProcessMessagesFromQueue(self, event):
        print("ProcessMessagesFromQueue")
        try:
            whole_msg = self.msg_queue.get_nowait()
            for msg_type,data in  whole_msg.items():    
                if self.CustomEventsHandlers[msg_type] is not None:           
                    self.CustomEventsHandlers[msg_type](data)
        except Exception as e:
            print("Error get message from queue:", e)


    def log_message(self,message):
        print(message)
        self.response_log.configure(state="normal")
        self.response_log.insert(tk.END, message + "\n")
        # Automatically scroll to the bottom
        self.response_log.see(tk.END)
        self.response_log.update()
        self.response_log.update_idletasks()
        self.response_log.configure(state="disabled")
        
    def receive_messages(self):
        while True:
            try:
                # Receive message from server
                print("Start wait for response")
                jMessage = self.client_socket.recv(1024).decode('utf-8')
                if jMessage:
                    message=json.loads(jMessage)
                    self.msg_queue.put({"echo_text":message["message"]})
                    print("event_generate echo ")
                    self.event_generate("<<Messages2Queue>>")
                    if message["data"] is not None:
                        if(type(message["data"]) is dict):
                            for index in message["data"]:
                                data=message["data"][index]
                                self.log_message(f"[{index}]:{data}")
                        else:
                            for data in message["data"]:
                                self.log_message(data)
                        self.msg_queue.put({message["data"]["datatype"]:message["data"]["content"]})
                        print("event_generate data ")
                        self.event_generate("<<Messages2Queue>>")
                print("before SetEvent")
                self.msg_queue.put({"event_wait":None})
                self.event_generate("<<Messages2Queue>>")
                print("after SetEvent")
            except Exception as e:
                print("Error receiving message:", e)
                break


if __name__ == "__main__":
    app = GUI()
    app.mainloop()
