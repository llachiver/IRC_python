import socket
import select
import sys
import datetime


PORT = 1459 #default port for the chat
HOST = ''

#Each channel gathers its own clients.

#clients:
    #> type: dictionnary
    #> client_socket -> [IP, nick, rank, location (string)]

#channel:
    #> type: dictionnary
    #> channelName (string) -> client_socket list (queue)


        
clients = dict()
channels = {"HUB":[]}
channels_names = {"HUB"}
nicks = set()
sockets = []
guest = 1
#-----------------------------------------------------
def log(data):
    f= open("log.txt","a+")
    print (str(datetime.datetime.now()),data[:-1])
    f.write(str(datetime.datetime.now())+"  :  "+data)
    f.close()

def send_channel(string, clt_sender, self=False):
    log(string + " IN " + clients[clt_sender][3] + "\n")
    string += "\n"
    for i in channels[clients[clt_sender][3]]:
        if(i != clt_sender):
            i.send(string.encode())
    if(self):
        clt_sender.send(string.encode())
    

def send(string, dest, defined = True):
    name = str(dest)
    if(defined):
        name = clients[dest][1]
    log(string+" TO "+ name + "\n")
    string += "\n"
    dest.send(string.encode())

def send_all(string, clt_sender, self=False):
    log(string + "\n")
    string += "\n"
    for i in sockets:
        if(i != clt_sender):
            i.send(string.encode())
    if(self):
        clt_sender.send(string.encode())
    
#-----------------------------------------------------
def picrom_new_co(clt, addr):
    global guest
    sockets.append(clt)
    if guest < sys.maxsize:                                     #set default nick to newcomers
        name = "Guest" + str(guest)
        guest += 1
        clients[clt] = [addr[0], name, 0, "HUB"]
        channels["HUB"].append(clt)
        send_all(("CONNECT " + name), clt, True)
        nicks.add(name)
    else:
        send("ERR 9", clt, False)


def picrom_bye(clt):
    if(clients[clt][3] == "HUB"):                                                 
        send_all("BYE " + clients[clt][1], clt)
        sockets.remove(clt)
        nicks.remove(clients[clt][1])
        channels["HUB"].remove(clt)
        clients.pop(clt)
        clt.close()
    else:
        send("ERR 11", clt)


        
def picrom_join(clt,args):
    global channels_names
    if (len(args) < 1):
        send("ERR 9", clt)
    else:
        channelName = args[0]                                   #the name of the channel he wants to join
        if(channelName == "HUB"):                               #rare case if try to join special channel "HUB"
            send("ERR 10", clt)
            return
        if(clients[clt][3] == "HUB"):
            
            channels["HUB"].remove(clt)                           
            existing = channelName in channels_names
            
            if(existing):
                channels[channelName].add(clt)
            else:
                channels[channelName] = {clt}
                channels_names.add(channelName)
                
            clients[clt][3] = channelName
                
            #send information, client can know with admin rank if the channel was created
            send_channel(("JOIN " + ("0 " if existing else "1 ") + clients[clt][1]), clt, True)

        else:
            send("ERR 5", clt)






'''

def picrom_msg(clt,args):
def picrom_nick(clt,args):
def picrom_list(clt,args):
def picrom_kill(clt,args):
def picrom_ban(clt,args):

'''
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
    for s_clt in connected:
        #print(clt_location[s_clt]);
        if (s_clt == serverSoc): #case of new connection
            
            (soc,addr) = serverSoc.accept()
            picrom_new_co(soc, addr)


        else: #the client is connected
            line = s_clt.recv(1500)
            
            if(len(line) == 0): #if a client leaves the server by send void data
                picrom_bye(s_clt)
                
            else: #the client send a command
                words = line.decode().split()
                command = ""
                args = ""
                if(len(words) > 0):
                    command = words[0]
                    args = words[1:]

                if(command == "JOIN"):
                    picrom_join(s_clt,args)
                elif(command == "MSG"):
                    picrom_msg(s_clt,args)
                elif(command == "NICK"):
                    picrom_nick(s_clt)
                elif(command == "LIST"):
                    picrom_list(s_clt)
                elif(command == "KILL"):
                    picrom_kill(s_clt,args)
                elif(command == "BAN"):
                    picrom_ban(s_clt,args)
                elif(command == "BYE"):
                    picrom_bye(s_clt)




                else:
                    send("ERR 0", s_clt)
               
                    
            
serverSoc.close()
