import sqlite3
import bcrypt
import argparse
import socket
import threading
import ssl
import ipaddress
import sys, time

def receive_messages(client_socket):
    while True:
        try:
            # Receive message from server
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print("Received message from server:", message)
        except Exception as e:
            print("Error receiving message:", e)
            break

def send_user(client_socket,username,password):
    login=username+','+password
    client_socket.send(login.encode('utf-8'))
    
    time.sleep(2)
    while True:
        try:
            # Input message from the user
            message=input("enter you command : ")
            if(message=="kuku"):
                print("sefdg")
            elif(message=="sign up"):
                client_socket.send(message.encode('utf-8'))
                username=input("enter username : ")
                password=input("enter password : ")
                message=username+','+password
                client_socket.send(message.encode('utf-8'))
            else:
                client_socket.send(message.encode('utf-8'))
            time.sleep(1)
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

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(ssl_client_socket,))
    receive_thread.start()
    threads.append(receive_thread)
    
    # Start a thread to send messages to the server
    send_thread = threading.Thread(target=send_user, args=(ssl_client_socket,args.username,args.password,))
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

