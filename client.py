import sqlite3
import bcrypt
import socket
import threading
import ssl

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

def send_user(client_socket):
    while True:
        try:
            # Input message from the user
            username = input("Enter username: ")
            password= input("Enter password: ")
            message=username+','+password
            if message == 'exit':
                break
            # Send message to the server
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print("Error sending message:", e)
            break

def main():
    # Create an SSL context with default settings and disable certificate verification
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    # Server configuration
    host = '192.168.0.204'
    port = 1234
    
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    ssl_client_socket =  context.wrap_socket(client_socket, server_hostname=host)

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(ssl_client_socket,))
    receive_thread.start()
    
    # Start a thread to send messages to the server
    send_thread = threading.Thread(target=send_user, args=(ssl_client_socket,))
    send_thread.start()

if __name__ == "__main__":
    main()

