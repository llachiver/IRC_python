import socket
import select
import sys


PORT = 1459
HOST = ''


#Each channel gathers its own clients.

#channels:
    #> type: dictionnary
    #> channelName (string) -> client
#hub_channel:
    #> type: dictionnary
    #> 
#clients :
    #> type : dictionnary
    #> socket -> client
#client :
    #> type : tuple
    #> (IP, nick)

channels = {}
hub_channel = {}#channel: hub
nicks = [] #existing nicknames

sockets = []

guest = 1



def send_all(string, clt_sender):
    print(string)
    for i in hubClients:
        if(i != clt_sender):
            i.send(string.encode())
    for i in channels:
        for j in i:
            if(j != clt_sender):
                j.send(string.encode())


def send(string, dest):
    dest.send(string.encode())

def log(data):
    f= open("log.txt","a+")
    print (str(datetime.datetime.now()),data)
    f.write(str(datetime.datetime.now())+"  :  "+data)
    f.close()

def picrom_join(clt,args):
    
    data = "MSG"+clients[clt]

def picrom_msg(clt,args):
    data = "MSG"+clients[clt]
    
def picrom_nick(clt,args):
def picrom_list(clt,args):
def picrom_kill(clt,args):
def picrom_ban(clt,args):


#starting server
#-----------------------------------------------------
serverSoc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0) #socket d'écoute
serverSoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #ferme la connection qd deconnexion
serverSoc.bind((HOST, PORT))
serverSoc.listen(1)
#-----------------------------------------------------


def generate_nick():
    name = "Guest"+str(guest)
    guest += 1
    return name



#LOOPBACK:
while(True):
    (connected, _, _) = select.select( sockets + [serverSoc], [], [])

    #browse all connected sockets
    for clt in connected:
        if (clt == serverSoc): #case of new connection
            
            (soc,addr) = serverSoc.accept()
            sockets.append(soc)
            if guest < sys.maxsize:#set default nick to new commers
                name = generate_nick()
                hubClients[soc]= (addr[0], name, "hub")
                send(("CONNECT " + name), soc)
                nicks.append(name)
            else:
                send("ERR 7\n", soc)


        else: #the client is connected
            line = clt.recv(1500)
            
            if(len(line) == 0): #if a client leaves the server
                sendToAllOthers("LEAVE " + hubClients[clt][1], i)
                clt.close()
                sockets.remove(clt)
                nicks.remove(hubClients[clt][1])
                hubClients.pop(clt)
                
            else: #the client send a command
                words = line.decode().split()
                command = words[0]
                args = words[1:]

                if(command == "JOIN"):
                    picrom_join(clt,args)
                elif(command == "MSG"):
                    picrom_msg(clt,args)
                elif(command == "NICK"):
                    picrom_nick(clt)
                elif(command == "LIST"):
                    picrom_list(clt)
                elif(command == "KILL"):
                    picrom_kill(clt,args)
                elif(command == "BAN"):
                    picrom_ban(clt,args)
                
               
                    
            

