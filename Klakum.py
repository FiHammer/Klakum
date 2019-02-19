from KlakumLib import *



GPIO.setmode(GPIO.BCM)

relay_list = [Relay(5), Relay(25), Relay(24), Relay(23), Relay(22), Relay(27), Relay(18)]
relay_surge_list = [RelaySurge(17)]


def reacter(msg):
    msg_split = msg.split("_")

    if msg_split[0] == "relay":

        relay_id = int(msg_split[1])

        if msg_split[2] == "set":
            relay_list[relay_id].set(msg_split[3])

        elif msg_split[2] == "get":
            Klakum_Server.send("relay_" + str(relay_id) + "_return_" + str(relay_list[relay_id].get()))

        elif msg_split[2] == "switch":
            relay_list[relay_id].switch()

    elif msg_split[0] == "srelay":

        relay_id = int(msg_split[1])

        if msg_split[2] == "switch":
            relay_surge_list[relay_id].switch()


Klakum_Server = Server(1007, reacter, ip="192.168.2.107", BigServerBuffersize=0)
Klakum_Server.start()
Klakum_Server.join()

GPIO.cleanup()
