import argparse
import socket
import threading
import ssl
import ipaddress
from datetime import date
import json
import os
from DatabaseManager import DatabaseManager 
from protocolsocket import ProtocolSocketWrapper
from shapes import Shape
from shapes import CreateShape
from shapes import ShapeJsonEncoder
from collections import defaultdict
from threading import Thread,Lock
from time import time
"""
    class cSession is used to manage the shapes in a session. It has methods to load, save, delete, add, move, scale, and rotate shapes.
"""
class cSession():
    def __init__(self,name):
        """
        The constructor function initializes attributes for a class instance,
        `name` : name of the session
        `shapes` : dictionary of shapes managed in the session
        `shapeID` : counter for shape IDs
        `filename` : name of the file loaded in the session
        `locker` : a lock object for safely updating the shapes dictionary by different clients
        
        """
        self.name = name
        self.shapes={}
        self.shapeID=0
        self.filename=None
        self.locker=threading.Lock()

    def FileOpener(self,path):
        """
        This function reads a file line by line, stores each line in a list, and prints each
        line with its line number.
        """
        file=open(path,'r')
        count=0
        lines=[]
        while True:
            count+=1
            line = file.readline()
            line=line.rstrip()
            
            if not line:
                break
            lines.append(line)
            print("Line{}: {}".format(count, lines[count-1].strip()))
        file.close()
        return lines
    
    def LoadFile(self,path) -> bool:
        """
        This function loads a file, reads its contents with the fileopener function
        inserts shapes into a dictionary line by line
        """
        with self.locker:
            if os.path.exists(path):
                lines=self.FileOpener(path)
                parts=path.split("\\")
                self.filename=parts[len(parts)-1]
                for line in lines:
                    self.shapeID+=1
                    self.shapes.update({self.shapeID:CreateShape(line)})
                return True
            else:
                return False
    def DeleteShape(self,ssid) -> dict:
        """
        This function check if the shape exists in the dictionary and deletes it based on the given shape ID.
        """
        with self.locker:
            SiID=int(ssid)
            if(SiID in self.shapes.keys()): 
                deletedShape={-SiID:self.shapes[SiID]}
                del self.shapes[SiID]
                return deletedShape
            return None
    
    def AddShape(self,line) ->dict:
        """
        This function adds a new shape to a dictionary of shapes with a unique ID using the shapeID class memeber.
        """
        with self.locker:
            if(line is not None and type(line) is str):
                self.shapeID+=1
                addedShape = {self.shapeID:CreateShape(line)}
                self.shapes.update(addedShape)
                return addedShape
            return None
    
    def SaveFile(self,path):
        """
        This function writes the string representation of shapes to a file specified by the `path` parameter.
        """
        with self.locker:
            file=open(path,'w')
            for shape in self.shapes.values():
                file.write(shape.GetString() + '\n')
            file.close()
            del self.shapes
            self.shapes={}
            self.filename=None
            return True

    def shape_operation(func):
        """
        This function is a decorator that ensures thread safety and handles shape
        operations based on the provided function.
        
        """
        def wrapper(self, ssid, *args):
            with self.locker:
                SiID = int(ssid)
                if self.shapes[SiID] is not None:
                    result = func(self, SiID, *args)
                    return {SiID: self.shapes[SiID]} if result else None
                return None
        return wrapper

    @shape_operation
    def MoveShape(self, ssid, Mx:str, My:str) -> dict:
        """
        This function moves a shape identified by `ssid` by the specified amounts `Mx` and `My`.
        """
        self.shapes[ssid].MoveShape(float(Mx), float(My))
        return True

    @shape_operation
    def ScaleShape(self, ssid, Sf:str) -> dict:
        """
        This function scales a shape identified by `ssid` by a factor `Sf`.
        """
        self.shapes[ssid].ScaleShape(float(Sf))
        return True

    @shape_operation
    def RotateShape(self, ssid, ra:str) -> dict:
        """
        The function RotateShape rotates a shape by a specified angle.
        """
        self.shapes[ssid].RotateShape(float(ra))
        return True


"""
    class cClient is used to manage the client connection the session the client is connected to. 
    It has methods to handle sending messages, and broadcast messages to all clients.
"""
class cClient():
    Session ={}
    workingFolder = os.getcwd()
    def __init__(self, client_socket, address, clients, db_manager):
        """
        The function initializes attributes for a client connection handler in a Python server.
        client_socket : the socket object for the server connection
        address : the IP address of the connected client
        clients : a list of all connected clients to the server
        db_manager : the database manager object
        username : the username of the client
        session : the session the client is connected to
        is_connection_live : a boolean flag to check if the connection is still active
        lock : a lock object for safely updating the client socket
        client_thread : a thread object for handling the client communication between the client and the server
        """
        self.client_socket = client_socket
        self.address = address
        self.clients = clients
        self.db_manager = db_manager
        self.username=""
        self.session=None
        self.is_connection_live=False
        self.lock = threading.Lock()
        self.client_thread = threading.Thread(target=self.handle_client)

    def __del__(self):
        """
        The above function is a destructor that takes care of closing the clients socket.
        """
        self.client_socket.close()

    def safe_send(self, data):
        """
        This function sends data using a client socket while ensuring thread safety with a lock.
        """
        with self.lock:
            self.client_socket.send(data)

    
    def Broadcast(self,msg2send,data2send,datatype:str,send2self:bool = False,refresh :bool=False):    
        """
        This function sends a message with data to all clients in json format
        the message includes the message to send,the status of the function either success or fail, the datatype of the data, and the data itself.
        the broadcast can send to all the clients in the session or to all the clients connected to the server 
        with the option to not send the message to the sender itself
        """
        data={
                "message":msg2send,
                "status":"success",
                "data":{
                            "datatype":datatype,
                            "content":data2send
                        }
             }
        jData=json.dumps(data,cls=ShapeJsonEncoder)
        for c in self.clients:
            if(refresh):
                if(c.session is None):
                    c.safe_send(jData)
            else:
                if(self.session == c.session and (self.client_socket != c.client_socket or send2self==True)):
                    c.safe_send(jData)
        



    def handle_client(self):
        """
        This function is ran on a separate thread for each client 
        and is used to manage the client connection and communication between the server and the client.
        """
        print(f"accepted connection from {self.address}")
        """
            this while loop is responisble for authenticating the user and checking if the user is already registered in the database
            or signing up a new user and registering him into the database
        """
        while True:
            data = self.client_socket.recv() #1024)
            if not data:
                break

            messagestr=data
            print(f"Received message [{messagestr}] with length {len(messagestr)}")
            
            user=messagestr.split(',')
            if(user[0]=="sign_up" or user[0]=="login"):
                """
                    the if statement checks if the user is signing up or logging in
                """
                if(user[0]=="sign_up"):
                    if(len(user[1:])!=2):
                        data={'message':"missing arguments for sign up",
                            "status":"fail",
                            "data":None}
                    else:
                        self.username = user[1]
                        password = user[2]
                        print(self.username)
                        print(password)
                        if(self.db_manager.IfExists(self.username)==True):
                            print(f"user already exists")
                            data={'message':"username in use or doesnt exist",
                            "status":"fail",
                            "data":None}
                        else:
                            self.db_manager.insert_user(self.username,password)
                            data={'message':"successfully added user now please login using the same info",
                            "status":"success",
                            "data":None}
                    jData=json.dumps(data)
                    self.client_socket.send(jData)
        
                else:
                    if(len(user[1:])!=2):
                        data={'message':"missing arguments for login try again",
                            "status":"fail",
                            "data":None}
                    else:
                        self.username = user[1]
                        password = user[2]
                        print(self.username)
                        print(password)
                        if(self.db_manager.IfExists(self.username)==False):
                            data={"message":"user doesnt exist",
                                "status":"fail",
                                "data":None}
                        elif(ValidateLogin(self.username,password,self.db_manager)==True):
                            data={"message":"succesfull login from"+ str(self.address),
                                    "status":"success",
                                    "data":None}
                        else:
                            data={"message":"wrong password try again",
                                    "status":"fail",
                                    "data":None}
                        if(data.get("status")=="success"):
                            jData=json.dumps(data)
                            self.client_socket.send(jData)
                            self.is_connection_live=True
                            password=""
                            break
                        else:
                            jData=json.dumps(data)
                            self.client_socket.send(jData)
            else:
                data={"message":"no such command please log in to use other commands",
                    "status":"fail",
                    "data":None}
                jData=json.dumps(data)
                self.client_socket.send(jData)
        
        """
            the second while loop is responsible for handling and processing the commands sent by the client
            and sending coresponding responses to the client in a json format which includes the message, status of the function, and the data

            the command from the client should be a string and follow a certain format:
            <command>,<optional argument1>,<optional argumentN>.....
        """
        while self.is_connection_live:
            try:
                data = self.client_socket.recv() # 1024)
                if not data:
                    self.is_connection_live=False
                    break
                messagestr = data
                print(f"Received message [{messagestr}] with length {len(messagestr)}")
                command=messagestr.split(',')
                if len(command)==0:
                    continue
                print("recived command ",command[0])
                """
                    the if statement checks if the command is to broadcast a message to all users in the session
                    or to all users connected to the server
                """
                if "all" == command[0]:
                    print("contains all")
                    if(self.session!=None):
                        if(len(command[1:])==0):
                            data={'message':"be more precise",
                                "status":"fail",
                                "data":None}
                        else:
                            msg="[" + self.username + "]" + ' '.join(command[1:])
                            print(msg)
                            self.Broadcast(None,msg,datatype="msg_broadcast",send2self=True)
                            continue
                        
                    else:
                        data={'message':"user isnt in session to broadcast",
                                "status":"fail",
                                "data":None}
                elif(command[0]=="print_users"):
                    """
                        the if statement checks if the command is to print all users in the session or all users connected to the server
                    """
                    Users=[]
                    if(len(command[1:]) == 1):
                        if command[1] == "all":
                            for client in self.clients:
                                Users.append(client.username)
                        elif command[1] == "session":
                            if self.session:
                                Users=self.db_manager.Session_users(self.session)
                        self.Broadcast(msg2send="users are :",data2send=Users,datatype="user_list",send2self=False)
                        data={"message":"users are : ",
                            "status":"success",
                            "data":{"datatype":"user_list",
                                    "content":Users}
                            }
                    else:
                        data={"message":"wrong arguments",
                            "status":"fail",
                            "data":None}
                elif(command[0]=="create_session"):
                    """
                        the if statement checks if the command is to create a new session, this command takes 2 arguments: session name and max amount of participants
                    """
                    session=command[1:]
                    session.append(self.username)
                    sessname=session[0]
                    if(self.db_manager.Create_Session(session)==False):
                        data={"message":"session not created, session with this name already exists",
                            "status":"fail",
                            "data":None}
                    else:
                        self.Session[sessname] = cSession(sessname)
                        data={"message":"new session created",
                            "status":"success",
                            "data":None}
                        self.Broadcast("broadcast updated sessions",self.db_manager.Get_Sessions(),datatype="session_list",refresh=True)

                elif(command[0] == "delete_session"):
                    """
                        the if statement checks if the command is to delete a session, this command takes 1 argument: session name
                    """
                    if(command[1]):
                        session=command[1]
                        if(self.db_manager.Delete_session(session) == False):
                            data={"message":"session not delete, session with this name doesnt exist",
                                "status":"fail",
                                "data":None}  
                        else:
                            data={"message":"session deleted",
                                "status":"success",
                                "data":None}
                            self.Broadcast("broadcast updated sessions",self.db_manager.Get_Sessions(),datatype="session_list",refresh=True)
                
                elif(command[0]=="print_sessions"):
                    """
                        the if statement checks if the command is to print all sessions, this command takes no arguments
                    """
                    sessions=self.db_manager.Get_Sessions()
                    data={"message":"sessions and owners are : ",
                        "status":"success",
                        "data":{"datatype":"session_list",
                                "content":sessions}
                         }
                elif(command[0]=="join_session"):
                    """
                        the if statement checks if the command is to join a session, this command takes 1 argument: session name
                        the server checks if the session exists, if the user is already in the session, and if the session is full.
                        and returns an error in the specified cases
                    """
                    sessname=command[1]
                    data={"message":"",
                        "status":"fail",
                        "data":None}
                    if(self.session==None):
                        if(self.db_manager.Does_Sess_Exist(sessname)==True):
                            if(self.db_manager.Is_User_in_sess(self.username,sessname)==False):
                                if(self.db_manager.Can_Join(sessname)==True):
                                    self.db_manager.Insert_Active_User(self.username,sessname)
                                    self.session=sessname
                                    data["message"]="successfully joined session"
                                    data["status"]="success"
                                    data["data"]={"datatype":"shape_list",
                                                  "content":self.Session[self.session].shapes}
                                else: 
                                    data["message"]="cant join due to max participant amount"
                            else:
                                data["message"]="cant join user is already in this session"
                        else:
                            data["message"]="there isnt a session with this name"
                        print(data["message"])
                    else:
                        data["message"]="user already in a session"

                elif(command[0]=="exit_session"):
                    """
                        the if statement checks if the command is to exit a session, this command takes no arguments
                        the server checks if the user is in a session and removes the user from the session and from the active users list
                    """
                    sessname=self.session
                    data={"message":"",
                          "status":"fail",
                          "data":None}
                    if(self.session==None):
                        data["message"]="user isnt in a session"
                    else:
                        if(self.db_manager.Does_Sess_Exist(sessname)==True):
                            if(self.db_manager.Is_User_in_sess(self.username,sessname)==True):
                                self.db_manager.Remove_Active_User(self.username,sessname)
                                self.session=None
                                data["message"]="removed user from session"
                                data["status"]="success"
                            else:
                                data["message"]="user isnt in this session"
                        else:
                            data["message"]="session doesnt exist"
                elif(command[0]=="load_file"):
                    """
                        the if statement checks if the command is to load a file, this command takes 1 argument: file name
                        the server checks if the user is in a session and if the file is already loaded in the session
                        and returns an error in the specified cases
                        or broadcasts the shapes to all users in the session
                    """
                    ufileName=command[1]
                    if(self.session==None and self.session not in self.Session.keys()):
                        data={"message":"create session before loading file",
                            "status":"fail",
                            "data":None}
                    else:
                        if(len(self.Session[self.session].shapes) != 0):
                            data={"message":"file is already loaded",
                                "status":"fail",
                                "data":None}
                        else:
                            ffileName = os.path.abspath(os.path.join(self.workingFolder, "assests", ufileName))
                            if self.Session[self.session].LoadFile(ffileName):                            
                                data={"message":"file loaded",
                                    "status":"success",
                                    "data":None}
                                self.Broadcast(None,self.Session[self.session].shapes,datatype="shape_list",send2self=True)

                            else:
                                data={"message":"Error",
                                    "status":"fail",
                                    "data":None}
                elif(command[0]=="list_files"):
                    """
                        the if statement checks if the command is to list all files in the assests folder which are filtered by the .avsf suffix
                        the server checks if the user is in a session and if the session is already created
                    """
                    if(self.session==None and self.session not in self.Session.keys()):
                        data={"message":"create session before list files",
                            "status":"fail",
                            "data":None}
                    else:
                        suffix = ".avsf"
                        files = [f for f in os.listdir(os.path.abspath(os.path.join(self.workingFolder, "assests"))) if f.endswith(suffix)]
                        data = {"message": "list of files:",
                                "status": "success",
                                "data":{"datatype":"list_files",
                                    "content":files}
                                }
                elif(command[0]=="save_file"):
                    """
                        the if statement checks if the command is to save a file, this command takes 1 argument: file name
                        the file is saved in the asset folder by the file name
                    """
                    if(len(command[1:]) == 1):
                        ufileName=command[1]
                        if(self.session==None and self.session not in self.Session.keys()):
                            data={"message":"create session before saving file",
                                "status":"fail",
                                "data":None}
                        else:
                            ffileName = os.path.abspath(os.path.join(self.workingFolder, "assests", ufileName))
                            if self.Session[self.session].SaveFile(ffileName):                            
                                data={"message":"file saved",
                                    "status":"success",
                                    "data":None}
                                self.Broadcast(None,self.Session[self.session].shapes,datatype="shape_list",send2self=True)
                            else:
                                data={"message":"Error",
                                    "status":"fail",
                                    "data":None}
                    else:
                        data={"message":"file name not provided",
                              "status":"fail",
                              "data":None}

                            
                elif(command[0]=="print_shapes"):
                    """
                        the if statement checks if the command is to print all shapes in the session
                        this command returns a shape list to the user
                    """
                    if(self.session==None and self.session not in self.Session.keys()):
                        data={"message":"cannot print shapes if not in session",
                            "status":"fail",
                            "data":None}  
                    else:
                        shapeD=self.Session[self.session].shapes                     
                        data={"message":"shapes are",
                            "status":"success",
                            "data":{"datatype":"shape_list",
                                    "content":shapeD}
                             }


                elif(command[0]=="delete_shape"):
                    """
                        the if statement checks if the command is to delete a shape in the session
                        this command takes 1 argument: shape ID
                        the server checks if the user is in a session and if the session is already created
                        and returns an error in the specified cases
                        or broadcasts the shapes to all users in the session
                    """
                    if(self.session==None and self.session not in self.Session.keys()):
                        data={"message":"cannot delete shapes if not in session",
                            "status":"fail",
                            "data":None}  
                    else:
                        if(command[1] is not None):
                            deletedShape=self.Session[self.session].DeleteShape(command[1])
                            if(deletedShape is not None):
                                data={"message":"shape deleted",
                                    "status":"success",
                                    "data":None}
                                self.Broadcast(None,deletedShape,datatype="shape_list",send2self=True)
                            else:
                                data={"message":"no shape with such id",
                                    "status":"fail",
                                    "data":None}
                        else:
                            data={"message":"please provide shapeiD",
                                "status":"fail",
                                "data":None}
                                             
                elif(command[0] == "add_shape"):
                    """
                        the if statement checks if the command is to add a shape in the session
                        this command takes 1 argument: shape string in a predefined format in the class shape
                        the server checks if the user is in a session and if the session is already created
                        and returns an error in the specified cases
                        or broadcasts the shapes to all users in the session
                    """
                    if(self.session==None and self.session not in self.Session.keys()):
                        data={"message":"cannot add shapes if not in session",
                            "status":"fail",
                            "data":None}  
                    else:
                        line=' '.join(command[1:])
                        addedShape=self.Session[self.session].AddShape(line)
                        if(addedShape is not None):
                            data={"message":"shape added",
                                "status":"success",
                                "data":None}
                            self.Broadcast("Broadcast Add Shape",addedShape,datatype="shape_list",send2self=True)
                        else:
                            data={"message":"not added",
                                "status":"fail",
                                "data":None}
                elif(command[0]=="move_shape"):
                    """
                        the if statement checks if the command is to move a shape in the session
                        this command takes 3 arguments: shape ID, x move distance, y move distance
                        the server checks if the user is in a session and if the session is already created
                        and returns an error in the specified cases
                        or broadcasts the shapes to all users in the session
                    """
                    if(self.session==None and self.session not in self.Session.keys()):
                        data={"message":"cannot move shapes if not in session",
                            "status":"fail",
                            "data":None}  
                    else:
                        if(len(command[1:]) == 3):
                            changeShape=self.Session[self.session].MoveShape(command[1],command[2],command[3])
                            if(changeShape is not None):
                                data={"message":"moved shape",
                                      "status":"success",
                                      "data":None}
                                self.Broadcast(None,changeShape,datatype="shape_list",send2self=True)
                            else:
                                data={"message":"error",
                                      "status":"fail",
                                      "data":None}
                        else:
                            data={"message":"missing arguments",
                                      "status":"fail",
                                      "data":None}
                elif(command[0]=="scale_shape"):
                    """
                        the if statement checks if the command is to scale a shape in the session
                        this command takes 2 arguments: shape ID, scale factor and multiplies the vertexes of the shape by the scale factor
                        the server checks if the user is in a session and if the session is already created
                        and returns an error in the specified cases
                        or broadcasts the shapes to all users in the session
                    """
                    if(self.session==None and self.session not in self.Session.keys()):
                        data={"message":"cannot scale shapes if not in session",
                            "status":"fail",
                            "data":None}  
                    else:
                        if(len(command[1:]) == 2):
                            changeShape=self.Session[self.session].ScaleShape(command[1],command[2])
                            if(changeShape is not None):
                                data={"message":"scale shape",
                                      "status":"success",
                                      "data":None}  
                                self.Broadcast(None,changeShape,datatype="shape_list",send2self=True)
                            else:
                                data={"message":"error",
                                      "status":"fail",
                                      "data":None}
                        else:
                            data={"message":"missing arguments",
                                      "status":"fail",
                                      "data":None}    
                elif(command[0]=="rotate_shape"):
                    """
                        the if statement checks if the command is to rotate a shape in the session
                        this command takes 2 arguments: shape ID, rotation angle and recalculates the shape by the rotation angle
                        the server checks if the user is in a session and if the session is already created
                        and returns an error in the specified cases
                        or broadcasts the shapes to all users in the session
                    """
                    if(self.session==None and self.session not in self.Session.keys()):
                        data={"message":"cannot rotate shapes if not in session",
                            "status":"fail",
                            "data":None}  
                    else:
                        if(len(command[1:]) == 2):
                            changeShape=self.Session[self.session].RotateShape(command[1],command[2])
                            if(changeShape is not None):
                                data={"message":"rotate shape",
                                      "status":"success",
                                      "data":None}  
                                self.Broadcast(None,changeShape,datatype="shape_list",send2self=True)
                            else:
                                data={"message":"error",
                                      "status":"fail",
                                      "data":None}
                        else:
                            data={"message":"missing arguments",
                                      "status":"fail",
                                      "data":None}
                              


                else:
                    # Echo back the message
                    data={"message":"[echo]"+ messagestr,
                        "status":"success",
                        "data":None}
                    

                jData=json.dumps(data,cls=ShapeJsonEncoder)
                self.client_socket.send(jData)
            
            except Exception as e:
                print("error",e)
                break

        print(f"Connection from {self.address} closed")
        self.db_manager.Remove_Active_User(self.username,self.session)
        self.client_socket.close()
        self.clients.remove(self)

    def start_client_thread(self):
        """
            This function starts the client thread.
        """
        self.client_thread.start()



def ValidateLogin(username,password,db_manager):
    """
        This function validates the login credentials of a user by checking the stored password hash against the entered password hash.
    """
    print("Validate Login", username," ", password)   
    stored_salt = db_manager.GetSalt(username)
    stored_pwd = db_manager.GetPassword(username)
    hashed_entered_pwd=db_manager.HashPassword(password,stored_salt.encode('utf-8')) 
    
    if(stored_pwd==hashed_entered_pwd):
        print("ok")
        return True
    else:
        print("wrong password")
        return False



"""
    This class is used to parse the boolean command line arguments for the server
"""
class SslAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, True)

def parse_arguments():
    """
        This function parses the command line arguments for the server.
    """
    parser = argparse.ArgumentParser(description='Parse ssl')
    parser.add_argument("--use_ssl", type=bool,action=SslAction,nargs=0,default=False, help='use ssl protocol for socket or no')
    return parser.parse_args()


def main():

    args = parse_arguments()

    if args.use_ssl:
        print("server will use ssl")
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile="server.crt", keyfile="server.key")

    """
        detecting the host's address and his IP, based on where the server application is ran
    """
    ip_address = socket.gethostbyname(socket.gethostname())
    ip_address = ipaddress.ip_address(ip_address)

    """
        creating a database manager object to manage the database
        creating a server socket object to listen for incoming connections on port 1234
        defining the maximum amount of connections and the time window for connection attempts
    """
    db_manager=DatabaseManager()
    server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind((str(ip_address),1234))
    server_socket.listen(5)
    print(f"server listening")
    clients=[]
    clients_lock=Lock()

    MAX_CONNECTIONS = 100
    CONNECTION_TIME_WINDOW = 60  # 1 minute
    connection_attempts = defaultdict(list)

    def clean_old_connections(address):
        """
            This function is a part of the ddos protection proccess, it cleans the history of connections from the connection_attempts dictionary.
            based on how long ago was the connection attempt:
            if the connection attempt was more than 1 minute ago it will be removed from the list
        """
        current_time = time()
        connection_attempts[address] = [
            timestamp for timestamp in connection_attempts[address]
            if current_time - timestamp < CONNECTION_TIME_WINDOW
        ]

    """
        the while loop is responsible for accepting incoming connections and creating a new client object for each connection 
        appending it to the global clients list and starting that clients thread
        while also preventingand checking for a dddos attack by limiting the amount of connections from the same IP address
        if the option is selected the server will use ssl protocol for the socket
    """
    while True:
        client_socket, address = server_socket.accept()
        address=address[0]
        print("Accepted connection from", address)
        with clients_lock:
            clean_old_connections(address)
            if len(connection_attempts[address]) >= MAX_CONNECTIONS:
                print(f"Too many connections from {address}. Connection denied.")
                client_socket.close()
                continue
            connection_attempts[address].append(time())
        if args.use_ssl:
            try:
                client_socket = context.wrap_socket(client_socket, server_side=True)
            except ssl.SSLError as e:
                print(f"SSL error: {e}")
                client_socket.close()
                continue
        client_socket = ProtocolSocketWrapper(client_socket)
        client = cClient(client_socket, address, clients, db_manager)
        with clients_lock:
            clients.append(client)

        client.start_client_thread()


if __name__ == '__main__' :
    main()