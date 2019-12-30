import socket
import sys
import os
from cmd import Cmd
from getpass import getpass
import signal

ClientFolder = os.getcwd() + '/' + 'ClientFolder'

os.chdir(ClientFolder)


class Client(Cmd):
    def __init__(self, hostname, port):
        Cmd.__init__(self)
        Cmd.intro = "Starting FTP Client. For help type 'help' or '?'.\n"
        Cmd.prompt = "ftp> "
        self.client_socket = None
        self.server_addr = (socket.gethostbyname(hostname), port)
        self.connected = False
        self.prom = True
        self.Hash = True

    # To handle ctrl + c interrupt. exits without errors
    def sigint_handler(self, signum, frame):
        print('^C')
        sys.exit()

    def authClient(self):
        try:
            self.client_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(self.server_addr)
            try:
                username = input("Username: ")
                # print(username)
                password = getpass()
            except KeyboardInterrupt:
                self.client_socket.close()
                sys.exit()

            packet = "{}:{}".format(username, password)
            self.client_socket.sendall(packet.encode())

            response = self.client_socket.recv(1024).decode()

            if response == "SUCCESS":
                signal.signal(signal.SIGINT, self.sigint_handler)
                self.connected = True
                print("Connected to server {}:{}".format(*self.server_addr))
                return True
            else:
                self.connected = False
                print("Username or Password wrong.")
                return False
        except socket.error:
            print("Check that server is running or mentioned address is right")
            sys.exit()

    def do_hash(self, args):
        """hash      	toggle printing `#' for each buffer transferred"""
        if len(args.split()) != 0:
            if self.Hash == True:
                print("Hash mark printing on(1024 bytes/hash mark).")
            else:
                print("Hash mark printing off.")
        else:
            if self.Hash == True:
                self.Hash = False
                print("Hash mark printing off.")
            else:
                self.Hash = True
                print("Hash mark printing on(1024 bytes/hash mark).")

    def do_prom(self, args):
        """prompt    	force interactive prompting on multiple commands"""
        if self.prom == True:
            self.prom = False
            print("Interactive mode off.")
        else:
            self.prom = True
            print("Interactive mode on.")

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

    def do_lcd(self, args):
        """lcd       	change local working directory"""
        dir_name = args.split()
        # print(dir_name)
        if len(dir_name) == 1:
            try:
                if (dir_name[0] == '..' and os.getcwd() == ClientFolder):
                    return
                os.chdir(dir_name[0])
                print('Local directory now ' + os.getcwd())
            except FileNotFoundError:
                print(f"directory '{dir_name}' not found")
        else:
            print("CD requires exactly one argument.")

    def do_ls(self, args):
        """ls        	list contents of remote directory"""
        if not self.connected:
            print('Not connected.')
            return
        if len(args) != 0:
            print("No arguments required.")
            return
        self.client_socket.sendall("LS".encode())
        response = self.client_socket.recv(1024).decode()
        if response == "EMPTY":
            return
        else:
            print(response)

    def do_pwd(self, args):
        """pwd       	print working directory on remote machine"""

        if not self.connected:
            print('Not connected.')
            return
        if len(args) != 0:
            print("pwd requires no argument.")
            return
        self.client_socket.sendall("PWD".encode())
        response = self.client_socket.recv(1024).decode()
        if response == "EMPTY":
            return
        else:
            print(response)

    def do_cd(self, args):
        """cd        	change remote working directory"""

        if not self.connected:
            print('Not connected.')
            return
        if len(args) == 0:
            print("cd requires one argument as directory name")
        else:
            dir = args.split(" ")
            if len(dir) != 1:
                print("Only one argument required")
                return
            packet = "CD,{}".format(dir[0])
            self.client_socket.sendall(packet.encode())
            response = self.client_socket.recv(1024).decode()
            print(response)

    def do_mkdir(self, args):
        """mkdir     	make directory on the remote machine"""
        if not self.connected:
            print('Not connected.')
            return
        if len(args) == 0:
            print("mkdir requires one or more arguments as directory name")
        else:
            dirs = args.split(" ")
            for dir in dirs:
                packet = "MKDIR,{}".format(dir)
                self.client_socket.sendall(packet.encode())
                response = self.client_socket.recv(1024).decode()
                print(response)

    def do_rmdir(self, args):
        """rmdir     	remove directory on the remote machine"""
        if not self.connected:
            print('Not connected.')
            return
        if len(args) == 0:
            print("rmdir requires one argument as directory name")
        else:
            dir = args.split(" ")
            # for dir in dirs:
            packet = "RMDIR,{}".format(dir[0])
            self.client_socket.sendall(packet.encode())
            response = self.client_socket.recv(1024).decode()
            print(response)

    def do_delete(self, args):
        """delete    	delete remote file"""
        if not self.connected:
            print('Not connected.')
            return
        if len(args) == 0:
            print("delete requires one argument as directory name")
        else:
            file = args.split(" ")
            # for file in files:
            packet = "RM,{}".format(file[0])
            self.client_socket.sendall(packet.encode())
            response = self.client_socket.recv(1024).decode()
            print(response)

    def do_mdelete(self, args):
        """mdelete   	delete multiple files"""

        if not self.connected:
            print('Not connected.')
            return
        if len(args) == 0:
            print("mdelete requires one or more arguments as filename")
        else:
            files = args.split(" ")
            for file in files:
                if self.prom == True:
                    confirmation = input('mdelete ' + file + '?')
                    if confirmation == 'n' or confirmation == 'no' or confirmation == 'N' or confirmation == 'NO':
                        continue
                    else:
                        self.do_delete(file)
                else:
                    self.do_delete(file)

    def do_get(self, args):
        """get       	receive file"""

        if not self.connected:
            print('Not connected.')
            return

        file = args.split()

        if len(file) == 1:
            file_name = file[0]

            try:
                packet = "rget,{}".format(file_name)
                self.client_socket.sendall(packet.encode())

                # Initilize data connection
                dataConnection = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                dataConnection.bind(('', 0))
                dataConnection.listen(1)
                dataPort = dataConnection.getsockname()[1]

                # Send data connection port to server over control connection
                # so server can connect.
                self.client_socket.send(str(dataPort).encode())

                # Wait for server to connect.
                dataConnection, maddr = dataConnection.accept()
                print('[Control] Got connection from', maddr)

                print('200 PORT command successful')

                while True:
                    recv_data = self.client_socket.recv(1024)

                    packet_info = recv_data.decode(
                        'utf-8').strip().split(",")

                    if packet_info[0] == "Exists":
                        self.client_socket.sendall("Ready".encode('utf-8'))
                        # print(
                        #     "{} exits on the server, ready to download.".format(file_name))

                        save_file = open(file_name, "wb")

                        amount_recieved_data = 0
                        while amount_recieved_data < int(packet_info[1]):
                            recv_data = dataConnection.recv(1024)
                            amount_recieved_data += len(recv_data)
                            save_file.write(recv_data)

                            # printing hashes for each 1024 bytes of data transfered
                            if self.Hash == True:
                                print('#', end="")

                        # printing new line after printing hashes
                        if self.Hash == True:
                            print()

                        save_file.close()

                        self.client_socket.sendall("Received,{}".format(
                            amount_recieved_data).encode('utf-8'))
                    elif packet_info[0] == "Success":
                        print('226 Transfer complete')
                        break
                    elif packet_info[0] == "Failed":
                        print(
                            "File {} does not exist on server.".format(file_name))
                        break
                    else:
                        print("Something went wrong when downloading '{}' from server. Try again.".format(
                            file_name))
                        break
            except socket.error:
                print("SOCKET_ERROR: Check and ensure that server is running.")
        else:
            print("rget requires exactly 1 argument.")

    def do_put(self, args):
        """put       	send one file"""

        if not self.connected:
            print('Not connected.')
            return

        files = args.split()
        if len(files) == 1:
            file_name = files[0]

            try:
                packet = "rput,{},{}".format(
                    file_name, os.path.getsize(file_name))
                self.client_socket.sendall(packet.encode('utf-8'))
                print('200 PORT command successful')
                while True:
                    recv_data = self.client_socket.recv(1024)
                    packet_info = recv_data.decode(
                        'utf-8').strip().split(",")

                    if packet_info[0] == "Ready":
                        # print("Sending file {} to server {}".format(
                        #     file_name, self.client_socket.getpeername()))

                        with open(file_name, mode="rb") as file:
                            self.client_socket.sendfile(file)

                        if self.Hash == True:
                            # printing hash for each 1024 bytes of data transferred
                            for _ in range(os.path.getsize(file_name)//1024):
                                print('#', end="")

                    elif packet_info[0] == "Received":
                        if self.Hash == True:
                            print()
                        if int(packet_info[1]) == os.path.getsize(file_name):
                            print('226 Transfer complete')
                            break
                        else:
                            print("Something went wrong trying to upload to server {}. Try again".format(
                                self.client_socket.getpeername()))
                            break
                    else:
                        print("Something went wrong trying to upload to server {}. Try again.".format(
                            self.client_socket.getpeername()))
                        break
            except IOError:
                print("File doesn't exist on the system!")
        else:
            print("put requires exactly 1 argument.")
            print()

    def do_mget(self, args):
        """mget      	get multiple files"""

        if not self.connected:
            print('Not connected.')
            return
        if len(args) == 0:
            print("atleast one argument required.")
            return
        else:
            filelist = args.split()
            for file in filelist:
                if self.prom == True:
                    confirmation = input('mget ' + file + '?')
                    if confirmation == 'n' or confirmation == 'no' or confirmation == 'N' or confirmation == 'NO':
                        continue
                    else:
                        self.do_get(file)
                else:
                    self.do_get(file)

    def do_mput(self, args):
        """mput      	send multiple files"""

        if not self.connected:
            print('Not connected.')
            return
        if len(args) == 0:
            print("atleast one argument required.")
            return
        else:
            filelist = args.split()
            for file in filelist:
                if self.prom == True:
                    confirmation = input('mput ' + file + '?')
                    if confirmation == 'n' or confirmation == 'no' or confirmation == 'N' or confirmation == 'NO':
                        continue
                    else:
                        self.do_put(file)
                else:
                    self.do_put(file)

    def do_exit(self, args):
        """exit      	terminate ftp session and exit"""
        self.client_socket.send("EXIT".encode())
        self.client_socket.close()
        sys.exit()

    def do_bye(self, args):
        """bye      	terminate ftp session and exit"""
        self.client_socket.send("EXIT".encode())
        self.client_socket.close()
        sys.exit()

    def do_quit(self, args):
        """quit      	terminate ftp session and exit"""
        self.client_socket.send("EXIT".encode())
        self.client_socket.close()
        sys.exit()

    # using '!' before commands, escaping to local command execution
    def do_shell(self, args):
        """Pass command to a system shell when line begins with '!'"""
        os.system(args)

    do_EOF = do_exit        # exiting by ctrl+d

    def do_close(self, args):
        """close     	terminate ftp session"""
        if not self.connected:
            print('Not connected.')
        self.connected = False
        self.client_socket.close()

    def do_open(self, args):
        if not self.connected:
            self.authClient()
        else:
            print('Already connected.')


if __name__ == "__main__":
    if len(sys.argv) == 3:
        hostname = sys.argv[1]
        port = int(sys.argv[2])
    else:
        print("Server IP and PORT NO. required as arguments")
        sys.exit(2)

    client = Client(hostname, port)
    if client.authClient():
        client.cmdloop()
