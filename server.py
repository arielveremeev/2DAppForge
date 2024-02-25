import sqlite3
import bcrypt
import socket
import threading



class DatabaseManager:
    def __init__(self, db_name='app_database.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect('app_database.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # Create a table to store user data if it doesn't exist
        #self.cursor.execute('''drop table users''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                salt TEXT NOT NULL
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

    def PrintUsers(self):
        #print all current registered users in the database
        cursor=self.cursor.execute("SELECT username,password,salt FROM users")
        for row in cursor:
            print( row[0])
            print( row[1],"\n")
            print( row[2],"\n")

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
        print("from salt", username)
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
    print("Validate Loigin", username," ", password)   
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


    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            user=message.split(",")
            username = user[0]
            password = user[1]
            print(user[0])
            print(user[1])
            if(ValidateLogin(username,password,db_manager)==True):
                print(f"succesfull login from {address}")
            print(f"Received from {address}")

            if "all" in message:
                print("contains all")
                for c in clients:
                    c.send(message.encode('utf-8'))
            else:
                # Echo back the message
                client_socket.sendall(data)
        
        except Exception as e:
            print("error",e)
            break

    print(f"Connection from {address} closed")
    client_socket.close()


def main():
    db_manager=DatabaseManager()
    server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind(("192.168.0.204",1234))
    server_socket.listen(5)
    print(f"server listening")
    clients=[]
    while True:
        client_socket, address = server_socket.accept()
        print("Accepted connection from", address)

        clients.append(client_socket)
        
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address, clients,db_manager))
        client_thread.start()

if __name__ == '__main__' :
    main()