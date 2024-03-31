import argparse
import socket
import threading
import ssl
import ipaddress
from datetime import date
import json
from DatabaseManager import DatabaseManager 


class cClient():
    def __init__(self, client_socket, address, clients, db_manager):
        self.client_socket = client_socket
        self.address = address
        self.clients = clients
        self.db_manager = db_manager
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
                    self.ssl_client_socket.sendall(jData.encode('utf-8'))
        
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
                        c.client_socket.send(jData.encode('utf-8'))
                    continue
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
                    if(self.db_manager.Create_Session(session)==False):
                        data={"message":"session not created, session with this name already exists",
                            "status":"fail",
                            "data":None}
                    else:
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
                    session=command[1]
                    data={"message":"",
                        "status":"fail",
                        "data":None}
                    if(self.db_manager.Does_Sess_Exist(session)==True):
                        if(self.db_manager.Is_User_in_sess(username,session)==False):
                            if(self.db_manager.Can_Join(session)==True):
                                self.db_manager.Insert_Active_User(username,session)
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
                    # Echo back the message
                    data={"message":"[echo]"+ messagestr,
                        "status":"success",
                        "data":None}
                    

                jData=json.dumps(data)
                self.client_socket.sendall(jData.encode('utf-8'))
            
            except Exception as e:
                print("error",e)
                break

        print(f"Connection from {self.address} closed")
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