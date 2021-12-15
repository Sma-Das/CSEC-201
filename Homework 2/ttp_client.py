import socket
from getpass import getpass

from ttp_service import Handler, Service
from ttp_service import PacketException
from ttp_service import __VERSION__

from cryptography.hazmat.backends import default


class ServerHandler(Handler):
    def __init__(self, connection, secure):
        super().__init__(connection, secure)
        if secure:
            self.session_key = None
            self.algorithm = None
            self.key = None

    def connect(self):
        start_packet = self.make_packet(["SS", "TTP", __VERSION__, str(int(self.secure))])
        self.send_packet(start_packet)

        if self.secure:
            self.algorithm = self.get_algorithm()
            if self.algorithm == "DES":
                private_key = self.make_private_key()
                public_key = private_key.public_key()

        response = self.get_packet()
        print(response)
        response_packet = self.break_packet(response)
        if not response_packet[0] == "CC":
            raise PacketException("Server did not send a confirm request")

        if self.secure and self.algorithm == "DES":
            session_key_packet = self.get_packet()
            session_key_packet = self.break_packet(session_key_packet)
            if not session_key_packet[0] == "SK":
                raise PacketException("Server did not send session key")
            self.session_key = session_key_packet[1]

        print("Connected to the server!")

    @staticmethod
    def get_algorithm():
        return input("Enter algorithm: ")

    @staticmethod
    def make_private_key():
        return


class Client(Service):
    def start(self, secure):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.address, self.port))
            try:
                handler = ServerHandler(client_socket, secure)
                handler.connect()
            except PacketException as PKE:
                print(f"Could not connect to the server {PKE}")
                return

            while True:
                query = input("> ")
                query_packet = handler.make_packet(["IN", query])
                handler.send_packet(query_packet)


if __name__ == '__main__':
    Client("localhost", 10000).start(secure=False)