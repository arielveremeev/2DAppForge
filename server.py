import sqlite3
import bcrypt
import argparse
import socket
import threading
import ssl
import ipaddress
from datetime import date
import json

class DatabaseManager:
    def __init__(self, db_name='app_database.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect('app_database.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("DELETE FROM active_session_users")
        self.cursor.execute("DROP TABLE IF EXISTS active_session_users")

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                salt TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                owner TEXT NOT NULL,
                creation_date TEXT NOT NULL,
                max_participants TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_session_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                session TEXT NOT NULL
            )
        ''')
    
        
        self.conn.commit()
        


    def insert_user(self, username, password):
        #inserts new user into the databse
        count=self.cursor.execute("SELECT count(*) FROM users WHERE username=(?)",(username,)) 
        for row in count:
            if(row[0] != 0):
                print("already exists")
            else:
                salt = bcrypt.gensalt()
                hashed_pwd = self.HashPassword(password,salt)
                self.cursor.execute('INSERT INTO users (username, password,salt) VALUES (?, ?, ?)', (username, hashed_pwd ,salt.decode('utf-8'),))
                self.conn.commit()

    def Create_Session(self,session):
        name=session[0]
        sesstype=session[1]
        maxpart=session[2]
        owner=session[3]
        credate=str(date.today())
        count=self.cursor.execute("SELECT count(*) FROM sessions WHERE name=(?)",(name,)) 
        for row in count:
            if(row[0]!=0):
                print("a session with this name already exists")
                return False
            else:
                self.cursor.execute('INSERT INTO sessions(name,type,owner,creation_date,max_participants) VALUES (?,?,?,?,?)',(name,sesstype,owner,credate,maxpart))
                self.conn.commit()
                print("session created")
                return True

    def Print_sessions(self):
        cursor=self.cursor.execute("SELECT name,owner FROM sessions")
        for sess in cursor:
            print(sess)


    def Get_Sessions(self):
        sessions=[]
        cursor=self.cursor.execute("SELECT name,owner FROM sessions")
        for sess in cursor:
            print(sess)
            sessions.append(sess)
        return sessions

    def Does_Sess_Exist(self,name):
        cursor=self.cursor.execute("SELECT name FROM sessions")
        for sess in cursor:
            if(name==sess[0]):
                print("session with this name exists")
                return True
        return False

    def Is_User_in_sess(self,username,sessname):
        cursor=self.cursor.execute("SELECT username,session FROM active_session_users")
        print(username)
        print(sessname)
        for user in cursor:
            print(user[0])
            print(user[1])
            if(username==user[0] and sessname==user[1]):
                print('user already in this session')
                return True
            else:
                print('user isnt in this session')
                return False
        return False
    def Can_Join(self,sessname):
        if(self.Does_Sess_Exist(sessname)==True):
            cursor=self.cursor.execute('SELECT session FROM active_session_users WHERE session= (?)',(sessname,))
            rows=cursor.fetchall()
            if(len(rows)==0):
                return True
            count=len(rows)
            maxpart_query=self.cursor.execute("SELECT max_participants FROM sessions WHERE name= (?)",(sessname,))
            maxpart_row=maxpart_query.fetchone()
            if(maxpart_row is not None):
                maxpart=int(maxpart_row[0])

            if(count<maxpart):
                return True
            else:
                return False
        else:
            print('session doesnt exist')
            return False


    def Join_Session(self,username,sessname):
        if(self.Does_Sess_Exist(sessname)==True):
            if(self.Is_User_in_sess(username,sessname)==False):
                if(self.Can_Join(sessname)==True):
                    self.cursor.execute('INSERT INTO active_session_users(username,session) VALUES (?,?)',(username,sessname))
                    self.conn.commit()
                    return True            
                else:
                    print("cant join due to max participant amount")
                    return False
            else:
                print("cant join user is already in this session")
                return False
        else:
            print("there isnt a session with this name")
            return False

    def PrintUsers(self):
        #print all current registered users in the database
        cursor=self.cursor.execute("SELECT username,password,salt FROM users")
        for row in cursor:
            print( row[0])
            print( row[1],"\n")
            print( row[2],"\n")
    
    def GetUsers(self):
        Users=[]
        cursor=self.cursor.execute("SELECT username FROM users")
        for usr in cursor:
            print(usr[0])
            Users.append(usr[0])
        return Users

    def IfExists(self,username):
        #check if the username exists by username
        cursor=self.cursor.execute("SELECT username,password FROM users")
        for row in cursor:
            if(username==row[0]):
                print("username already exists")
                return True
        return False

    def GetPassword(self,username):
        #gets password according to username
        cursor=self.cursor.execute("SELECT password FROM users WHERE username=(?) ",(username,))
        if(cursor==" "):
            print("user doesnt exist")
        for row in cursor:
            return row[0]
    
    def GetSalt(self,username):
        cursor=self.cursor.execute("SELECT salt FROM users WHERE username=(?) ",(username,))
        if(cursor==" "):
            print("user doesnt exist")
        for row in cursor:
            return row[0]

    def HashPassword(self,password,salt):
        password=password.encode('utf-8')
        hashed = bcrypt.hashpw(password,salt)
        return hashed

    def close_connection(self):
        # Close the database connection
        self.conn.close()

    def Clear(self):
        #clears the database
        self.cursor.execute("DELETE FROM users")

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
                if(db_manager.Join_Session(username,session)==True):
                    data={"message":"successfully joined session ",
                        "status":"success",
                        "data":None}
                else:
                    data={"message":"couldnt join session",
                        "status":"fail",
                        "data":None}

            else:
                # Echo back the message
                data={"message":messagestr,
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