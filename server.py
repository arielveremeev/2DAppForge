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

class cSession():
    def __init__(self,name):
        self.name = name
        self.shapes={}
        self.shapeID=0
        self.filename=None

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



class cClient():
    Session ={}
    workingFolder = os.getcwd()
    def __init__(self, client_socket, address, clients, db_manager):
        self.client_socket = client_socket
        self.address = address
        self.clients = clients
        self.db_manager = db_manager
        self.session=None
        self.client_thread = threading.Thread(target=self.handle_client)



    def handle_client(self):
        print(f"accepted connection from {self.address}")
        #pre login while
        while True:
            data = self.client_socket.recv(1024)
            if not data:
                data={'message':"data not sent try again",
                    "status":"success",
                    "data":None}
            messagestr=data.decode('utf-8')
            user=messagestr.split(',')
            if(user[0]=="sign_up" or user[0]=="login"):
                if(user[0]=="sign_up"):
                    if(len(user[1:])!=2):
                        data={'message':"missing arguments for sign up",
                            "status":"fail",
                            "data":None}
                    else:
                        username = user[1]
                        password = user[2]
                        print(username)
                        print(password)
                        if(self.db_manager.IfExists(username)==True):
                            print(f"user already exists")
                            data={'message':"username in use or doesnt exist",
                            "status":"fail",
                            "data":None}
                        else:
                            self.db_manager.insert_user(username,password)
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
                        username = user[1]
                        password = user[2]
                        print(username)
                        print(password)
                        if(self.db_manager.IfExists(username)==False):
                            data={"message":"user doesnt exist",
                                "status":"fail",
                                "data":None}
                        elif(ValidateLogin(username,password,self.db_manager)==True):
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
        while True:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                messagestr = data.decode('utf-8')
                command=messagestr.split(',')
                if len(command)==0:
                    continue
                #message broadcasting
                if "all" == command[0]:
                    print("contains all")
                    if(self.session!=None):
                        if(len(command[1:])==0):
                            data={'message':"be more precise",
                                "status":"fail",
                                "data":None}
                        else:
                            data={'message':' '.join(command[1:]),
                                "status":"success",
                                "data":None}
                            jData=json.dumps(data)
                            for c in self.clients:
                                if(self.session == c.session and self.client_socket != c.client_socket):
                                    c.client_socket.send(jData.encode('utf-8'))
                            continue
                        
                    else:
                        data={'message':"user isnt in session to broadcast",
                                "status":"fail",
                                "data":None}
                #printing all users registered in the databse
                elif(command[0]=="print_users"):
                    #db_manager.PrintUsers()
                    Users=self.db_manager.GetUsers()
                    data={"message":"users are : ",
                        "status":"success",
                        "data":Users}
                #create a new session
                elif(command[0]=="create_session"):
                    session=command[1:]
                    session.append(username)
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
                
                #print all registered sessions
                elif(command[0]=="print_sessions"):
                    sessions=self.db_manager.Get_Sessions()
                    data={"message":"sessions and owners are : ",
                        "status":"success",
                        "data":sessions}
                #join an existing session
                elif(command[0]=="join_session"):
                    sessname=command[1]
                    data={"message":"",
                        "status":"fail",
                        "data":None}
                    if(self.session==None):
                        if(self.db_manager.Does_Sess_Exist(sessname)==True):
                            if(self.db_manager.Is_User_in_sess(username,sessname)==False):
                                if(self.db_manager.Can_Join(sessname)==True):
                                    self.db_manager.Insert_Active_User(username,sessname)
                                    self.session=sessname
                                    data["message"]="successfully joined session"
                                    data["status"]="success"
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
                            if(self.db_manager.Is_User_in_sess(username,sessname)==True):
                                self.db_manager.Remove_Active_User(username,sessname)
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

                            else:
                                data={"message":"Error",
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
                            "data":shapeD}


                elif(command[0]=="delete_shape"):
                    if(command[1] is not None):
                        SiD=int(command[1])
                        if(SiD in self.Session[self.session].shapes.keys()): 
                            del self.Session[self.session].shapes[SiD]  
                            data={"message":"shape deleted",
                                  "status":"success",
                                  "data":None}
                        else:
                            data={"message":"no shape with such id",
                                  "status":"fail",
                                  "data":None}
                    else:
                        data={"message":"please provide shapeiD",
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
        self.db_manager.Remove_Active_User(username,self.session)
        self.client_socket.close()

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




def main():
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
    while True:
        client_socket, address = server_socket.accept()
        print("Accepted connection from", address)
        ssl_client_socket = context.wrap_socket(client_socket, server_side=True)
        client=cClient(ssl_client_socket,address,clients,db_manager)
        clients.append(client)

        client.start_client_thread()


if __name__ == '__main__' :
    main()