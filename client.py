import sqlite3
import bcrypt
import argparse
import socket
import threading
import ssl
import ipaddress
import sys, time
from datetime import date
import json

def receive_messages(client_socket,event):
    while True:
        try:
            # Receive message from server
            jMessage = client_socket.recv(1024).decode('utf-8')
            if jMessage:
                message=json.loads(jMessage)
                print(message["message"])
                if message["data"] != None:
                    if(type(message["data"]) is dict):
                        for index in message["data"]:
                            data=message["data"][index]
                            print(f"[{index}]:{data}")
                    else:
                        for data in message["data"]:
                            print(data)
            event.set()

        except Exception as e:
            print("Error receiving message:", e)
            break

def send_user(client_socket,event,username = None,password = None):    
    message ="login"
    while True:
        try:
            # Input message from the user
            if message == None:
                message=input(">:")
            command=message.split(" ")
            if(command[0] in ['',' ',""," "]):
                print("wrong input")
                message=None
                continue
            if(command[0]=="sign_up"):
                username=input("enter username : ")
                password=input("enter password : ")
                message=','.join([command[0],username,password])
                username=None
                password=None
            elif(command[0]=="login"):
                if username == None:
                    username=input("enter username : ")
                if password == None:
                    password=input("enter password : ")
                message=','.join([command[0],username,password])
                username=None
                password=None
            else:
                message=','.join(command)
            
            client_socket.send(message.encode('utf-8'))
            message = None
            event.wait()
            event.clear()
        except Exception as e:
            print("Error sending message:", e)
            break

def has_live_threads(threads):
    return True in [t.is_alive() for t in threads]

def parse_arguments():
    parser = argparse.ArgumentParser(description='Parse IP address, username, and password.')
    parser.add_argument("--ip_address", type=str,nargs='?', help='The IP address')
    parser.add_argument("--username", type=str,nargs='?', help='The username')
    parser.add_argument("--password", type=str,nargs='?', help='The password')
    return parser.parse_args()

def main():

    args = parse_arguments()

    if(args.ip_address==None):
        ip_address = socket.gethostbyname(socket.gethostname())
        ip_address = ipaddress.ip_address(ip_address)
        args.ip_address=str(ip_address)
    if(args.username==None and args.password==None):
        args.username=input("enter username : ")
        args.password=input("enter password : ")
    elif(args.username==None and args.password):
        args.username=input("enter username : ")
    elif(args.username and args.password==None):
        args.password=input("enter password : ")

    # Create an SSL context with default settings and disable certificate verification
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    # Server configuration
    host = args.ip_address
    port = 1234
    
    threads = []
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    ssl_client_socket =  context.wrap_socket(client_socket, server_hostname=host)
    
    #create event for thread synchronization
    event=threading.Event()

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(ssl_client_socket,event,))
    receive_thread.start()
    threads.append(receive_thread)
    
    # Start a thread to send messages to the server
    send_thread = threading.Thread(target=send_user, args=(ssl_client_socket,event,args.username,args.password,))
    send_thread.start()
    threads.append(send_thread)

    while has_live_threads(threads):
        try:
            # synchronization timeout of threads kill
            [t.join(1) for t in threads
             if t is not None and t.is_alive()]
        except KeyboardInterrupt:
            # Ctrl-C handling and send kill to threads
            print("Sending kill to threads...")
            for t in threads:
                t.kill_received = True
            ssl_client_socket.close()

    print ("Exited")


if __name__ == "__main__":
    main()

