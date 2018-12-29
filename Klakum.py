import RPi.GPIO as GPIO
import threading
import socket
import datetime
import simplecrypt

from KlakumLib import *


class Server(threading.Thread):
    def __init__(self, port: int, react, ip=socket.gethostbyname(socket.gethostname()), buffersize=1024, loginName=None, loginPW=None, maxConnections=1, Seculevel=0, BigServerBuffersize=536870912, BigServerPort=0, welcomeMessage="", thisBig=False):
        """
        ip
        ip of the server

        port
        the port where the server listen on

        reac
        the function with will be executed when the server sent data

        buffersize
        normaly 1024
        byte limit of your get data

        loginName
        if enabled in the server the loginName is defined here

        loginPW
        if enabled in the server the loginPW is defined here

        Seculevel
        normaly 0 if both uses 0 no secu will be used
        -2: the encryption will be deactivated so you can not connect with server with seculevel 2
        -1: the encryption will be deactivated, but if the client has enabled Secu, Secu will be used
        0:  the client decide if the encryption is enabled
        1:  you force the client to generate a encryption code, but if the client has deactivated Secu, no Secu will be used
        2:  the encryption will be deactivated so you can not connect with server with seculevel -2

        S   C   Y=Encryption N=No Encryption E=No Connection
        -2  -2  N
        -2  -1  N
        -2  0   N
        -2  1   N
        -2  2   E

        -1  -2  N
        -1  -1  N
        -1  0   N
        -1  1   N
        -1  2   Y

        0  -2   N
        0  -1   N
        0  0    N
        0  1    Y
        0  2    Y

        1  -2   N
        1  -1   Y
        1  0    Y
        1  1    Y
        1  2    Y

        2  -2   E
        2  -1   Y
        2  0    Y
        2  1    Y
        2  2    Y

        BigServerBuffersize
        normaly 536870912 (maybe 512MB)
        if this Buffersize is less then the normal buffersize the BigServer will be deactivated
        you can set the Buffersize of the Bigserver

        BigServerPort
        set the Port of the BigServer if it is 0 the port is the normal port+1

        Keywords:
        #C! for a command
        #T! do not use, this will be used to talk to the client directly, like login in
        #R! for receiving some return infomation
        #B! for travel through bigserver

        """
        super().__init__()

        self.version = "1.0.0"

        self.thisBigServer = thisBig
        self.port = port
        self.react = react
        self.ip = ip
        self.buffersize = buffersize
        self.maxConnections = maxConnections
        self.welcomeMessage = welcomeMessage

        if loginName and loginPW:
            self.login = True
        else:
            self.login = False
        self.loginName = loginName
        self.loginPW = loginPW

        self.Seculevel = Seculevel

        self.Timer = TimerC()

        self.BigServerBuffersize = BigServerBuffersize
        if not BigServerPort:
            self.BigServerPort = port + 1

        if BigServerBuffersize > self.buffersize:
            self.BigServerEnabled = True
            self.BigServer = Server(port=BigServerPort, react=self.receive, buffersize=self.BigServerBuffersize,
                                    loginName=self.loginName, loginPW=self.loginPW, Seculevel=self.Seculevel,
                                    BigServerBuffersize=0, thisBig=True)
        else:
            self.BigServerEnabled = False
            self.BigServer = None

        self.Logsend = []
        self.Logrece = []

        self.s = socket.socket()
        try:
            self.s.bind((self.ip, self.port))
        except OSError:
            raise ServerPortUsed(self.port)

        self.Running = False  # between start and end
        self.Connected = False  # while connected

        self.connects = []

        self.conAddress = None
        self.con = None
        self.conInfo = None

        self.Info = {"ip": self.ip, "port": self.port, "buffersize": self.buffersize,
                     "maxconnections": self.maxConnections, "welcomeMessage": self.welcomeMessage,
                     "login": {"status": self.login, "name": self.loginName, "password": self.loginPW},
                     "bigserver": {"status": self.BigServerEnabled, "ip": self.ip, "port": self.BigServerPort},
                     "secu": {"level": self.Seculevel}}

        self.Log = []
        self.Status = "Starting"

    def run(self):
        self.Running = True
        self.Timer.start()

        self.Status = "Setup"
        self.writeLog("Status:")
        self.writeLog("Ip: " + str(self.ip))
        self.writeLog("Port: " + str(self.port))
        self.writeLog("Login: " + str(self.login))
        self.writeLog("LoginName: " + str(self.loginName))
        self.writeLog("LoginPW: " + str(self.loginPW))
        self.writeLog("BigServer: " + str(self.BigServerEnabled))
        self.writeLog("BigServerPort: " + str(self.BigServerPort))
        self.writeLog("Seculevel: " + str(self.Seculevel))

        while self.Running:

            self.Status = "Listening..."
            self.writeLog("Listening...")

            self.s.listen(self.maxConnections)

            self.con, self.conAddress = self.s.accept()

            self.writeLog("Found Client with IP: %s, Port: %s" % (self.conAddress[0], self.conAddress[1]))

            self.Connected = True
            self.Status = "Connected"
            self.connects.append(self.conAddress)

            InfoSend = b'#T!' + str(self.Info["login"]["status"]).encode() + b'!' + \
                       str(self.Info["bigserver"]["status"]).encode() + b'!' + \
                       str(self.Info["bigserver"]["port"]).encode() + b'!' + \
                       str(self.Info["secu"]["level"]).encode()

            # self.Log.append(InfoSend)
            self.send(InfoSend, encrypt=False)

            try:
                InfoClient_raw = self.con.recv(1024)
            except ConnectionResetError:
                self.writeLog("Client disconnected while logging in")
                continue

            InfoClient = InfoClient_raw.decode("UTF-8").split("!")

            if not InfoClient[0] == "#T":
                self.writeLog("Client send wrong Infoconnection")
                continue

            elif InfoClient[0] == "#T" and InfoClient[1] == "Test":
                self.conInfo = {"secu": {"status": -1}, "key": "None"}
                self.writeLog("Client uses the 'Test'-Version")

            else:
                if InfoClient[1] == "True":
                    # noinspection PyTypeChecker
                    InfoClient[1] = True
                else:
                    # noinspection PyTypeChecker
                    InfoClient[1] = False

                self.conInfo = {"login": {"status": InfoClient[1], "name": InfoClient[2], "password": InfoClient[3]},
                                "secu": {"status": int(InfoClient[4]), "level": int(InfoClient[5]),
                                         "key": InfoClient[6]}}

            self.writeLog("Client:")
            self.writeLog("Login: " + str(InfoClient[1]))
            self.writeLog("LoginName: " + InfoClient[2])
            self.writeLog("LoginPW: " + InfoClient[3])
            self.writeLog("Secu: " + str(InfoClient[4]))
            self.writeLog("Seculevel: " + str(InfoClient[5]))
            self.writeLog("Secukey: " + self.conInfo["secu"]["key"])

            # print(self.Info, self.conInfo)

            if self.login:
                if self.conInfo["login"]["status"]:
                    if self.loginName == self.conInfo["login"]["name"] and self.loginPW == self.conInfo["login"][
                        "password"]:
                        conAccept = True
                    else:
                        conAccept = False
                else:
                    conAccept = False
            elif self.conInfo["login"]["status"]:
                conAccept = False
            else:
                conAccept = True

            self.send(conAccept, encrypt=False)
            if not conAccept:
                self.writeLog("Client sent wrong logindata")
                continue

            if self.welcomeMessage:
                self.send(self.welcomeMessage)

            if self.conInfo["secu"]["status"] == 1:  # yes
                self.writeLog("Started Connection with Client. Decryption")

                while self.Running and self.Connected and self.Status != "Ended" and self.Status == "Connected":
                    try:
                        data_en = self.con.recv(1024)
                    except ConnectionResetError:
                        self.writeLog("Client disconnected without warning")
                        break
                    except ConnectionAbortedError:
                        self.writeLog("Connection aborted")
                        break
                    except OSError:
                        break

                    data = simplecrypt.decrypt(self.conInfo["secu"]["key"], data_en)

                    if not data:
                        self.writeLog("Client disconnected. If this happens the Client send something courious")
                        break

                    self.receive(data)

            elif self.conInfo["secu"]["status"] == -1:  # no
                self.writeLog("Started Connection with Client. No Decryption")

                while self.Running and self.Connected and self.Status != "Ended" and self.Status == "Connected":
                    try:
                        data = self.con.recv(1024)
                    except ConnectionResetError:
                        self.writeLog("Client disconnected without warning")
                        break
                    except ConnectionAbortedError:
                        self.writeLog("Connection aborted")
                        break
                    except OSError:
                        break

                    if not data:
                        self.writeLog("Client disconnected. If this happens the Client send something courious")
                        break

                    self.receive(data)

            elif self.conInfo["secu"]["status"] == 0:  # no connection
                self.writeLog("Can not establish a connection. Seclevels: Server: %s, Client: %s" % (
                    self.Seculevel, self.conInfo["secu"]["level"]))

            else:
                self.writeLog("The Client sent: " + str(self.conInfo["secu"]["status"]) + ". Error")

            self.Connected = False
            self.con.close()
            # reset
            self.conAddress = None
            self.con = None
            self.conInfo = None

        self.Running = False
        self.Status = "Ended"

    def send(self, data, encrypt=None):
        if self.Running and self.Connected and self.Status != "Ended" and self.Status == "Connected" or not encrypt:

            if type(data) == str:
                data_send = data.encode()
            elif type(data) == int:
                data_send = str(data).encode()
            elif type(data) == bool:
                data_send = str(data).encode()
            else:
                data_send = data

            if encrypt is None:
                if self.conInfo["secu"]["status"] == 1:
                    data_send_de = simplecrypt.encrypt(self.conInfo["secu"]["key"], data_send)
                else:
                    data_send_de = data_send
            elif encrypt:
                data_send_de = simplecrypt.encrypt(self.conInfo["secu"]["key"], data_send)
            else:
                data_send_de = data_send

            # print(encrypt, self.conInfo["secu"]["status"])
            # print(data, data_send, data_send_de)
            self.Logsend.append(data)
            self.writeLog("Sended: " + data_send.decode("UTF-8"))
            self.con.send(data_send_de)

    def receive(self, data):
        if self.Running and self.Connected and self.Status != "Ended" and self.Status == "Connected":
            data_form = data.decode("UTF-8")
            data_form_split = data_form.split("!")

            self.Logrece.append(data)
            self.writeLog("Receive: " + data_form)

            if data_form_split[0] == "#C" and len(data_form_split) > 1:
                if data_form_split[1] == "getTimeRaw":
                    self.send("#R!" + str(self.getRunTime()))
                elif data_form_split[1] == "getTime":
                    self.send("#R!" + str(self.getRunTime(False)))
                elif data_form_split[1] == "exit":
                    self.exit()
            elif data_form_split[0] == "#T" and len(data_form_split) > 1:
                if data_form_split[1] == "exit":
                    self.exit(sendM=False)
                    self.writeLog("Client disconnected")
            elif data_form_split[0] == "#B" and len(data_form_split) > 1:
                pass
            else:
                self.react(data_form)

    def writeLog(self, data):
        write = "(" + datetime.datetime.now().strftime("%H:%M:%S:%f") + ") " + "(" + self.Status + ") " + data
        self.Log.append(write)
        print("[Log] " + write)
        self.save()

    def save(self):
        file_log_raw = open("Log.txt", "w")
        for x in self.Log:
            file_log_raw.write(x)
        file_log_raw.close()

        file_logsend_raw = open("LogSend.txt", "w")
        for x in self.Logsend:
            if type(x) == str:
                file_logsend_raw.write(x)
            elif type(x) == bytes:
                file_logsend_raw.write(x.decode("UTF-8"))
            elif type(x) == bool:
                file_logsend_raw.write(str(x))
        file_logsend_raw.close()

        file_logrece_raw = open("LogReceive.txt", "w")
        for x in self.Logrece:
            if type(x) == str:
                file_logrece_raw.write(x)
            elif type(x) == bytes:
                file_logrece_raw.write(x.decode("UTF-8"))
            elif type(x) == bool:
                file_logrece_raw.write(str(x))
        file_logrece_raw.close()

    def exit(self, sendM=True):
        if sendM:
            self.send("#T!exit")
        self.con.close()

    def getStatus(self):
        curStatus = {"status": {"status": self.Status, "running": self.Running, "connected": self.Connected},
                     "log": self.Log, "info": self.Info, "connects": self.connects}
        return curStatus

    def getRunTime(self, raw=True):
        if raw:
            return self.Timer.getTime()
        else:
            return self.Timer.getTimeFor()


class Relay:
    def __init__(self, pin):
        self.pin = pin
        self.value = 0
        GPIO.setup(pin, GPIO.OUT, initial=1)

    def set(self, value):
        if type(value) == str:
            try:
                value = int(value)
            except ValueError:
                if value == "True":
                    value = 1
                elif value == "False":
                    value = 0
                else:
                    if value:
                        value = 1
                    else:
                        value = 0
        elif value:
            value = 1
        else:
            value = 0

        self.value = value
        if self.value:
            GPIO.output(self.pin, 0) #an
        else:
            GPIO.output(self.pin, 1) #aus

    def get(self):
        return self.value

    def switch(self):
        if self.value:
            self.set(0)
        else:
            self.set(1)


class RelaySurge:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT, initial=1)

    def switch(self):
        GPIO.output(self.pin, 0)
        time.sleep(0.1)
        GPIO.output(self.pin, 1)


GPIO.setmode(GPIO.BCM)

relay_list = [Relay(5), Relay(25), Relay(24), Relay(23), Relay(22), Relay(27), Relay(18)]
relay_surge_list = [RelaySurge(17)]


def reacter(mess):

    mess_split = mess.split("_")

    if mess_split[0] == "relay":

        relay_id = int(mess_split[1])

        if mess_split[2] == "set":
            relay_list[relay_id].set(mess_split[3])

        elif mess_split[2] == "get":
            Klakum_Server.send("relay_" + str(relay_id) + "_return_" + str(relay_list[relay_id].get()))

        elif mess_split[2] == "switch":
            relay_list[relay_id].switch()

    elif mess_split[0] == "srelay":

        relay_id = int(mess_split[1])

        if mess_split[2] == "switch":
            relay_surge_list[relay_id].switch()


Klakum_Server = Server(1007, reacter, ip="192.168.2.107", BigServerBuffersize=0)
Klakum_Server.start()
Klakum_Server.join()

GPIO.cleanup()
