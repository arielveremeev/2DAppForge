import sqlite3
import bcrypt
import socket
import threading

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
    # Server configuration
    host = '192.168.0.204'
    port = 1234
    
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()
    
    # Start a thread to send messages to the server
    send_thread = threading.Thread(target=send_user, args=(client_socket,))
    send_thread.start()

if __name__ == "__main__":
    main()

