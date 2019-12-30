import socket
import sys
import csv
from thread_functions import ThreadFunctions

created_threads = []


class Server():
    def __init__(self, server_port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_port = server_port
        self.max_queued = 10
        self.allowed_users = self.load_users()

    def runserver(self):
        self.server_socket.bind(('', self.server_port))
        self.server_socket.listen(self.max_queued)
        # created_threads = []
        print("Server started listening at {}:{}".format(
            *self.server_socket.getsockname()))

        while True:
            # waiting for connection and accepting
            client_socket, client_addr = self.server_socket.accept()

            # another inside while loop to authorize username and password
            while True:
                response = client_socket.recv(1024).decode().strip().split(":")
                try:
                    if self.auth_user(response[0], response[1]):
                        client_socket.sendall("SUCCESS".encode())
                        # print("Connected with {}:{}".format(client_addr[0], client_addr[1]))

                        # now spawn new client thread
                        new_client_thread = ThreadFunctions(
                            client_socket, *client_addr)
                        new_client_thread.start()
                        created_threads.append(new_client_thread)
                        break
                    else:
                        client_socket.sendall("FAILURE".encode())
                        # client_socket.shutdown(socket.SHUT_RDWR)
                        client_socket.close()
                        break
                except IndexError:
                    client_socket.sendall("FAILURE".encode())
                    # client_socket.shutdown(socket.SHUT_RDWR)
                    client_socket.close()
                    break

            # response = client_socket.recv(1024).decode()
            # if response == "EXIT":
            #     print("Disconnected from {}:{}".format(
            #         client_addr[0], client_addr[1]))

        for thread in created_threads:
            thread.join()

    def auth_user(self, name=None, password=None):
        if name == None or password == None:
            return False
        for user in self.allowed_users:
            if name == user["name"] and user["passwd"] == password:
                return True
        return False

    def load_users(self):
        try:
            register_file = open("users.txt", "r")
        except FileNotFoundError:
            print(
                "Server is not able to authenticate user due to some issues with server")
            sys.exit()

        users = []
        csv_file = csv.DictReader(register_file, delimiter=",")
        for user in csv_file:
            users.append(user)

        return users


if __name__ == "__main__":
    if len(sys.argv) == 2:
        server_port = int(sys.argv[1])
    else:
        print("Must have PORT No. as the first and only argument")
        sys.exit(2)

    server = Server(server_port)
    server.runserver()
