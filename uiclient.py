import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
from tkinter import filedialog
from PIL import Image, ImageDraw
import socket
import ipaddress
import ssl
import json
import threading
import queue

from dialogs import ConnectDialog, LoadFileDialog, SaveFileDialog
from drawcanvas import DrawCanvas
from sessionlistframe import SessionListFrame
from shapelistframe import Shape_List_frame



class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("2DAppForge")
        self.geometry("800x600")

        self.threads=[]
        self.client_socket=None
        self.verbose=tk.BooleanVar()
        self.in_sess=False

        self.CustomEventsHandlers = {
            "event_wait":None,
            "user_list": self.update_user_list,
            "session_list": self.update_session_list,
            "shape_list": self.update_shape_list,
            "list_files": self.update_list_files,
            "echo_text":self.update_echo_text
        }

        self.SessionHandlers={
            "on_create_session":self.on_create_session,
            "on_join_session":self.on_join_session,
            "on_leave_session":self.on_leave_session,
            "on_load_file":self.on_load_file,
            "on_save_file":self.on_save_file
        }

        self.CanvasHandlers={
            "on_change_type":self.change_shape_type,
            "on_clear_canvas":self.on_clear_canvas,
            "on_shape_finish":self.send_new_shape,
            "on_delete_shape":self.delete_shape,
            "on_shape_select":self.select_shape,
            "on_change_draw":self.change_draw_type,
            "on_change_edit":self.change_edit_type,
            "on_shape_move":self.move_shape,
            "on_shape_scale":self.scale_shape,
            "on_shape_rotate":self.rotate_shape
        }

        # Queue for inter-thread communication
        self.msg_queue = queue.Queue()
        self.bind("<<Messages2Queue>>",self.ProcessMessagesFromQueue)
        self.create_widgets()
        self.log_message("Welcome")
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        self.storage_shapes = dict()
    
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
        
        self.login_btn = tk.Button(self.nav_bar, text="Connect", command=self.open_login_dialog)
        self.login_btn.pack(side=tk.LEFT)

        self.disconnect_btn = tk.Button(self.nav_bar, text="Disconnect", command=self.disconnect_from_server)
        self.disconnect_btn.configure(state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT)

        self.load_btn = tk.Button(self.nav_bar, text="Load File", command=self.load_file)
        self.load_btn.pack(side=tk.RIGHT)

        self.save_btn = tk.Button(self.nav_bar, text="Save File", command=self.open_save_file_dialog)
        self.save_btn.pack(side=tk.RIGHT)
        self.nav_bar.pack(side=tk.TOP, fill=tk.X)

        self.export_btn=tk.Button(self.nav_bar, text="export image",command=self.export_image)
        self.export_btn.pack(side=tk.RIGHT)
        self.nav_bar.pack(side=tk.TOP, fill=tk.X)


        # Main frame divided into three areas
        self.main_frame = tk.Frame(self)#,borderwidth = 10, relief = 'ridge')
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        self.main_left_frame=tk.Frame(self.main_frame)#, borderwidth = 10, relief = 'ridge')

        self.user_list_scrollbar=tk.Scrollbar(self.main_left_frame,orient=tk.VERTICAL)
        self.user_list_scrollbar.pack(side=tk.LEFT,fill=tk.Y)

        self.user_list_label=tk.Label(self.main_left_frame,text="user list")
        self.user_list_label.pack(side=tk.TOP)
        self.user_list=tk.Listbox(self.main_left_frame)
        self.user_list.pack(expand=True,fill=tk.BOTH)
        self.user_list.configure(yscrollcommand=self.user_list_scrollbar.set)
        self.user_list_scrollbar.configure(command=self.user_list.yview)
        self.main_left_frame.pack(side=tk.LEFT,fill=tk.Y)
        
        self.rightnotebook=ttk.Notebook(self.main_frame)
        self.session_list_widget=SessionListFrame(self.rightnotebook,self.SessionHandlers)
        self.session_list_widget.pack(expand=True, fill=tk.BOTH)
        self.rightnotebook.add(self.session_list_widget,text="session list")

        self.shape_list_widget=Shape_List_frame(self.rightnotebook,self.SessionHandlers,self.CanvasHandlers)
        self.shape_list_widget.pack(expand=True, fill=tk.BOTH)
        self.rightnotebook.add(self.shape_list_widget,text="shape list")

        self.rightnotebook.pack(side=tk.RIGHT,fill=tk.Y)

        #self.main_right_frame=tk.Frame(self.main_frame)#, borderwidth = 10, relief = 'ridge')
        #self.session_list_widget=SessionListFrame(self.main_right_frame,self.SessionHandlers)
        #self.session_list_widget.pack(expand=True, fill=tk.BOTH)
        #self.main_right_frame.pack(side=tk.RIGHT,fill=tk.Y)

        self.main_center_frame=tk.Frame(self.main_frame)#, borderwidth = 10, relief = 'ridge')
        self.main_center_frame.pack(expand=True,fill=tk.BOTH)
        self.canvas=DrawCanvas(self.main_center_frame,self.CanvasHandlers)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        

        # Command prompt
        self.command_frame = tk.Frame(self)
        self.command_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.response_log_scrollbar=tk.Scrollbar(self.command_frame,orient=tk.VERTICAL)
        self.response_log_scrollbar.pack(side=tk.RIGHT,fill=tk.Y)

        self.response_log=tk.Text(self.command_frame , state="disabled" , wrap="word",height=5)
        self.response_log.pack(fill="x",expand=True)
        self.response_log.configure(yscrollcommand=self.response_log_scrollbar.set)
        self.response_log_scrollbar.configure(command=self.response_log.yview)

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
        local_ip_as_default = socket.gethostbyname(socket.gethostname())
        dialog = ConnectDialog(self, local_ip_as_default,self.on_connect)
        dialog.grab_set()  # Make the dialog modal
        self.wait_window(dialog)        
            

    def open_save_file_dialog(self):
        dialog = SaveFileDialog(self)
        dialog.grab_set()  # Make the dialog modal
        self.wait_window(dialog)
        if dialog.save_clicked:
            self.on_save_file(dialog.result)

    def export_image(self):
        '''open FileDialog with tkinter to save the image'''
        filetypes = [("PNG files", "*.png"), ("All files", "*")]
        filename = filedialog.asksaveasfilename(title="Save image as...", filetypes=filetypes)
        if filename:
            if not filename.endswith(".png"):
                filename += ".png"
            image = self.canvas.CretaeSceenShotOfDraws()
            image.save(filename)

    def update_user_list(self,user_list):
        if user_list:
            self.user_list.delete(0,tk.END)
            for user in user_list:
                self.user_list.insert(tk.END,user)

    def update_session_list(self,session_list:dict):
        self.session_list_widget.Update_list(session_list)

    def update_shape_list(self,shape_list:dict):
        for Sid,details in shape_list.items():
            print(Sid)
            srvShapeId = int(Sid)
            if(srvShapeId in self.storage_shapes.keys()):
                self.canvas.edit_shape(self.storage_shapes[srvShapeId],details)
            else:
                self.shape_list_widget.Update_listSingle(srvShapeId,details)

                if srvShapeId < 0:
                    srvShapeId = -srvShapeId
                    if srvShapeId in self.storage_shapes.keys():
                        canvasId = self.storage_shapes.pop(srvShapeId)
                        print("from remove shape",canvasId)
                        self.canvas.remove_shape(canvasId)
                    self.update()
                else:               
                    # canvas may return list of ids
                    self.storage_shapes[srvShapeId] = self.canvas.add_shape(details)
                
        print("yes")
                

    def update_echo_text(self,echo_text:str):
        self.log_message(echo_text)
        pass

    

    def on_connect(self, credentials, isLogin=True):
        if credentials:
            server_ip, username, password = credentials
            
            port=1234

            if(server_ip is not None and self.client_socket is None):
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
                
                if isLogin:
                    message=','.join(["login",str(username),str(password)])
                    self.CustomEventsHandlers["event_wait"] = self.after_login
                    self.client_socket.send(message.encode('utf-8'))                                
                else:
                    message=','.join(["sign_up",str(username),str(password)])
                    self.CustomEventsHandlers["event_wait"] = self.after_sign_up
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
            self.shape_list_widget.Joined_sess()
            self.canvas.toggle_draw()
            message=','.join(["join_session",sessname])
            self.client_socket.send(message.encode('utf-8'))
            self.client_socket.send(("print_users,session").encode('utf-8'))
            self.in_sess=True
        else:
            pass

    def on_leave_session(self):
        if(self.client_socket is not None):
            message=','.join(["exit_session"])
            self.client_socket.send(message.encode('utf-8'))
            self.shape_list_widget.ListClear()
            self.canvas.on_clear(None)
            self.storage_shapes.clear()
        else:
            pass

    def on_load_file(self,filename):
        if(self.client_socket is not None and filename):
            message=','.join(["load_file",filename])
            self.client_socket.send(message.encode('utf-8'))
        else:
            pass

    def on_save_file(self,filename):
        if(self.client_socket is not None and filename):
            message=','.join(["save_file",filename])
            self.client_socket.send(message.encode('utf-8'))
        else:
            pass 

    def change_shape_type(self,shape):
        if shape:
            self.canvas.change_shape_type(shape)

    def change_draw_type(self,draw_type):
        if draw_type:
            self.canvas.change_draw_type(draw_type)
    
    def change_edit_type(self,edit_type):
        if edit_type:
            self.canvas.change_edit_type(edit_type)

    def move_shape(self,shapeId,moveX,moveY):
        if shapeId:
            servId=self.convert_canvas_2serv(shapeId)
        if (self.client_socket is not None and moveX and moveY and servId):
            message=",".join(["move_shape",str(servId),str(moveX),str(moveY)])
            self.client_socket.send(message.encode('utf-8'))
        else:
            pass
    
    def scale_shape(self,shapeId,scale_factor):
        if shapeId:
            servId=self.convert_canvas_2serv(shapeId)
        if (self.client_socket is not None and scale_factor and servId):
            message=",".join(["scale_shape",str(servId),str(scale_factor)])
            self.client_socket.send(message.encode('utf-8'))
        else:
            pass
    def rotate_shape(self,shapeId,rotate_factor):
        if shapeId:
            servId=self.convert_canvas_2serv(shapeId)
        if (self.client_socket is not None and rotate_factor and servId):
            message=",".join(["rotate_shape",str(servId),str(rotate_factor)])
            self.client_socket.send(message.encode('utf-8'))
        else:
            pass

    def on_clear_canvas(self):
        self.canvas.on_clear()

    def convert_canvas_2serv(self,Cid):
        for key,value in self.storage_shapes.items():
            if Cid == value :
                return key
        print("not found")

    def send_new_shape(self,shape):
        if (self.client_socket is not None and shape):
            message=",".join(["add_shape",str(shape)])
            self.client_socket.send(message.encode('utf-8'))
        else:
            pass
    
    def delete_shape(self,shapeid):
        if (self.client_socket is not None and shapeid):
            message=",".join(["delete_shape",str(shapeid)])
            self.client_socket.send(message.encode('utf-8'))
        else:
            pass
    def select_shape(self,servId):
        if servId:
            self.canvas.draw_shape_bb(self.storage_shapes[servId])


    def after_login(self,srv_responce):
        self.CustomEventsHandlers["event_wait"]=None
        if srv_responce["status"] == "success":         
            self.log_message("login successful")
            print("send print_session")
            self.client_socket.send("print_sessions".encode('utf-8'))
            self.client_socket.send(("print_users,all").encode('utf-8'))
            self.login_btn.configure(state=tk.DISABLED)
            self.disconnect_btn.configure(state=tk.ACTIVE)
        else:
            self.client_socket.close()
            self.client_socket=None
            self.log_message("login failed")
            self.login_btn.configure(state=tk.NORMAL)
            self.disconnect_btn.configure(state=tk.DISABLED)
    def after_sign_up(self,srv_responce):
        self.CustomEventsHandlers["event_wait"]=None
        if srv_responce["status"] == "success":
            self.log_message("sign up successful you can login")
        else:
            self.client_socket.close()
            self.client_socket=None
            self.log_message("sign up failed")            

    def disconnect_from_server(self):
        if self.client_socket is not None:
            self.client_socket.close()
            self.client_socket = None
        self.disconnect_btn.configure(state=tk.DISABLED)
        self.login_btn.configure(state=tk.ACTIVE)
        self.user_list.delete(0,tk.END)
        self.session_list_widget.Update_list({})
        self.shape_list_widget.ListClear()

    def load_file(self):
        self.dialog=LoadFileDialog(self,self.SessionHandlers)
        if(self.client_socket is not None):
            message=','.join(["list_files"])
            self.client_socket.send(message.encode('utf-8'))
        else:
            pass
        self.dialog.grab_set()
        self.wait_window(self.dialog)
        self.dialog = None
    def update_list_files(self,shape_list:dict):
        if self.dialog is not None:
            self.dialog.update_list(shape_list)

    def save_file(self):
        pass

    def on_verbose(self):
        if(self.verbose.get()):
            self.log_message("verbose turned on")
        else:
            self.log_message("verbose turned off")

    def send_command(self):
        text=self.command_entry.get()
        if text:
            if self.in_sess:
                message=','.join(["all",text])
            else:
                message=text
            self.client_socket.send(message.encode('utf-8'))
            self.command_entry.delete(0,tk.END)


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
        if message:
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
                    if (message["data"] is not None):
                        if(self.verbose.get()):
                            self.msg_queue.put({"echo_text":message["message"]})
                            print("event_generate echo ")
                            if(type(message["data"]) is dict):
                                for index in message["data"]:
                                    data=message["data"][index]
                                    msg="[" + str(index) + "]" + ":" + str(data)
                                    self.msg_queue.put({"echo_text" : msg})
                            else:
                                for data in message["data"]:
                                    self.msg_queue.put({"echo_text" : data})
                        print("event_generate data ")                                    
                        self.msg_queue.put({message["data"]["datatype"]:message["data"]["content"]})
                else:
                    self.msg_queue.put({"echo_text":"server disconected"})
                    self.msg_queue.put({"event_wait":None})
                    self.event_generate("<<Messages2Queue>>")
                    self.client_socket.close()
                    self.client_socket = None
                    break

                print("before SetEvent")
                # assume that callback for event_wait if present coresponded exactly to responce from server, sent to callback status of responce
                self.msg_queue.put({"event_wait":message})
                self.event_generate("<<Messages2Queue>>")
                print("after SetEvent")

            except Exception as e:
                print("Error receiving message:", e)
                break


if __name__ == "__main__":
    app = GUI()
    app.mainloop()
