import socket
import struct

class ProtocolSocketWrapper:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def send(self, msg):
        # Prepend the length of the message to the message itself
        msg = f'{len(msg):<{10}}' + msg
        self.sock.sendall(msg.encode('utf-8'))

    def recv(self):
        # Read the length of the message
        len_str = self.recv_all(10)
        if len_str is None:
            return None
        msg_len = int(len_str)

        # Read the message
        msg = self.recv_all(msg_len)
        return msg

    def recv_all(self, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = b''
        while len(data) < n:
            packet = self.sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data.decode('utf-8')
    def close(self):
        self.sock.close()