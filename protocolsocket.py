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
        
        :param sock: The `sock` parameter in the `__init__` method of the class is used to either create a
        new socket or save an existing socket provided by the user. If `sock` is `None`, a new socket is
        created using `socket.socket(socket.AF_INET, socket.SOCK_STREAM)`
        """
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        """
        The `connect` function establishes a connection to a specified host and port.
        
        :param host: The `host` parameter in the `connect` method is typically a string representing the
        hostname or IP address of the server to which you want to establish a connection. It is the address
        of the remote machine you want to connect to
        :param port: The `port` parameter in the `connect` method is used to specify the port number to
        which the socket will connect on the remote host. Ports are communication endpoints that allow
        different services or processes to communicate over a network. Each service or process listens on a
        specific port for incoming connections
        """
        """"""
        self.sock.connect((host, port))

    def send(self, msg):
        """
        The `send` function takes a message, adds the length of the message to the beginning of the message formatted as {takes exactly 10 spaces},
        and then sends the encoded message over a socket.
        
        :param msg: The `send` method takes a message (`msg`) as input and sends it over a socket
        connection. The message is first formatted to include the length of the message followed by the
        message itself, and then it is sent over the socket connection after encoding it in UTF-8
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
        
        :param n: The parameter `n` in the `recv_all` method represents the total number of bytes that the
        method is expected to receive before returning the complete data. The method reads data from a
        socket (`self.sock`) in chunks until it has received `n` bytes in total
        :return: The `recv_all` method returns the received data as a UTF-8 decoded string if the data is
        successfully received within the specified length `n`. If no data is received or an error occurs
        during the reception, it returns `None`.
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