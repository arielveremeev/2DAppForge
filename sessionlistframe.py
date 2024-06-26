import tkinter as tk
from tkinter import ttk
from dialogs import CreateSessDialog
class SessionListFrame(ttk.Frame):
    def __init__(self,parent,callbacks):
        """
        This Python constructor initializes a GUI frame with buttons and a listbox for managing sessions.
        
        """
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
        self.create_btn.configure(state=tk.DISABLED)
        self.create_btn.pack(side=tk.RIGHT)

        self.delete_btn=ttk.Button(self.nav_bar,text="delete",command=self.delete_sess)
        self.delete_btn.configure(state=tk.DISABLED)
        self.delete_btn.pack(side=tk.RIGHT)

    def on_successful_login(self):
        self.create_btn.configure(state=tk.ACTIVE)

    def on_disconect(self):
        self.leave_btn.configure(state=tk.DISABLED)
        self.join_btn.configure(state=tk.DISABLED)
        self.create_btn.configure(state=tk.DISABLED)
        self.delete_btn.configure(state=tk.DISABLED)

    def on_select(self,event):
        """
        The `on_select` function enables or disables buttons based on whether an item is selected in a
        listbox.
        
        """
        if self.listbox.curselection():
            self.join_btn.configure(state=tk.ACTIVE)
            if self.current_sess:
                pass
            else:
                self.delete_btn.configure(state=tk.ACTIVE)
        else:
            self.join_btn.config(state=tk.DISABLED)
            self.delete_btn.configure(state=tk.DISABLED)

    def on_double_click(self,event):
        """
        The `on_double_click` function checks if an item is selected in a listbox and opens a dialog for
        joining a session if an item is selected.
        
        """
        if self.listbox.curselection():
            self.open_join_sess_dialog()
        else:
            pass


    def Update_list(self,sList:dict):
        """
        The `Update_list` function deletes all items in a listbox and then inserts new items based on the
        input dictionary `sList`.
        
        """
        self.listbox.delete(0,tk.END)
        for item in sList:
            session=','.join([str(item[0]),str(item[1])])
            self.listbox.insert(tk.END,session)

    def open_create_sess_dialog(self):
        """
        This function opens a dialog window for creating a session.
        """
        dialog=CreateSessDialog(self,self.callbacks)
        dialog.grab_set()
        self.wait_window(dialog)

    def open_join_sess_dialog(self):
        """
        This function opens a dialog box to join a selected session and updates the UI accordingly.
        """
        seleceted_sess=self.listbox.get(self.listbox.curselection())
        if(seleceted_sess):
            details=seleceted_sess.split(',')
            self.current_sess=details[0]
            self.callbacks["on_join_session"](self.current_sess)
            self.leave_btn.configure(state=tk.ACTIVE)
            self.join_btn.configure(state=tk.DISABLED)
            self.create_btn.configure(state=tk.DISABLED)
            self.delete_btn.configure(state=tk.DISABLED)
        else:
            pass
        
    
    def delete_sess(self):
        """
        This function deletes a selected session by extracting the session name from a listbox and
        calling a callback function with the session name as an argument.
        """
        seleceted_sess=self.listbox.get(self.listbox.curselection())
        if(seleceted_sess):
            sessname=seleceted_sess.split(",")[0]
            print(sessname)
            self.callbacks["on_delete_session"](sessname)
        else:
            pass

    def Leave_Sess(self):
        """
        The  function checks if there is a current session and performs certain actions if there is.
        """
        if self.current_sess != "":
            self.callbacks["on_leave_session"]()

            self.leave_btn.configure(state=tk.DISABLED)
            self.join_btn.configure(state=tk.ACTIVE)
            self.create_btn.configure(state=tk.ACTIVE)
            self.current_sess=""