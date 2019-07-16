import RPi.GPIO as GPIO
import socket
import datetime
import simplecrypt
import shutil
import json

from EveconTools import *

path_seg = "/"


class ServerPortUsed(Exception):
    def __init__(self, port):
        print("The port: %s is already used, please use another one!" % port)

class Server(threading.Thread):
    def __init__(self, port: int, react, ip=socket.gethostbyname(socket.gethostname()), buffersize=1024, loginName=None,
                 loginPW=None, maxConnections=1, Seculevel=0, BigServerBuffersize=536870912, BigServerPort=0,
                 welcomeMessage="", thisBig=False):
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
        self.Connected = False


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
            GPIO.output(self.pin, 0)  # an
        else:
            GPIO.output(self.pin, 1)  # aus

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



class Notie:
    def __init__(self, keyname: str):
        """
        starts the object, search if it exists

        :param keyname: the KEYname of the note. It is ONLY for the programme
        """

        self.keyname = keyname

        allNoties = os.listdir("data"+path_seg+"Noties")
        self.allNoties = []
        for note in allNoties:
            if rsame(note, ".json"):
                self.allNoties.append(note.rstrip(".json"))
        self.existing = bool(Search(self.keyname, self.allNoties))

        self.file = "Noties" + path_seg + self.keyname + ".json"
        self.dir = "Noties" + path_seg + self.keyname + path_seg

        self.name = ""
        self.lines = []
        self.lines_en = []
        self.encryption = False
        self.encryptionKey = ""

        self.saveEnKey = None
        self.autosave = None

        self.started = False

    def __del__(self):
        """
        if autosave the file will be saved
        """
        if self.started and self.autosave:
            self.save()

    def len(self):
        return len(self.getLines())
    len = property(len)

    def _read(self):
        """
        reads the file

        :return: success
        """
        with open(self.file) as jsonfile:
            data = json.load(jsonfile)

        self.name = data["name"]
        self.encryption = data["config"]["encryption"]
        self.saveEnKey = data["config"]["saveEnKey"]
        self.autosave = data["config"]["autosave"]
        lineLen = data["len"]

        if self.encryption:
            self.lines_en = []
            # noinspection PyArgumentList
            for num in range(lineLen):
                with open(self.dir+str(num)+".byte", "rb") as bytefile:
                    self.lines_en.append(bytefile.read())



        else:
            self.lines_en = data["lines"]

        if self.encryption and self.saveEnKey:
            self.encryptionKey = data["encryptionKey"]
        elif self.encryption and not self.saveEnKey:
            pass
        else:
            self.encryptionKey = ""
        self._decrypt()

        return bool(data)

    def _write(self):
        """
        reads the file

        :return: success
        """
        self._encrypt()

        if self.saveEnKey:
            enKey = self.encryptionKey
        else:
            enKey = ""

        if self.encryption:
            if not os.path.exists(self.dir.rstrip(path_seg)):
                os.mkdir(self.dir.rstrip(path_seg))

            for x in range(len(self.lines_en)):
                with open(self.dir+str(x)+".byte", "wb") as bytefile:
                    bytefile.write(self.lines_en[x])


            output = {"config": {"encryption": self.encryption, "saveEnKey": self.saveEnKey, "autosave": self.autosave},
                      "lines": [],
                      "encryptionKey": enKey, "len": self.len, "name": self.name}

        else:
            output = {"config": {"encryption": self.encryption, "saveEnKey": self.saveEnKey, "autosave": self.autosave},
                      "lines": self.lines,
                      "encryptionKey": enKey, "len": self.len, "name": self.name}



        with open(self.file, "w") as jsonfile:
            json.dump(output, jsonfile, indent=4, sort_keys=True)

        return os.path.exists(self.file)

    def _encrypt(self):
        """
        encrypt the self.lines in self.lines_en
        """
        if self.encryption:
            self.lines_en = []
            for line in self.lines:
                self.lines_en.append(simplecrypt.encrypt(self.encryptionKey, line))
        else:
            self.lines_en = self.lines.copy()
    def _decrypt(self):
        """
        decrypt the self.lines_en in self.lines
        """
        if self.encryption:
            self.lines = []
            for line in self.lines_en:
                self.lines.append(simplecrypt.decrypt(self.encryptionKey, line).decode())
        else:
            self.lines = self.lines_en.copy()

    def enableEncryption(self, encryptionKey=randompw(returnpw=True, printpw=False, length=10), saveEnKey=True):
        """
        enables the encryption

        :param encryptionKey: the key for the encryption
        :param saveEnKey: if True it saves the encrpytion key in the SAME file with the content
        :rtype: bool
        :return: success
        """
        if self.started and not self.encryption:
            self.encryptionKey = encryptionKey
            self.saveEnKey = saveEnKey

            return  self._write()
        else:
            return False

    def setConfig(self, config: str, value):
        """
        resets the config

        :param config: the config name
        :param value: the value
        :return: succsess
        """

        if config == "autosave":
            self.autosave = value
        elif config == "saveEnKey":
            self.saveEnKey = value
        else:
            return False

        if self.autosave:
            return self._write()
        return True

    def open(self, encryptionKey=""):
        """
        Reads the file for the first time!
        :param encryptionKey: if needed the encryptkey for the file (DO not need if: 1. no encryption 2. saveEnKey

        :rtype: bool
        :return: success
        """

        if self.existing and not self.started:
            self.started = True


            if os.path.exists(self.dir+"0.byte"):

                with open(self.file) as jsonfile:
                    data = json.load(jsonfile)

                self.saveEnKey = data["config"]["saveEnKey"]
                if self.saveEnKey:
                    encryptionKey = data["encryptionKey"]

                with open(self.dir+"0.byte", "rb") as file:
                    b = file.read()
                try:
                    simplecrypt.decrypt(encryptionKey, b)
                except simplecrypt.DecryptionException or ValueError:
                    return False

            return self._read()
        else:
            return False

    def create(self, name: str, content="", encryption=False, encryptionKey=randompw(returnpw=True, printpw=False, length=10), saveEnKey=True, autosave=True):
        """
        Creates a note (if it already exists or opened it will be OVERRIDDEN)

        :param name: the name of the file (title)
        :param content: the predefined first line of the file
        :param encryption: enables the encryption
        :param encryptionKey: the key for the encryption
        :param saveEnKey: if True it saves the encrpytion key in the SAME file with the content
        :param autosave: saves the file after every change (slow with encryption)
        :return: success
        """

        if self.started or self.existing:
            self.remove()

        self.started = True

        self.name = name
        self.encryption = encryption
        if self.encryption:
            self.encryptionKey = encryptionKey
        else:
            self.encryptionKey = ""

        if content:
            self.lines = [content]
        else:
            self.lines = []

        self.lines_en = []

        self.saveEnKey = saveEnKey
        self.autosave = autosave

        return self._write()


    def export(self, filename="", path="data" + path_seg + "Output"+path_seg):
        """
        :param filename: the name of the export file (without .txt)
        :param path: the specified path of the export directory

        :rtype: bool
        :return: success
        """
        if self.started:
            if filename:
                filename += ".txt"
            else:
                filename = self.name + ".txt"

            content = self.name + ":\n\n"
            for con in range(len(self.lines)):
                if con == len(self.lines) - 1: # last line
                    content += self.lines[con]
                else:
                    content += self.lines[con] + "\n"

            with open(path + filename, "w") as file:
                file.write(content)

            return os.path.exists(path+filename)
        else:
            return False
    def save(self):
        """
        saves the file

        :rtype: bool
        :return: success
        """

        return self._write()
    def clear(self):
        """
        clears the content/lines

        :rtype: bool
        :return: success
        """

        self.lines = []
        if self.autosave:
            self._write()
    def remove(self):
        """
        removes the file

        :rtype: bool
        :return: success
        """

        if self.existing:
            self.name = ""
            self.lines = []
            self.lines_en = []
            self.encryption = False
            self.encryptionKey = ""

            self.saveEnKey = None
            self.autosave = None

            self.started = False

            os.remove(self.file)
            if self.encryption:
                shutil.rmtree(self.dir.rstrip(path_seg))

            return not os.path.exists(self.file) and not os.path.exists(self.dir)
        else:
            return False

    def add(self, text: str):
        """
        adds one line
        :param text: text
        """
        self.lines.append(text)
        if self.autosave:
            self._write()
    def set(self, lines: list):
        """
        sets all lines
        :param lines: lines in list
        :return:
        """
        self.lines = lines
        if self.autosave:
            self._write()
    def setLine(self, line: int, text: str):
        """
        sets one specific line

        :param line: the line number
        :param text: text
        """
        self.lines[line] = text
        if self.autosave:
            self._write()
    def setName(self, name: str):
        """
        sets the name new

        :param name: name
        :return:
        """
        self.name = name
        if self.autosave:
            self._write()

    def getLines(self, read=False):
        """
        gets all lines

        :param read: if true the file will be read again (slow with encryption)
        :rtype: list
        :return: all lines
        """
        if read:
            self._read()
        return self.lines

    def getLine(self, line: int, read=False):
        """
        gets one specific line

        :param line: the line
        :param read: if true the file will be read again (slow with encryption)
        :rtype: list
        :return: one line
        """
        if read:
            self._read()
        return self.lines[line]
    def getName(self, read=False):
        """
        gets the name

        :param read: if true the file will be read again (slow with encryption)
        :rtype: str
        :return: name
        """
        if read:
            self._read()
        return self.name


