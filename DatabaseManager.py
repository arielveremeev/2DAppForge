import sqlite3
import bcrypt
from datetime import date
import re
from functools import wraps


def detect_sql_injection(param):
    """
    Detects potential SQL injection patterns in a parameter.
    """
    sql_injection_pattern = re.compile(
        r'(--|;|\'|\"|\/\*|\*\/|xp_|\bSELECT\b|\bUPDATE\b|\bDELETE\b|\bINSERT\b|\bDROP\b|\bUNION\b|\bALTER\b|\bEXEC\b)',
        re.IGNORECASE
    )
    if sql_injection_pattern.search(str(param)):
        return True
    return False

def sql_injection_safe(func):
    """
    Static method decorator to check for SQL injection in function parameters.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        for arg in args:
            if isinstance(arg, (list, tuple)):
                for item in arg:
                    if detect_sql_injection(item):
                        raise ValueError("Potential SQL injection detected in arguments.")
            else:
                if detect_sql_injection(arg):
                    raise ValueError("Potential SQL injection detected in arguments.")

        for key, value in kwargs.items():
            if isinstance(value, (list, tuple)):
                for item in value:
                    if detect_sql_injection(item):
                        raise ValueError(f"Potential SQL injection detected in keyword argument '{key}'.")
            else:
                if detect_sql_injection(value):
                    raise ValueError(f"Potential SQL injection detected in keyword argument '{key}'.")

        return func(*args, **kwargs)
    return wrapper

class DatabaseManager:
    """class for operating with all the tables/databases"""
    def __init__(self, db_name='app_database.db'):
        """class constructor, constructs sqlite3 database from file whose name is saved in db_name and creates tables"""
        self.db_name = db_name
        self.conn = sqlite3.connect('app_database.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """function that creates the following tables if they dont exist: users,session,active_session_users
           session and active_session_users are cleared on each new run of the server"""
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
        





    @sql_injection_safe
    def insert_user(self, username, password):
        """
        The `insert_user` function checks if a username already exists in the database, and if not, inserts
        the username, hashed password, and salt into the `users` table.
        
        """
        count=self.cursor.execute("SELECT count(*) FROM users WHERE username=(?)",(username,)) 
        for row in count:
            if(row[0] != 0):
                print("already exists")
            else:
                salt = bcrypt.gensalt()
                hashed_pwd = self.HashPassword(password,salt)
                self.cursor.execute('INSERT INTO users (username, password,salt) VALUES (?, ?, ?)', (username, hashed_pwd ,salt.decode('utf-8'),))
                self.conn.commit()

    @sql_injection_safe
    def Create_Session(self,session):
        """
        The function `Create_Session` checks if a session with a given name already exists in a database
        table and creates a new session if it doesn't exist.
        
        """
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
    
    
    @sql_injection_safe
    def Delete_session(self,session):
        """
        The function `Delete_session` deletes a session from a database table if it exists and returns True,
        otherwise returns False.
        
        """
        cursor=self.cursor.execute("SELECT name FROM sessions WHERE name=(?)",(session,))
        result=cursor.fetchone()
        if result:
            cursor.execute("DELETE FROM sessions WHERE name=(?)",(session,))
            print(session)
            print(result)
            self.conn.commit()
            return True
        return False


    def Print_sessions(self):
        """
        The function `Print_sessions` is for debbuging purposes, it retrieves and prints the names and owners of sessions from a database
        table.
        """
        cursor=self.cursor.execute("SELECT name,owner FROM sessions")
        for sess in cursor:
            print(sess)


    def Get_Sessions(self):
        """
        The function `Get_Sessions` retrieves session names and owners from a database table and returns
        them as a list.
        :return: A list of tuples containing the name and owner of each session from the database table
        "sessions" is being returned.
        """
        sessions=[]
        cursor=self.cursor.execute("SELECT name,owner FROM sessions")
        for sess in cursor:
            print(sess)
            sessions.append(sess)
        return sessions

    def Does_Sess_Exist(self,name):
        """
        The function checks if a session with a given name exists in a database table.
        
        """
        cursor=self.cursor.execute("SELECT name FROM sessions")
        for sess in cursor:
            if(name==sess[0]):
                print("session with this name exists")
                return True
        return False

    @sql_injection_safe
    def Is_User_in_sess(self,username,sessname):
        """
        This function checks if a user is in an active session by querying a database table.
        
        """
        cursor=self.cursor.execute("SELECT username FROM active_session_users WHERE username=(?) and session=(?)",(username,sessname))
        print(username)
        print(sessname)
        row=cursor.fetchone()
        if(row is not None):
            if(len(row)==0):
                return False
            return True
        return False
    
    @sql_injection_safe
    def Can_Join(self,sessname):
        """
        This Python function checks if a user can join a session based on the number of participants already
        in the session and the maximum allowed participants.
        
        """
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

    @sql_injection_safe
    def Insert_Active_User(self,username,sessname):
        """
        The function `Insert_Active_User` inserts a username and session name into a table called
        `active_session_users`.
        
        """
        self.cursor.execute('INSERT INTO active_session_users(username,session) VALUES (?,?)',(username,sessname))
        self.conn.commit()

    @sql_injection_safe
    def Remove_Active_User(self,username,sessname):
        """
        The function `Remove_Active_User` deletes a record from the `active_session_users` table based on
        the provided `username` and `sessname`.
        
        """
        self.cursor.execute("DELETE FROM active_session_users WHERE username = (?) and session = (?)",(username,sessname,))
        self.conn.commit()

    @sql_injection_safe
    def Session_users(self,sessname):
        """
        This Python function retrieves a list of usernames associated with a specific session from a
        database table.
        
        """
        cursor=self.cursor.execute("SELECT username FROM active_session_users WHERE session = (?)",(sessname,))
        Users=[]
        for usr in cursor:
            print(usr[0])
            Users.append(usr[0])

        return Users

    def PrintUsers(self):
        """
        The function `PrintUsers` is for debbuging purposesn,it retrieves and prints the usernames, passwords, and salts of users from a
        database.
        """
        cursor=self.cursor.execute("SELECT username,password,salt FROM users")
        for row in cursor:
            print( row[0])
            print( row[1],"\n")
            print( row[2],"\n")
    
    def GetUsers(self):
        """
        This function retrieves a list of usernames from a database table named "users".
        :return: The `GetUsers` method is returning a list of usernames from the `users` table in the
        database.
        """
        Users=[]
        cursor=self.cursor.execute("SELECT username FROM users")
        for usr in cursor:
            print(usr[0])
            Users.append(usr[0])
        return Users

    def IfExists(self,username):
        """
        The function checks if a username already exists in a database table and returns True if it does,
        otherwise returns False.
        
        """
        cursor=self.cursor.execute("SELECT username,password FROM users")
        for row in cursor:
            if(username==row[0]):
                print("username already exists")
                return True
        return False

    @sql_injection_safe
    def GetPassword(self,username):
        """
        The function `GetPassword` retrieves the password associated with a given username from a database
        table.
        
        """
        cursor=self.cursor.execute("SELECT password FROM users WHERE username=(?) ",(username,))
        if(cursor==" "):
            print("user doesnt exist")
        for row in cursor:
            return row[0]
    
    @sql_injection_safe
    def GetSalt(self,username):
        """
        The function `GetSalt` retrieves the salt value associated with a given username from a database
        table.
        
        """
        cursor=self.cursor.execute("SELECT salt FROM users WHERE username=(?) ",(username,))
        if(cursor==" "):
            print("user doesnt exist")
        for row in cursor:
            return row[0]

    def HashPassword(self,password,salt):
        """
        The function HashPassword takes a password and a salt as input, encodes the password, hashes it
        using bcrypt, and returns the hashed password.
        
        """
        password=password.encode('utf-8')
        hashed = bcrypt.hashpw(password,salt)
        return hashed

    def close_connection(self):
        """
        The `close_connection` function closes the database connection.
        """
        self.conn.close()

    def Clear(self):
        """
        The `Clear` function in Python clears the database by executing a SQL query to delete all records
        from the "users" table.
        """
        self.cursor.execute("DELETE FROM users")