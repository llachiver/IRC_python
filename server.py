import socket
import select

PORT = 1459

#data structure: list of dictionnaries(channels)
#channels: channelName -> (clients queue)
#clients: socket -> (nick, channel)

channels = []
nicks = [] #existing nicknames


#starting server
#-----------------------------------------------------
s = socket.socket(socket.AF_INET6,socket.SOCK_STREAM,0) #socket d'écoute
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) #ferme la connection qd deconnexion
s.bind(('',PORT))
s.listen(1)

#-----------------------------------------------------
