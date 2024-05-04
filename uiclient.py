import tkinter as tk
from tkinter import ttk
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

class CreateSessDialog(tk.Toplevel):
    def __init__(self,parent,callback):
        super().__init__(parent)

        self.callback=callback

        self.title("create session")

        self.sess_name = tk.Label(self, text="Enter session name")        
        self.sess_name.pack(pady=5)
        self.sess_name_text=tk.StringVar()
        self.sess_name_text.set("test")
        self.name_entry = tk.Entry(self,textvariable=self.sess_name_text)
        self.name_entry.pack(pady=5)

        self.max_part = tk.Label(self, text="Enter max amount of participants")
        self.max_part.pack(pady=5)
        self.sess_maxpart_text=tk.StringVar()
        self.sess_maxpart_text.set("15")
        self.max_entry = tk.Entry(self,textvariable=self.sess_maxpart_text)
        self.max_entry.pack(pady=5)

        
        self.create_button = tk.Button(self, text="Create session", command=self.on_Create)
        self.create_button.pack(side=tk.LEFT,padx=10, pady=10)
        self.cancel_button = tk.Button(self, text="Cancel", command=self.on_cancel)
        self.cancel_button.pack(side=tk.RIGHT,padx=10, pady=10)

        self.result=None
        self.create_clicked=False

    def on_Create(self):
        name = self.name_entry.get()
        maxpart = self.max_entry.get()
        print(name)
        print(maxpart)
        if name and maxpart:
            self.result=(name,maxpart)
            self.create_clicked=True
            self.callback["on_create_session"](self.result)
            self.destroy()

    def on_cancel(self):
        self.destroy()

class SessionListFrame(ttk.Frame):
    def __init__(self,parent,callbacks):
        ttk.Frame.__init__(self, parent)

        self.callbacks=callbacks

        self.current_sess=""

        self.label=ttk.Label(self,text="session list")
        self.label.pack(side=tk.TOP)
        
        self.listbox=tk.Listbox(self)
        self.listbox.pack(expand=True,fill=tk.BOTH)
        self.listbox.bind("<ButtonRelease-1>", self.on_select)
        self.listbox.bind("<Double-Button-1>", self.on_double_click)

        self.nav_bar = ttk.Frame(self)
        self.nav_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.leave_btn=ttk.Button(self.nav_bar,text="leave",command=self.Leave_Sess)
        self.leave_btn.configure(state=tk.DISABLED)
        self.leave_btn.pack(side=tk.LEFT)

        self.join_btn=ttk.Button(self.nav_bar,text="join",command=self.open_join_sess_dialog)
        self.join_btn.configure(state=tk.DISABLED)
        self.join_btn.pack(side=tk.RIGHT)

        self.create_btn=ttk.Button(self.nav_bar,text="create",command=self.open_create_sess_dialog)
        self.create_btn.pack(side=tk.RIGHT)

    def on_select(self,event):
        if self.listbox.curselection():
            self.join_btn.config(state=tk.NORMAL)
        else:
            self.join_btn.config(state=tk.DISABLED)

    def on_double_click(self,event):
        if self.listbox.curselection():
            self.open_join_sess_dialog()
        else:
            pass


    def Update_list(self,sList:dict):
        self.listbox.delete(0,tk.END)
        for item in sList:
            session=','.join([str(item[0]),str(item[1])])
            self.listbox.insert(tk.END,session)

    def open_create_sess_dialog(self):
        dialog=CreateSessDialog(self,self.callbacks)
        dialog.grab_set()
        self.wait_window(dialog)

    def open_join_sess_dialog(self):
        seleceted_sess=self.listbox.get(self.listbox.curselection())
        if(seleceted_sess):
            details=seleceted_sess.split(',')
            self.current_sess=details[0]
            self.callbacks["on_join_session"](self.current_sess)
            self.leave_btn.configure(state=tk.ACTIVE)
            self.join_btn.configure(state=tk.DISABLED)
            self.create_btn.configure(state=tk.DISABLED)
        else:
            pass
        
    
    def Leave_Sess(self):
        if self.current_sess != "":
            self.callbacks["on_leave_session"]()

            self.leave_btn.configure(state=tk.DISABLED)
            self.join_btn.configure(state=tk.ACTIVE)
            self.create_btn.configure(state=tk.ACTIVE)
            self.current_sess=""

class Shape_List_frame(ttk.Frame):
    def __init__(self,parent,callbacks):
        ttk.Frame.__init__(self, parent)

        self.callbacks=callbacks

        self.label=ttk.Label(self,text="shape list")
        self.label.pack(side=tk.TOP)
        
        self.listbox=tk.Listbox(self)
        self.listbox.pack(expand=True,fill=tk.BOTH)
        #self.listbox.bind("<ButtonRelease-1>", self.on_select)

        self.nav_bar = ttk.Frame(self)
        self.nav_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.add_btn=ttk.Button(self.nav_bar,text="add shape",command=self.add_shape)
        self.add_btn.pack(side=tk.LEFT)

        self.remove_btn=ttk.Button(self.nav_bar,text="remove shape",command=self.remove_shape)
        self.remove_btn.pack(side=tk.RIGHT)

    def add_shape(self):
        pass

    def remove_shape(self):
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
        self.verbose=tk.BooleanVar()

        self.CustomEventsHandlers = {
            "event_wait":None,
            "user_list": self.update_user_list,
            "session_list": self.update_session_list,
            "shape_list": self.update_shape_list,
            "echo_text":self.update_echo_text
        }

        self.SessionHandlers={
            "on_create_session":self.on_create_session,
            "on_join_session":self.on_join_session,
            "on_leave_session":self.on_leave_session
        }
        # Queue for inter-thread communication
        self.msg_queue = queue.Queue()
        self.bind("<<Messages2Queue>>",self.ProcessMessagesFromQueue)
        self.create_widgets()
        self.log_message("Welcome")
        self.protocol("WM_DELETE_WINDOW", self.close_window)
    
    def close_window(self):
        if self.client_socket is not None:
            self.CustomEventsHandlers["event_wait"] = self.on_close
            self.client_socket.close()
        else:
            self.quit()
    def on_close(self,_):
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
        
        self.rightnotebook=ttk.Notebook(self.main_frame)
        self.session_list_widget=SessionListFrame(self.rightnotebook,self.SessionHandlers)
        self.session_list_widget.pack(expand=True, fill=tk.BOTH)
        self.rightnotebook.add(self.session_list_widget,text="session list")

        self.shape_list_widget=Shape_List_frame(self.rightnotebook,self.SessionHandlers)
        self.shape_list_widget.pack(expand=True, fill=tk.BOTH)
        self.rightnotebook.add(self.shape_list_widget,text="shape list")

        self.rightnotebook.pack(side=tk.RIGHT,fill=tk.Y)

        #self.main_right_frame=tk.Frame(self.main_frame)#, borderwidth = 10, relief = 'ridge')
        #self.session_list_widget=SessionListFrame(self.main_right_frame,self.SessionHandlers)
        #self.session_list_widget.pack(expand=True, fill=tk.BOTH)
        #self.main_right_frame.pack(side=tk.RIGHT,fill=tk.Y)

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

        self.verbose.set(False)
        self.verbose_btn=tk.Checkbutton(self.command_frame,text="verbose",variable=self.verbose,onvalue=True,offvalue=False, command=self.on_verbose)
        self.verbose_btn.pack(side=tk.LEFT)

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
    
    def on_create_session(self,sess_details):
        if(self.client_socket is not None and sess_details):
            name,maxpart=sess_details
            message=','.join(["create_session",name,maxpart])
            self.client_socket.send(message.encode('utf-8'))

        else:
            pass

    def on_join_session(self,sessname):
        if(self.client_socket is not None and sessname):
            message=','.join(["join_session",sessname])
            self.client_socket.send(message.encode('utf-8'))
        else:
            pass

    def on_leave_session(self):
        if(self.client_socket is not None):
            message=','.join(["exit_session"])
            self.client_socket.send(message.encode('utf-8'))
        else:
            pass

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

    def on_verbose(self):
        if(self.verbose.get()):
            self.log_message("verbose turned on")
        else:
            self.log_message("verbose turned off")

    def send_command(self):
        pass

    def event_wait(self):
        pass
    def ProcessMessagesFromQueue(self, event):
        print("ProcessMessagesFromQueue")
        size=self.msg_queue.qsize()
        try:
            for msg in range(size):
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
                    if (message["data"] is not None):
                        if(self.verbose.get()):
                            if(type(message["data"]) is dict):
                                for index in message["data"]:
                                    data=message["data"][index]
                                    msg="[" + str(index) + "]" + ":" + str(data)
                                    self.msg_queue.put({"echo_text" : msg})
                            else:
                                for data in message["data"]:
                                    self.msg_queue.put({"echo_text" : data})
                        self.msg_queue.put({message["data"]["datatype"]:message["data"]["content"]})
                        print("event_generate data ")
                else:
                    self.msg_queue.put({"echo_text":"server disconected"})
                    self.msg_queue.put({"event_wait":None})
                    self.event_generate("<<Messages2Queue>>")
                    self.client_socket.close()
                    self.client_socket = None
                    break

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
