import argparse
import socket
import threading
import ssl
import ipaddress
from datetime import date
import json
from DatabaseManager import DatabaseManager 


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



def handle_client(client_socket, address, clients,db_manager):
    print(f"accepted connection from {address}")
    #pre login while
    while True:
        data = client_socket.recv(1024)
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
                    if(db_manager.IfExists(username)==True):
                        print(f"user already exists")
                        data={'message':"username in use or doesnt exist",
                        "status":"fail",
                        "data":None}
                    else:
                        db_manager.insert_user(username,password)
                        data={'message':"successfully added user now please login using the same info",
                        "status":"success",
                        "data":None}
                jData=json.dumps(data)
                client_socket.sendall(jData.encode('utf-8'))
    
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
                    if(db_manager.IfExists(username)==False):
                        data={"message":"user doesnt exist",
                            "status":"fail",
                            "data":None}
                    elif(ValidateLogin(username,password,db_manager)==True):
                        data={"message":"succesfull login from"+ str(address),
                                "status":"success",
                                "data":None}
                    else:
                        data={"message":"wrong password try again",
                                "status":"fail",
                                "data":None}
                    if(data.get("status")=="success"):
                        jData=json.dumps(data)
                        client_socket.sendall(jData.encode('utf-8'))
                        break
                    else:
                        jData=json.dumps(data)
                        client_socket.sendall(jData.encode('utf-8'))
        else:
            data={"message":"no such command please log in to use other commands",
                "status":"fail",
                "data":None}
            jData=json.dumps(data)
            client_socket.sendall(jData.encode('utf-8'))
    
    #after login while(all general commands)
    while True:
        try:
            data = client_socket.recv(1024)
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
                for c in clients:
                    c.send(jData.encode('utf-8'))
                continue
            #printing all users registered in the databse
            elif(command[0]=="print_users"):
                #db_manager.PrintUsers()
                Users=db_manager.GetUsers()
                data={"message":"users are : ",
                      "status":"success",
                      "data":Users}
            #create a new session
            elif(command[0]=="create_session"):
                session=command[1:]
                session.append(username)
                if(db_manager.Create_Session(session)==False):
                    data={"message":"session not created, session with this name already exists",
                          "status":"fail",
                          "data":None}
                else:
                    data={"message":"new session created",
                          "status":"success",
                          "data":None}
            
            #print all registered sessions
            elif(command[0]=="print_sessions"):
                sessions=db_manager.Get_Sessions()
                data={"message":"sessions and owners are : ",
                      "status":"success",
                      "data":sessions}
            #join an existing session
            elif(command[0]=="join_session"):
                session=command[1]
                data={"message":"",
                      "status":"fail",
                      "data":None}
                if(db_manager.Does_Sess_Exist(session)==True):
                    if(db_manager.Is_User_in_sess(username,session)==False):
                        if(db_manager.Can_Join(session)==True):
                            db_manager.Insert_Active_User(username,session)
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
            client_socket.sendall(jData.encode('utf-8'))
        
        except Exception as e:
            print("error",e)
            break

    print(f"Connection from {address} closed")
    client_socket.close()


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
        clients.append(ssl_client_socket)
        
        client_thread = threading.Thread(target=handle_client, args=(ssl_client_socket, address, clients,db_manager))
        client_thread.start()

if __name__ == '__main__' :
    main()