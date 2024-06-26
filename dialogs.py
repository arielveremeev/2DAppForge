import tkinter as tk

class ConnectDialog(tk.Toplevel):
    def __init__(self, parent, default_server_ip, callback):
        """
        The function initializes a dialog window for connecting to a server with input fields for server IP,
        username, and password, along with buttons for login, sign up, and cancel.
        
        """
        super().__init__(parent)

        self.callback = callback

        self.title("Connect to Server")

        # Get the main window position
        parent_pos_x = parent.winfo_rootx()
        parent_pos_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        # Calculate the position of the dialog to be in the center of the main window
        dialog_width = 300
        dialog_height = 200
        dialog_pos_x = parent_pos_x + (parent_width - dialog_width) // 2
        dialog_pos_y = parent_pos_y + (parent_height - dialog_height) // 2

        # Set the geometry of the dialog to be in the center of the main window
        self.geometry(f"{dialog_width}x{dialog_height}+{dialog_pos_x}+{dialog_pos_y}")

        self.server_ip_label = tk.Label(self, text="Server IP:")
        self.server_ip_label.grid(row=0, column=0, padx=5, pady=5)
        self.server_ip_text = tk.StringVar()
        self.server_ip_text.set("127.0.0.1" if default_server_ip is None else default_server_ip)
        self.server_ip_entry = tk.Entry(self, textvariable=self.server_ip_text)
        self.server_ip_entry.grid(row=0, column=1, padx=5, pady=5)

        self.username_label = tk.Label(self, text="Username:")
        self.username_label.grid(row=1, column=0, padx=5, pady=5)
        self.username_text = tk.StringVar()
        self.username_entry = tk.Entry(self, textvariable=self.username_text)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)

        self.password_label = tk.Label(self, text="Password:")
        self.password_label.grid(row=2, column=0, padx=5, pady=5)
        self.password_text = tk.StringVar()
        self.password_entry = tk.Entry(self, show="*", textvariable=self.password_text)
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)

        # Create the buttons and place them on the same row
        self.login_button = tk.Button(self, text="Login", command=lambda: self.on_ok(True))
        self.login_button.grid(row=3, column=0, padx=5, pady=5)

        self.signup_button = tk.Button(self, text="Sign Up", command=lambda: self.on_ok(False))
        self.signup_button.grid(row=3, column=1, padx=5, pady=5)

        self.cancel_button = tk.Button(self, text="Cancel", command=self.on_cancel)
        self.cancel_button.grid(row=3, column=2, padx=5, pady=5)

        self.ssl=tk.BooleanVar()
        self.ssl.set(False)

        self.ssl_check=tk.Checkbutton(self,text="ssl on/off",variable=self.ssl,onvalue=True,offvalue=False,command=self.toggle_ssl)
        self.ssl_check.grid(row=4, column=2, padx=5, pady=5)

        self.result = None
        self.ok_clicked = False

    def on_ok(self, is_login):
        """
        The function `on_ok` retrieves server IP, username, and password from user input fields, validates
        the input, stores the result, and calls a callback function before destroying the window.
        
        """
        server_ip = self.server_ip_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if server_ip and username and password:
            self.result = (server_ip, username, password)
            self.ok_clicked = True
            self.callback(self.result, is_login,self.ssl.get())
        self.destroy()

    def on_cancel(self):
        """
        The `on_cancel` function in Python destroys the current window dialog.
        """
        self.destroy()

    def toggle_ssl(self):
        """
        The `toggle_ssl` function checks if SSL is enabled and prints a message accordingly.
        """
        if self.ssl.get():
            print("ssl on")
        else:
            print("ssl off")

class CreateSessDialog(tk.Toplevel):
    def __init__(self,parent,callback):
        """
        This Python code snippet defines a class with a constructor that creates a GUI window for creating a
        session with input fields for session name and maximum participants, along with buttons for creating
        the session and canceling.
        
        """
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
        """
        The function `on_Create` retrieves input values, checks if they are not empty, stores them, triggers
        a callback function, and then closes the current window.
        """
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
        """
        The `on_cancel` function in Python destroys the current windod dialog.
        """
        self.destroy()


class LoadFileDialog(tk.Toplevel):
    def __init__(self,parent,callback):
        """
        The above code for choosing a file to be loaded to the server session
        
        """
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
        """
        The `on_open` function in Python retrieves a file name, prints it, sets a result variable, triggers
        a callback function, and then destroys the current object.
        
        """
        name = self.file_name_entry.get()
        print(name)
        if name :
            self.result=(name)
            self.Open_clicked=True
            self.callback["on_load_file"](self.result)
            self.destroy()

    def on_cancel(self):
        """
        The `on_cancel` function in Python destroys the current window dialog.
        """
        self.destroy()

    def on_select(self, event):
        """
        The `on_select` function sets the selected file name in a text variable when an item is selected in
        a listbox.
        
        """
        if self.listbox.curselection():
            selected_file = self.listbox.get(self.listbox.curselection())
            self.file_name_text.set(selected_file)
    
    def update_list(self,file_list:list):
        """
        The `update_list` function clears the existing items in a listbox and inserts new items from a given
        file list.
        
        """
        self.listbox.delete(0,tk.END)
        for item in file_list:
            self.listbox.insert(tk.END,item)


class SaveFileDialog(tk.Toplevel):
    def __init__(self,parent):
        """
        This Python code opens a dialog which lets you choose a file name and saves it with the .avsf extension
        
        """
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
        """
        The `on_save` function retrieves a file name from an entry widget, appends ".avsf" if not already
        present, sets a flag, and closes the window dialog.
        
        """
        self.result=self.file_name_entry.get()
        if self.result :
            if ".avsf" not in self.result:
                self.result+=".avsf"
            self.save_clicked=True
        self.destroy()

    def on_cancel(self):
        """
        The `on_cancel` function in Python destroys the current window dialog.
        """
        self.destroy()            
