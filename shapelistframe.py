import tkinter as tk
from tkinter import ttk

class Shape_List_frame(ttk.Frame):
    def __init__(self,parent,callbacks,cCallbacks):
        """
        The constructor initializes a GUI frame with various widgets for shape manipulation and selection.
        
        """
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
        self.move_btn.grid(row=0,column=5,padx=1,pady=1)
        
        self.scale_btn=tk.Radiobutton(self.nav_bar,text="scale",variable=self.edit,value="scale_shape",command=self.edit_shape)
        self.scale_btn.configure(state=tk.DISABLED)
        self.scale_btn.grid(row=1,column=5,padx=1,pady=1)

        self.rotate_btn=tk.Radiobutton(self.nav_bar,text="rotate",variable=self.edit,value="rotate_shape",command=self.edit_shape)
        self.rotate_btn.configure(state=tk.DISABLED)
        self.rotate_btn.grid(row=2,column=5,padx=1,pady=1)

        self.edit.set(None)

        self.clear_btn=ttk.Button(self.nav_bar,text="clear canvas",command=self.clear_canvas)
        self.clear_btn.configure(state=tk.DISABLED)
        self.clear_btn.grid(row=4,column=3,padx=1,pady=1)

        self.delete_btn=ttk.Button(self.nav_bar,text="delete",command=self.delete_shape)
        self.delete_btn.configure(state=tk.DISABLED)
        self.delete_btn.grid(row=4,column=2,padx=1,pady=1)



        self.var=tk.StringVar()

        self.draw_circle_button=tk.Radiobutton(self.nav_bar,text="circle",variable=self.var,value="circle",command=self.sel)
        self.draw_circle_button.configure(state=tk.DISABLED)
        self.draw_circle_button.grid(row=0,column=1,padx=1,pady=1)

        self.draw_rectangle_button=tk.Radiobutton(self.nav_bar,text="rectangle",variable=self.var,value="rectangle",command=self.sel)
        self.draw_rectangle_button.configure(state=tk.DISABLED)
        self.draw_rectangle_button.grid(row=1,column=1,padx=1,pady=1)

        self.draw_triangle_button=tk.Radiobutton(self.nav_bar,text="triangle",variable=self.var,value="triangle",command=self.sel)
        self.draw_triangle_button.configure(state=tk.DISABLED)
        self.draw_triangle_button.grid(row=2,column=1,padx=1,pady=1)

        self.draw_polygon_button=tk.Radiobutton(self.nav_bar,text="polygon",variable=self.var,value="polygon",command=self.sel)
        self.draw_polygon_button.configure(state=tk.DISABLED)
        self.draw_polygon_button.grid(row=3,column=1,padx=1,pady=1)

        self.var.set(None)

        self.listbox.bind('<<ListboxSelect>>', self.on_select)

    def toggle_draw(self):
        """
        This function enables drawing buttons and disables transformation buttons in a GUI
        canvas.
        """
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
        """
        The function disables drawing buttons and enables editing buttons in a GUI
        application.
        """
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
        """
        The function iterates through a dictionary and calls `Update_listSingle` for each
        key-value pair.
        
        """
        #self.listbox.delete(0,tk.END)
        for Sid,details in sList.items():
            self.Update_listSingle(int(Sid),details)

    def Update_listSingle(self,srvShapeId:int,details:str):
        """
        This function updates a listbox by either deleting an item with a specific ID or
        inserting a new item based on the provided details.
        
        """
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
        """
        The ListClear function deletes all items from a listbox.
        """
        self.listbox.delete(0,tk.END)

    def Joined_sess(self):
        """
        This function sets certain buttons to be active if `in_sess` is False.
        """
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
        """
        This function prints the selected option and calls a callback function with the selected option
        as an argument.
        """
        print("You selected the option " + str(self.var.get()))
        self.canvascallbacks["on_change_type"](str(self.var.get()))

    def edit_shape(self):
        """
        This function prints the selected option and triggers a callback with the selected option as
        an argument.
        """
        print("you selected the option " + str(self.edit.get()))
        self.canvascallbacks["on_change_edit"](str(self.edit.get()))

    def on_select(self,event):
        """
        This function handles the selection of an item in a listbox and triggers a callback with the
        selected shape ID.
        
        """
        if self.listbox.curselection():
            selected_shape=self.listbox.curselection()
            index=int(selected_shape[0])
            shapeid=self.get_shape_id(index)
            self.canvascallbacks["on_shape_select"](shapeid)
            self.delete_btn.config(state=tk.NORMAL)
        else:
            self.delete_btn.config(state=tk.DISABLED)

    def delete_shape(self):
        """
        This function deletes a selected shape from a listbox and triggers a callback to delete the
        shape on a canvas.
        """
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
        """
        This function retrieves the shape ID from a selected item in a listbox.
        """
        selected_shape = self.listbox.get(index)
        selected_shapeID=selected_shape[1:6]
        shapeid=selected_shapeID.strip()
        return int(shapeid)

    def clear_canvas(self):
        """
        This function deletes all shapes from a canvas and clears a listbox.
        """
        for index in range(self.listbox.size()):
            srvShapeId = self.get_shape_id(index)
            self.canvascallbacks["on_delete_shape"](srvShapeId)
        self.listbox.delete(0,tk.END)
        self.canvascallbacks["on_clear_canvas"]()

