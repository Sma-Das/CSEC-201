__VERSION__ = "1.0"
BUFFER = 8192
DELIM = ";"
bDELIM = DELIM.encode()


class PacketException(Exception):
    """
    Raised when a packet is an exception
    """


class Service:
    def __init__(self, address, port):
        self.address = address
        self.port = port


class Handler:
    def __init__(self, connection, secure):
        self.connection = connection
        self.secure = secure

    def send_packet(self, packet):
        self.connection.send(packet)

    def get_packet(self):
        return self.connection.recv(BUFFER)

    @staticmethod
    def make_packet(packet_args):
        packet = ""
        for arg in packet_args:
            packet += arg + DELIM
        # Strip off any trailing delimiters
        return packet.rstrip(DELIM).encode()

    @staticmethod
    def break_packet(packet):
        return packet.rstrip().decode().split(DELIM)
