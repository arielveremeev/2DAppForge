import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
from tkinter import filedialog
#from PIL import Image, ImageDraw
import socket
import ipaddress
import ssl
import json
import threading
import queue
import math

class ConnectDialog(tk.Toplevel):
    def __init__(self, parent, default_server_ip, callback):
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
        self.server_ip_text.set("127.0.0.1" if default_server_ip is None else default_server_ip) 
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

class LoadFileDialog(tk.Toplevel):
    def __init__(self,parent,callback):
        super().__init__(parent)

        self.callback=callback

        self.title("Load file")

        self.listbox_frame = tk.Frame(self)
        self.listbox_frame.pack(expand=True, fill=tk.BOTH)

        self.listbox_scrollbar = tk.Scrollbar(self.listbox_frame)
        self.listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(self.listbox_frame, height=4, yscrollcommand=self.listbox_scrollbar.set)
        self.listbox.pack(expand=True, fill=tk.BOTH)

        self.listbox_scrollbar.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        self.file_name = tk.Label(self, text="Enter file name")        
        self.file_name.pack(pady=5)
        self.file_name_text=tk.StringVar()
        self.file_name_text.set("shapes.avsf")
        self.file_name_entry = tk.Entry(self,textvariable=self.file_name_text)
        self.file_name_entry.pack(pady=5)
        
        self.Open_button = tk.Button(self, text="Open", command=self.on_open)
        self.Open_button.pack(side=tk.LEFT,padx=10, pady=10)
        self.cancel_button = tk.Button(self, text="Cancel", command=self.on_cancel)
        self.cancel_button.pack(side=tk.RIGHT,padx=10, pady=10)

        self.result=None
        self.Open_clicked=False

        self.bind("<Return>", self.on_open)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def on_open(self, event=None):
        name = self.file_name_entry.get()
        print(name)
        if name :
            self.result=(name)
            self.Open_clicked=True
            self.callback["on_load_file"](self.result)
            self.destroy()

    def on_cancel(self):
        self.destroy()

    def on_select(self, event):
        if self.listbox.curselection():
            selected_file = self.listbox.get(self.listbox.curselection())
            self.file_name_text.set(selected_file)
    
    def update_list(self,file_list:list):
        self.listbox.delete(0,tk.END)
        for item in file_list:
            self.listbox.insert(tk.END,item)

class SaveFileDialog(tk.Toplevel):
    def __init__(self,parent):
        super().__init__(parent)

        self.title("save file")

        self.listbox_frame = tk.Frame(self)
        self.listbox_frame.pack(expand=True, fill=tk.BOTH)

        self.file_name = tk.Label(self, text="Enter file name")        
        self.file_name.pack(pady=5)
        self.file_name_entry = tk.Entry(self)
        self.file_name_entry.pack(pady=5)
        
        self.save_button = tk.Button(self, text="save", command=self.on_save)
        self.save_button.pack(side=tk.LEFT,padx=10, pady=10)
        self.cancel_button = tk.Button(self, text="Cancel", command=self.on_cancel)
        self.cancel_button.pack(side=tk.RIGHT,padx=10, pady=10)

        self.result=None
        self.save_clicked=False

        self.bind("<Return>", self.on_save)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def on_save(self, event=None):
        self.result=self.file_name_entry.get()
        if self.result :
            if ".avsf" not in self.result:
                self.result+=".avsf"
            self.save_clicked=True
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

        self.scrollbar=tk.Scrollbar(self,orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT,fill=tk.Y)

        self.listbox=tk.Listbox(self)
        self.listbox.pack(expand=True,fill=tk.BOTH)
        self.listbox.bind("<ButtonRelease-1>", self.on_select)
        self.listbox.bind("<Double-Button-1>", self.on_double_click)

        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

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
    def __init__(self,parent,callbacks,cCallbacks):
        ttk.Frame.__init__(self, parent)

        self.callbacks=callbacks
        self.canvascallbacks=cCallbacks
        self.in_sess=False

        self.label=ttk.Label(self,text="shape list")
        self.label.pack(side=tk.TOP)

        self.scrollbar=tk.Scrollbar(self,orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT,fill=tk.Y)

        self.listbox=tk.Listbox(self)
        self.listbox.pack(expand=True,fill=tk.BOTH)

        self.listbox.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.listbox.yview)

        self.nav_bar = ttk.Frame(self)
        self.nav_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.mode=tk.StringVar()

        self.edit_mode_button=tk.Radiobutton(self,text="edit mode",variable=self.mode,value="edit",command=self.toggle_edit)
        self.edit_mode_button.configure(state=tk.DISABLED)
        self.edit_mode_button.pack(side=tk.RIGHT)

        self.draw_mode_button=tk.Radiobutton(self,text="draw mode",variable=self.mode,value="draw",command=self.toggle_draw)
        self.draw_mode_button.configure(state=tk.DISABLED)
        self.draw_mode_button.pack(side=tk.LEFT)

        self.mode.set("draw")

        self.edit=tk.StringVar()

        self.move_btn=tk.Radiobutton(self.nav_bar,text="move",variable=self.edit,value="move_shape",command=self.edit_shape)
        self.move_btn.configure(state=tk.DISABLED)
        self.move_btn.pack(side=tk.RIGHT)

        self.scale_btn=tk.Radiobutton(self.nav_bar,text="scale",variable=self.edit,value="scale_shape",command=self.edit_shape)
        self.scale_btn.configure(state=tk.DISABLED)
        self.scale_btn.pack(side=tk.RIGHT)

        self.rotate_btn=tk.Radiobutton(self.nav_bar,text="rotate",variable=self.edit,value="rotate_shape",command=self.edit_shape)
        self.rotate_btn.configure(state=tk.DISABLED)
        self.rotate_btn.pack(side=tk.RIGHT)

        self.edit.set(None)

        self.clear_btn=ttk.Button(self.nav_bar,text="clear canvas",command=self.clear_canvas)
        self.clear_btn.configure(state=tk.DISABLED)
        self.clear_btn.pack(side=tk.RIGHT)

        self.delete_btn=ttk.Button(self.nav_bar,text="delete",command=self.delete_shape)
        self.delete_btn.configure(state=tk.DISABLED)
        self.delete_btn.pack(side=tk.RIGHT)



        self.var=tk.StringVar()

        self.draw_circle_button=tk.Radiobutton(self.nav_bar,text="circle",variable=self.var,value="circle",command=self.sel)
        self.draw_circle_button.configure(state=tk.DISABLED)
        self.draw_circle_button.pack(anchor=tk.W)

        self.draw_rectangle_button=tk.Radiobutton(self.nav_bar,text="rectangle",variable=self.var,value="rectangle",command=self.sel)
        self.draw_rectangle_button.configure(state=tk.DISABLED)
        self.draw_rectangle_button.pack(anchor=tk.W)

        self.draw_triangle_button=tk.Radiobutton(self.nav_bar,text="triangle",variable=self.var,value="triangle",command=self.sel)
        self.draw_triangle_button.configure(state=tk.DISABLED)
        self.draw_triangle_button.pack(anchor=tk.W)

        self.draw_polygon_button=tk.Radiobutton(self.nav_bar,text="polygon",variable=self.var,value="polygon",command=self.sel)
        self.draw_polygon_button.configure(state=tk.DISABLED)
        self.draw_polygon_button.pack(anchor=tk.W)

        self.var.set(None)

        self.listbox.bind('<<ListboxSelect>>', self.on_select)

    def toggle_draw(self):
        self.draw_circle_button.configure(state=tk.ACTIVE)
        self.draw_rectangle_button.configure(state=tk.ACTIVE)
        self.draw_triangle_button.configure(state=tk.ACTIVE)
        self.draw_polygon_button.configure(state=tk.ACTIVE)
        self.var.set(None)

        self.move_btn.configure(state=tk.DISABLED)
        self.scale_btn.configure(state=tk.DISABLED)
        self.rotate_btn.configure(state=tk.DISABLED)
        self.edit.set(None)

        self.canvascallbacks["on_change_draw"]("draw")

    def toggle_edit(self):
        self.draw_circle_button.configure(state=tk.DISABLED)
        self.draw_rectangle_button.configure(state=tk.DISABLED)
        self.draw_triangle_button.configure(state=tk.DISABLED)
        self.draw_polygon_button.configure(state=tk.DISABLED)
        self.var.set(None)

        self.move_btn.configure(state=tk.ACTIVE)
        self.scale_btn.configure(state=tk.ACTIVE)
        self.rotate_btn.configure(state=tk.ACTIVE)
        self.edit.set(None)

        self.canvascallbacks["on_change_draw"]("edit")

    def Update_list(self,sList:dict):
        #self.listbox.delete(0,tk.END)
        for Sid,details in sList.items():
            self.Update_listSingle(int(Sid),details)

    def Update_listSingle(self,srvShapeId:int,details:str):
        if srvShapeId < 0:
            srvShapeId = -srvShapeId
            # Iterate through each item in the Listbox
            for index in range(self.listbox.size()):
                # Get the value of the current item
                item_value = self.listbox.get(index)
                # Check if the current item's value matches the value we're searching for
                if item_value.find('[{:-5}]'.format(srvShapeId)) == 0:
                    self.listbox.delete(index)
                    break
        else:
            Sdetails=details.split(" ")
            if(Sdetails[0] == "polygon"):
                shape= '[{:-5}] {} [{:-5}]'.format(int(srvShapeId),Sdetails[0],int(Sdetails[1]))
            else:
                shape= '[{:-5}] {}'.format(int(srvShapeId),Sdetails[0])
            self.listbox.insert(tk.END,shape)
    def ListClear(self):
        self.listbox.delete(0,tk.END)

    def Joined_sess(self):
        if self.in_sess == False:
            self.in_sess=True
            self.draw_mode_button.configure(state=tk.ACTIVE)
            self.edit_mode_button.configure(state=tk.ACTIVE)
            self.clear_btn.configure(state=tk.ACTIVE)
            self.draw_circle_button.configure(state=tk.ACTIVE)
            self.draw_rectangle_button.configure(state=tk.ACTIVE)
            self.draw_triangle_button.configure(state=tk.ACTIVE)
            self.draw_polygon_button.configure(state=tk.ACTIVE)
        

    def sel(self):
        print("You selected the option " + str(self.var.get()))
        self.canvascallbacks["on_change_type"](str(self.var.get()))

    def edit_shape(self):
        print("you selected the option " + str(self.edit.get()))
        self.canvascallbacks["on_change_edit"](str(self.edit.get()))

    def on_select(self,event):
        if self.listbox.curselection():
            selected_shape=self.listbox.curselection()
            index=int(selected_shape[0])
            shapeid=self.get_shape_id(index)
            self.canvascallbacks["on_shape_select"](shapeid)
            self.delete_btn.config(state=tk.NORMAL)
        else:
            self.delete_btn.config(state=tk.DISABLED)

    def delete_shape(self):
        print("delete")
        selected_shape=self.listbox.curselection()
        if(selected_shape):
            index=int(selected_shape[0])
            shapeid=self.get_shape_id(index)
            print(shapeid)
            self.canvascallbacks["on_delete_shape"](shapeid)
            self.listbox.delete(index)
        self.delete_btn.config(state=tk.DISABLED)

    def get_shape_id(self,index):
        selected_shape = self.listbox.get(index)
        selected_shapeID=selected_shape[1:6]
        shapeid=selected_shapeID.strip()
        return int(shapeid)

    def clear_canvas(self):
        self.canvascallbacks["on_clear_canvas"]


class DrawCanvas(tk.Canvas):
    def __init__(self,parent,callbacks):
        tk.Canvas.__init__(self,parent,bg="white")
        
        self.callbacks=callbacks
        self.selectedshape=""
        self.selectedtype=""
        self.selectededit=""
        self.canvas_status=False

        self.start_x = None
        self.start_y = None
        self.current_shape_item = None
        self.debug_shapes = []



    def change_draw_type(self,text):
        if text:
            self.selectedtype=text
            if(self.selectedtype == "edit"):
                self.toggle_edit()
            else:
                self.toggle_draw()
            print("current drawing type is " + str(self.selectedtype))

    def change_shape_type(self,text):
        if text:
            self.selectedshape=text
            print("current shape is " + str(self.selectedshape))
            if text == "polygon":
                self.unbind("<B1-Motion>")
                self.unbind("<ButtonRelease-1>")
                self.bind("<Button-1>", self.draw_polygon)
                self.bind("<Double-Button-1>",self.stop_polygon)

                self.PolyPoints=[]
                self.polygon=None
            else:
                self.toggle_draw()

    def change_edit_type(self,text):
        if text:
            self.selectededit=text
            print("selected edit type is " + self.selectededit)
            

    def toggle_draw(self):
        self.canvas_status=True

        self.bind("<Button-1>", self.start_draw)
        self.bind("<B1-Motion>", self.draw_shape)
        self.bind("<ButtonRelease-1>", self.stop_draw)

    def toggle_edit(self):
        self.unbind("<B1-Motion>")
        self.unbind("<ButtonRelease-1>")

        self.bind("<Button-1>", self.on_shape_click)
        #self.bind("<B1-Motion>", self.move_shape)
        #self.bind("<ButtonRelease-1>", self.stop_move)

    def on_shape_click(self, event):

        print("on shape pressed")
        for shape_id in self.debug_shapes:
            self.delete(shape_id)
        self.debug_shapes = []
        self.drag_shape_id = self.find_closest(event.x, event.y)[0]
        if self.drag_shape_id:
            print("shape pressed")
            self.draw_shape_bb(self.drag_shape_id)
            self.start_drag_x,self.start_drag_y=event.x,event.y
            self.move_x,self.move_y=0,0
            self.start_coords=self.coords(self.drag_shape_id)
            if self.selectededit == "move_shape":
                self.bind("<B1-Motion>", self.move_shape)
                self.bind("<ButtonRelease-1>", self.stop_move)
            elif self.selectededit == "scale_shape":
                self.debug_shapes = self.draw_scale_star3debug(self.drag_shape_id)
                self.bind("<MouseWheel>", self.scale_shape)
            elif self.selectededit == "rotate_shape":
                self.debug_shapes = self.draw_scale_star3debug(self.drag_shape_id)
                self.bind("<MouseWheel>", self.rotate_shape)

    def move_shape(self,event):
        if self.drag_shape_id:
            delta_x = event.x - self.start_drag_x
            delta_y = event.y - self.start_drag_y
            self.move(self.drag_shape_id,delta_x,delta_y)
            self.draw_shape_bb(self.drag_shape_id)
            self.start_drag_x,self.start_drag_y=event.x,event.y
            self.move_x+=delta_x
            self.move_y+=delta_y

    def stop_move(self,event):
        self.callbacks["on_shape_move"](self.drag_shape_id,self.move_x,self.move_y)
        self.drag_shape_id=None

    def scale_shape(self,event):
        if self.drag_shape_id:
            size =(5*event.delta)/120
            print(self.size)
            if len(self.start_coords) == 4:
                cCoords=self.coords(self.drag_shape_id)
                self.coords(self.drag_shape_id,cCoords[0] - size, cCoords[1] - size, cCoords[2] + size, cCoords[3] + size)
            else:
                avgX,avgY=self.calc_center(self.coords(self.drag_shape_id))
                newX,newY=None,None
                coords=self.coords(self.drag_shape_id)
                cCoords=[]
                for i in range(0,len(self.coords(self.drag_shape_id)),2):
                    x=coords[i]
                    y=coords[i+1]
                    dir_x = x - avgX
                    dir_y = y - avgY
                    if event.delta > 0:
                        newX = avgX + dir_x * 1.05
                        newY = avgY + dir_y * 1.05
                    else:
                        newX = avgX + dir_x * 0.95
                        newY = avgY + dir_y * 0.95
                    cCoords.append(newX)
                    cCoords.append(newY)
                self.coords(self.drag_shape_id,cCoords)
            self.draw_shape_bb(self.drag_shape_id)

    def rotate_shape(self,event):
        if self.drag_shape_id:
            angle=5 if event.delta > 0 else -5
            avgX,avgY=self.calc_center(self.coords(self.drag_shape_id))
            cCoords=[]
            # Convert the angle from degrees to radians
            angle_rad = math.radians(angle)
            
            # Create a new list for the rotated vertices
            rotated_vertices = []
            for i in range(0, len(self.coords(self.drag_shape_id)), 2):
                x = self.coords(self.drag_shape_id)[i]
                y = self.coords(self.drag_shape_id)[i + 1]
                
                # Calculate the position relative to the center
                rel_x = x - avgX
                rel_y = y - avgY
                
                # Apply the rotation transformation
                new_rel_x = rel_x * math.cos(angle_rad) - rel_y * math.sin(angle_rad)
                new_rel_y = rel_x * math.sin(angle_rad) + rel_y * math.cos(angle_rad)
                
                # Calculate the new vertex position
                new_x = avgX + new_rel_x
                new_y = avgY + new_rel_y
                
                # Append the new vertex to the rotated vertices list
                cCoords.append(new_x)
                cCoords.append(new_y)

                
            self.coords(self.drag_shape_id,cCoords)
            self.draw_shape_bb(self.drag_shape_id)



    def calc_center(self,coords):
        count=0
        avgX,avgY=0,0
        for cord in coords:
            if count%2==0:
                avgX+=cord
            else:
                avgY+= cord
            count+=1
        avgX=avgX/(count/2)
        avgY=avgY/(count/2)
        return [avgX,avgY]
    
    def draw_scale_star3debug(self,Sid):
        if Sid:
            coords = self.coords(Sid)
            center_x,center_y = self.calc_center(coords)
            canvas_width = self.winfo_width()
            canvas_height = self.winfo_height()
            shape_ids = []

            for i in range(0, len(coords), 2):
                x = coords[i]
                y = coords[i+1]

                # Calculate the slope of the line
                if x != center_x:
                    slope = (y - center_y) / (x - center_x)
                else:
                    slope = float('inf')

                # Calculate the y-intercept of the line
                if slope != float('inf'):
                    intercept = y - slope * x
                else:
                    intercept = float('inf')

                # Calculate the x and y coordinates of the line's intersection with the canvas boundaries
                if slope != 0:
                    if x < center_x:
                        x1 = 0
                        y1 = intercept
                        x2 = center_x #canvas_width
                        y2 = center_y #slope * x2 + intercept
                    else:
                        x1 = center_x
                        y1 = center_y
                        x2 = canvas_width
                        y2 = slope * x2 + intercept
                else:
                    x1 = x
                    y1 = 0
                    x2 = x
                    y2 = canvas_height

                # Draw the line
                line_id = self.create_line(x1, y1, x2, y2, fill="green")
                shape_ids.append(line_id)

            return shape_ids
        return []


    def edit_shape(self,Sid,details:list):
        if Sid and details:
            print(self.coords(int(Sid)))
            shapeProperties = details.split(' ')
            if shapeProperties[0] == "square":
                coords = shapeProperties[2].split(";")
                self.coords(int(Sid),float(coords[0]), float(coords[1]), float(coords[6]), float(coords[7]))
            elif(shapeProperties[0] == "triangle" or shapeProperties[0] == "polygon"):
                Scoords=shapeProperties[2].split(";")
                Fcoords=self.convert_poly_2float(Scoords)
                self.coords(int(Sid),Fcoords)
            elif shapeProperties[0] == "circle":
                radius=shapeProperties[3]
                Scoords = shapeProperties[2].split(";")
                Ccoords=self.get_circle_points(radius,Scoords)
                self.coords(int(Sid),float(Ccoords[0]), float(Ccoords[1]), float(Ccoords[2]), float(Ccoords[3]))
                
    def start_draw(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.selectedshape == "rectangle":
            self.current_shape_item = self.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y, outline="black"
            )

        elif self.selectedshape == "triangle":
            self.current_shape_item=self.create_polygon(
                self.start_x,self.start_y,self.start_x,self.start_y,self.start_x,self.start_y,outline="black",fill=""
            )
            
        elif self.selectedshape == "circle":
            self.current_shape_item = self.create_oval(
                self.start_x, self.start_y, self.start_x, self.start_y, outline="black"
            )

    def draw_shape(self, event):
        if self.current_shape_item:
            if(self.selectedshape=="circle"):
                x= event.x
                y=(x-self.start_x) + self.start_y
                self.coords(self.current_shape_item, self.start_x, self.start_y, x, y)
            elif(self.selectedshape=="triangle"):
                if(event.x > self.start_x):
                    self.coords(self.current_shape_item,self.start_x,self.start_y,event.x,event.y,self.start_x-(event.x-self.start_x),event.y)
                else:
                    self.coords(self.current_shape_item,self.start_x,self.start_y,event.x,event.y,(self.start_x - event.x) + self.start_x,event.y)
            else:
                x, y = event.x, event.y
                self.coords(self.current_shape_item, self.start_x, self.start_y, x, y)
    
    def stop_draw(self, event):
        Ccoords=self.coords(self.current_shape_item)
        shape=""
        print(Ccoords)
        if(self.selectedshape == "rectangle"):
            coords=str(Ccoords[0]) + ";"+str(Ccoords[1]) + ";" + str(Ccoords[2]) + ";" + str(Ccoords[1]) + ";" + str(Ccoords[0])+ ";" + str(Ccoords[3])+ ";" + str(Ccoords[2])+ ";" + str(Ccoords[3])
            shape="square 4 "+ coords
            print(shape)

        elif(self.selectedshape == "triangle"):
            coords=self.convert_poly_2str(Ccoords)
            shape="triangle 3 "+coords
            print(shape)

        elif(self.selectedshape=="circle"):
            print(Ccoords[0])
            print(Ccoords[1])
            print(Ccoords[2])
            print(Ccoords[3])
            center=self.get_center(Ccoords[0],Ccoords[1],Ccoords[2],Ccoords[3])
            radius=self.get_radius(Ccoords[ 0],Ccoords[2])
            CenCord=str(center[0]) + ";" + str(center[1])
            shape="circle 1 " + str(CenCord) + " " + str(radius)

        self.delete(self.current_shape_item)
        self.callbacks["on_shape_finish"](shape)
        self.current_shape_item = None

    def draw_polygon(self,event):
        self.PolyPoints.append((event.x, event.y))
        self.delete(self.polygon)
        self.polygon=self.create_polygon(self.PolyPoints,outline="black", fill="")
        print(self.coords(self.polygon))

    def stop_polygon(self,event):
        Ccoords=self.coords(self.polygon)
        coords=self.convert_poly_2str(Ccoords)
        vertexes=len(self.PolyPoints)
        shape="polygon" + " " + str(vertexes) + " " + coords 
        print(shape)

        self.delete(self.polygon)

        self.callbacks["on_shape_finish"](shape)

        self.polygon=None
        self.PolyPoints=[]

    def add_shape(self,details)->list:
        shapeProperties = details.split(' ')
        if shapeProperties[0] == "square":
           coords = shapeProperties[2].split(";")
           current_shape_item = self.create_rectangle(
                float(coords[0]), float(coords[1]), float(coords[6]), float(coords[7]), outline="black"
            )
           
        elif(shapeProperties[0] == "triangle"):
            coords=shapeProperties[2].split(";")
            print(coords)
            current_shape_item=self.create_polygon(
                float(coords[0]), float(coords[1]), float(coords[2]), float(coords[3]),float(coords[4]), float(coords[5]),outline="black",fill=""
            )
        elif shapeProperties[0] == "circle":
            radius=shapeProperties[3]
            Scoords = shapeProperties[2].split(";")
            Ccoords=self.get_circle_points(radius,Scoords)
            current_shape_item = self.create_oval(
                float(Ccoords[0]), float(Ccoords[1]), float(Ccoords[2]), float(Ccoords[3]), outline="black"
            )
        elif shapeProperties[0] == "polygon":
            coords=self.convert_poly_2float(shapeProperties[2].split(";"))
            current_shape_item=self.create_polygon(
                coords,outline="black",fill=""
            )
        print("from add shape",current_shape_item)
        return current_shape_item

    def draw_shape_bb(self,Sid):
        self.delete("bounding_box")
        if Sid:
            x1, y1, x2, y2 = self.bbox(Sid)
            self.create_rectangle(x1, y1, x2, y2, outline="red", tags="bounding_box")

    def remove_shape(self,Sid):
        if Sid:
            self.delete(Sid)
            self.delete("bounding_box")

    def get_center(self,x1, y1, x2, y2):
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        return center_x, center_y

    def get_radius(self,x1, x2):
        radius = abs(x2 - x1) / 2
        return radius
    
    def get_circle_points(self,Sradius,Scoords):
        radius=float(Sradius)
        Ccoords=[]
        Ccoords.append(float(Scoords[0]) - radius)
        Ccoords.append(float(Scoords[1]) - radius)
        Ccoords.append(float(Scoords[0]) + radius)
        Ccoords.append(float(Scoords[1]) + radius)

        return Ccoords
    def convert_poly_2float(self,Spoints:list):
        Fpoints=[]
        for cord in Spoints:
            Fpoints.append(float(cord))
        return Fpoints
    def convert_poly_2str(self,Fpoints:list):
        Spoints=""
        count=0
        for cord in Fpoints:
            Spoints+=str(cord)
            if count < len(Fpoints) -1:
                Spoints+=";"
            count+=1
        return Spoints

    def on_clear(self,event):
        self.delete("all")


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
            "on_shape_move":self.move_shape
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
        
        self.login_btn = tk.Button(self.nav_bar, text="login", command=self.open_login_dialog)
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
        if dialog.ok_clicked:
            self.login_btn.configure(state=tk.DISABLED)
            self.disconnect_btn.configure(state=tk.ACTIVE)
        else:
            self.login_btn.configure(state=tk.NORMAL)
            self.disconnect_btn.configure(state=tk.DISABLED)

    def open_save_file_dialog(self):
        dialog = SaveFileDialog(self)
        dialog.grab_set()  # Make the dialog modal
        self.wait_window(dialog)
        if dialog.save_clicked:
            self.on_save_file(dialog.result)

    def export_image(self):
        canvas_image = self.canvas.postscript(file ="dima.ps")

    def update_user_list(self,user_list):
        if user_list:
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
                self.client_socket.send(("print_users").encode('utf-8'))
                
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
