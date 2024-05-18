import sqlite3
import bcrypt
from datetime import date


class DatabaseManager:
    def __init__(self, db_name='app_database.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect('app_database.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        debug=False
        if(debug==False):
            self.cursor.execute("DROP TABLE IF EXISTS active_session_users")
            self.cursor.execute("DROP TABLE IF EXISTS sessions")

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
        maxpart=session[1]
        owner=session[2]
        credate=str(date.today())
        count=self.cursor.execute("SELECT count(*) FROM sessions WHERE name=(?)",(name,)) 
        for row in count:
            if(row[0]!=0):
                print("a session with this name already exists")
                return False
            else:
                self.cursor.execute('INSERT INTO sessions(name,owner,creation_date,max_participants) VALUES (?,?,?,?)',(name,owner,credate,maxpart))
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
        cursor=self.cursor.execute("SELECT username FROM active_session_users WHERE username=(?) and session=(?)",(username,sessname))
        print(username)
        print(sessname)
        row=cursor.fetchone()
        if(row is not None):
            if(len(row)==0):
                return False
            return True
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

    def Insert_Active_User(self,username,sessname):
        self.cursor.execute('INSERT INTO active_session_users(username,session) VALUES (?,?)',(username,sessname))
        self.conn.commit()

    def Remove_Active_User(self,username,sessname):
        self.cursor.execute("DELETE FROM active_session_users WHERE username = (?) and session = (?)",(username,sessname,))
        self.conn.commit()


    def Session_users(self,sessname):
        cursor=self.cursor.execute("SELECT username FROM active_session_users WHERE session = (?)",(sessname,))
        Users=[]
        for usr in cursor:
            print(usr[0])
            Users.append(usr[0])

        return Users

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