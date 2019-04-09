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



def sendToAllOthers(string, origin):
    print(string)
    for i in hubClients:
        if(i != origin):
            i.send(string.encode())
    for i in channels:
        for j in i:
            if(j != origin):
                j.send(string.encode())


def send(string, dest):
    dest.send(string.encode())





#starting server
#-----------------------------------------------------
serverSoc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0) #socket d'écoute
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
                send(("CONNECT " + name), soc)
                nicks.append(name)
            else:
                send("ERR 7\n", soc)


        else: #client send command
            line = i.recv(1500)
            if(len(line) == 0): #if a clients leave the server
                sendToAllOthers("LEAVE " + hubClients[i][1], i)
                i.close()
                sockets.remove(i)
                nicks.remove(hubClients[i][1])
                hubClients.pop(i)
            

