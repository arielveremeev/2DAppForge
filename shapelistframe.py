import tkinter as tk
from tkinter import ttk

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

