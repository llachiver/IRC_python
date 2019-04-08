import socket
import select

PORT = 1459

#data structure: list of dictionnaries(channels)
#channels: channelName -> (clients queue)
#clients: socket -> (IP, nick, channel)

channels = []
hubClients = []
nicks = [] #existing nicknames

sockets = []

#starting server
#-----------------------------------------------------
serverSoc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0) #socket d'écoute
serverSoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #ferme la connection qd deconnexion
serverSoc.bind(('', PORT))
serverSoc.listen(1)
#-----------------------------------------------------


#LOOPBACK:
while(True)
    (connected, _, _) = select.select( socketss + [serverSoc], [], [])

    #browse all connected sockets
    for i in connected:
        if (i == serverSoc): #case of new connection
            fffff



        else: #client send command
            fdfd
