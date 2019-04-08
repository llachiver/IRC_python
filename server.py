import socket
import select
import sys


PORT = 1459
HOST = ''

#data structure: list of dictionnaries(channels)
#channels: channelName -> {clients queue}
#clients: socket -> (IP, nick, channel)

channels = []
hubClients = {}#channel: hub
nicks = [] #existing nicknames

sockets = []

guest = 1

#starting server
#-----------------------------------------------------
serverSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) #socket d'écoute
serverSoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #ferme la connection qd deconnexion
serverSoc.bind((HOST, PORT))
serverSoc.listen(1)
#-----------------------------------------------------


#LOOPBACK:
while(True):
    (connected, _, _) = select.select( sockets + [serverSoc], [], [])

    #browse all connected sockets
    for i in connected:
        if (i == serverSoc): #case of new connection
            
            (soc,addr) = serverSoc.accept()
            sockets.append(soc)
            if guest < sys.maxsize:#set default nick to new commers
                name = "Guest"+str(guest)
                guest += 1
                hubClients[soc]= (addr[0], name, "hub")
                soc.send(("CONNECT " + name).encode())
            else:
                soc.send(b"ERR 7\n")


        else: #client send command
            print("---------")
            for j in hubClients:
                print(hubClients[j][1])
