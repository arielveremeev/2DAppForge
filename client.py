import sqlite3
import bcrypt
import argparse
import socket
import threading
import ssl
import ipaddress

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
    while True:
        try:
            # Input message from the user
            message=username+','+password
            if message == 'exit':
                break
            # Send message to the server
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print("Error sending message:", e)
            break

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
    
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    ssl_client_socket =  context.wrap_socket(client_socket, server_hostname=host)

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(ssl_client_socket,))
    receive_thread.start()
    
    # Start a thread to send messages to the server
    send_thread = threading.Thread(target=send_user, args=(ssl_client_socket,args.username,args.password,))
    send_thread.start()

if __name__ == "__main__":
    main()

