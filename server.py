import argparse
import socket
import threading
import ssl
import ipaddress
from datetime import date
import json
import os
from DatabaseManager import DatabaseManager 
from shapes import Shape
from shapes import CreateShape
from shapes import ShapeJsonEncoder
from collections import defaultdict
from threading import Thread,Lock
from time import time

class cSession():
    def __init__(self,name):
        self.name = name
        self.shapes={}
        self.shapeID=0
        self.filename=None
        self.locker=threading.Lock()

    def FileOpener(self,path):
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
        with self.locker:
            SiID=int(ssid)
            if(SiID in self.shapes.keys()): 
                deletedShape={-SiID:self.shapes[SiID]}
                del self.shapes[SiID]
                return deletedShape
            return None
    
    def AddShape(self,line) ->dict:
        with self.locker:
            if(line is not None and type(line) is str):
                self.shapeID+=1
                addedShape = {self.shapeID:CreateShape(line)}
                self.shapes.update(addedShape)
                return addedShape
            return None
    
    def SaveFile(self,path):
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
        self.shapes[ssid].MoveShape(float(Mx), float(My))
        return True

    @shape_operation
    def ScaleShape(self, ssid, Sf:str) -> dict:
        self.shapes[ssid].ScaleShape(float(Sf))
        return True

    @shape_operation
    def RotateShape(self, ssid, ra:str) -> dict:
        self.shapes[ssid].RotateShape(float(ra))
        return True


class cClient():
    Session ={}
    workingFolder = os.getcwd()
    def __init__(self, client_socket, address, clients, db_manager):
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
        self.client_socket.close()

    def safe_send(self, data):
        with self.lock:
            self.client_socket.send(data)

    
    def Broadcast(self,msg2send,data2send,datatype:str,send2self:bool = False,refresh :bool=False):
        """ possible/awaited data types:
            user_list,
            session_list,
            shape_list,
            echo_text"""    
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
                    c.safe_send(jData.encode('utf-8'))
            else:
                if(self.session == c.session and (self.client_socket != c.client_socket or send2self==True)):
                    c.safe_send(jData.encode('utf-8'))
        



    def handle_client(self):
        print(f"accepted connection from {self.address}")
        #pre login while
        while True:
            data = self.client_socket.recv(1024)
            print ("recived message len",len(data) if data is None else 0)
            if not data:
                break

            messagestr=data.decode('utf-8')
            user=messagestr.split(',')
            # This Python code snippet is implementing a basic user authentication system. It checks
            # if the user input is either "sign_up" or "login". If the input is "sign_up", it checks
            # if the correct number of arguments are provided, then extracts the username and password
            # from the input. It then checks if the username already exists in the database, and if
            # not, inserts the user into the database. Finally, it sends a response message back to
            # the client.
            if(user[0]=="sign_up" or user[0]=="login"):
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
                    self.client_socket.sendall(jData.encode('utf-8'))
        
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
                            self.client_socket.sendall(jData.encode('utf-8'))
                            self.is_connection_live=True
                            password=""
                            break
                        else:
                            jData=json.dumps(data)
                            self.client_socket.sendall(jData.encode('utf-8'))
            else:
                data={"message":"no such command please log in to use other commands",
                    "status":"fail",
                    "data":None}
                jData=json.dumps(data)
                self.client_socket.sendall(jData.encode('utf-8'))
        
        #after login while(all general commands)
        while self.is_connection_live:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    self.is_connection_live=False
                    break
                messagestr = data.decode('utf-8')
                command=messagestr.split(',')
                if len(command)==0:
                    continue
                #message broadcasting
                print("recived command ",command[0])
                # The above Python code snippet is checking if the first element of the `command` list is equal to
                # "all". If it is, it prints "contains all" and then proceeds to check if the `self.session` is not
                # None. If the length of the `command` list excluding the first element is 0, it creates a response
                # dictionary with a message indicating to be more precise. Otherwise, it constructs a message using
                # the `self.username` and the remaining elements of the `command` list, broadcasts this message using
                # the `Broadcast` method, and continues to the next iteration.
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
                #printing all users registered in the databse
                elif(command[0]=="print_users"):
                    #db_manager.PrintUsers()
                    Users=[]
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
                #create a new session
                elif(command[0]=="create_session"):
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
                
                #print all registered sessions
                elif(command[0]=="print_sessions"):
                    sessions=self.db_manager.Get_Sessions()
                    data={"message":"sessions and owners are : ",
                        "status":"success",
                        "data":{"datatype":"session_list",
                                "content":sessions}
                         }
                #join an existing session
                elif(command[0]=="join_session"):
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
                self.client_socket.sendall(jData.encode('utf-8'))
            
            except Exception as e:
                print("error",e)
                break

        print(f"Connection from {self.address} closed")
        self.db_manager.Remove_Active_User(self.username,self.session)
        self.client_socket.close()
        self.clients.remove(self)

    def start_client_thread(self):
        self.client_thread.start()



def ValidateLogin(username,password,db_manager):
#checks if the username matches the password written in the database
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



class SslAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, True)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Parse ssl')
    parser.add_argument("--use_ssl", type=bool,action=SslAction,nargs=0,default=False, help='use ssl protocol for socket or no')
    return parser.parse_args()


def main():

    args = parse_arguments()

    if args.use_ssl:
        print("server will use ssl")
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile="server.crt", keyfile="server.key")

    ip_address = socket.gethostbyname(socket.gethostname())
    ip_address = ipaddress.ip_address(ip_address)

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
        current_time = time()
        connection_attempts[address] = [
            timestamp for timestamp in connection_attempts[address]
            if current_time - timestamp < CONNECTION_TIME_WINDOW
        ]

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
        client = cClient(client_socket, address, clients, db_manager)
        with clients_lock:
            clients.append(client)

        client.start_client_thread()


if __name__ == '__main__' :
    main()