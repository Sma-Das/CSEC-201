import socket
import threading

from ttp_service import Handler, Service
from ttp_service import PacketException


class ClientHandler(Handler):
    def __init__(self, connection):
        super().__init__(connection, None)
        self.session_key = None
        self.secure = None

    def start_connection(self):
        request = self.get_packet()
        request_packet = self.break_packet(request)
        if not request_packet[0] == "SS":
            self.send_exception(1, "Invalid start packet")
            return
        else:
            self.send_packet(self.make_packet(["CC"]))

        if request_packet[3] == "1":  # Secure Connection
            self.secure = True
            encrypted_packet = self.get_packet()
            encrypted_packet = self.break_packet(encrypted_packet)
            if encrypted_packet[1] == "Authentication":
                self.check_credentials(encrypted_packet[2])
            elif encrypted_packet[1] == "DES":
                self.session_key = self.make_session_key(encrypted_packet[2])
                session_key_packet = self.make_packet(["SK", self.session_key])
                self.send_packet(session_key_packet)
            else:
                self.send_exception(2, "Invalid encryption packet")
        else:
            self.secure = False
        print("Client has connected to the server!")

    def send_exception(self, code, message):
        exception_packet = self.make_packet(["EE", str(code), message])
        self.send_packet(exception_packet)

    @staticmethod
    def check_credentials(credentials):
        """
        # TODO check credentials
        :param credentials:
        :return:
        """
        return False

    @staticmethod
    def make_session_key(public_key):
        """
        # TODO Make session key generator
        :param public_key:
        :return:
        """
        return ""


class Server(Service):
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.address, self.port))
            server_socket.listen()
            while True:
                connection, client_addr = server_socket.accept()
                threading.Thread(target=self.client_handler,
                                 args=(client_addr, ClientHandler(connection),)
                                 ).start()

    @staticmethod
    def client_handler(client_addr, handler):
        client_addr = ":".join(client_addr)
        try:
            handler.start_connection()
        except PacketException:
            print("Could not establish connection")
            return
        try:
            while True:
                query = handler.get_packet()
                if not query:
                    continue
                print(client_addr, query)
                # TODO Packet management
        except OSError as ERR:
            print(client_addr, ERR)


if __name__ == '__main__':
    Server("localhost", 10000).start()
