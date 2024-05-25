import socket
import struct

class ProtocolSocketWrapper:

    """ProtocolSocketWrapper is a class that implements the following protocol on top of a basic python socket: 
    the protocol is string based, each message starts with the constant length string of the length of the message followed by the body of the message
    """
    def __init__(self, sock=None):
        """
        The `__init__` function initializes a socket object, either creating a new one or using a provided
        socket.
        """
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        """
        The `connect` function establishes a connection to a specified host and port.
        
        """
        """"""
        self.sock.connect((host, port))

    def send(self, msg):
        """
        The `send` function takes a message, adds the length of the message to the beginning of the message formatted as {takes exactly 10 spaces},
        and then sends the encoded message over a socket.
        
        """
        
        msg = f'{len(msg):<{10}}' + msg
        self.sock.sendall(msg.encode('utf-8'))

    def recv(self):
        """
        The function `recv` recives a message by a length defined by its prefix(exactly 10 bytes)
        first call of the recv_all function returns the length of the messages body while the second call reads the body
        on each stage of the function the state of the returned object is checked to see if the connection is still active
        if not the returned object will be none
        """
        len_str = self.recv_all(10)
        if len_str is None:
            return None
        msg_len = int(len_str)

        msg = self.recv_all(msg_len)
        return msg

    def recv_all(self, n):
        """
        The `recv_all` function reads a specified number of bytes from a socket and returns the data as a
        UTF-8 decoded string.
        
        """
        data = b''
        while len(data) < n:
            packet = self.sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data.decode('utf-8')
    def close(self):
        """
        The `close` function closes the socket connection.
        """
        self.sock.close()