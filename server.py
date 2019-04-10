import socket
import select
import sys


PORT = 1459 #default port for the chat
HOST = ''

#Each channel gathers its own clients.

#clt_location:
    #> type: dictionnary
    #> client_socket -> channelName (string)

#channels:
    #> type: dictionnary
    #> channelName (string) -> clients

#clients :
    #> type : dictionnary
    #> client_socket -> client

#hub_channel:
    #> type: clients

#client :
    #> type : tuple
    #> (IP, nick)

        
clt_location = {}
channels = {}
hub_channel = {}
nicks = [] 
sockets = []
guest = 1

def log(data):
    f= open("log.txt","a+")
    print (str(datetime.datetime.now()),data)
    f.write(str(datetime.datetime.now())+"  :  "+data)
    f.close()

def send_all(string, clt_sender): #send to all users of a channel -- work in progress
    log(string)
    for i in hub_channel:
        if(i != clt_sender):
            i.send(string.encode())
    for i in channels:
        for j in i:
            if(j != clt_sender):
                j.send(string.encode())

def send(string, dest):
    dest.send(string.encode())
    

def picrom_join(clt,args):
    currentChannel = clt_location[clt]                  #the channel where he's coming from
    this_client = channels[currentChannel][clt]         #(ip,nick)
    client_nick = this_client[1]
    channelName = args[0]                               #the name of the channel he wants to join

    del channels[currentChannel][clt]                   #we delete him from his current channel
    
    channels[channelName][clt]=this_client              #we add him to his new channel
    clt_location[clt] = channelName                     #we change the client's location
    
    currentAdmin = 
    data = "JOIN "+client_nick+
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
            sockets.append(soc)
            if guest < sys.maxsize:#set default nick to new commers
                name = "Guest"+str(guest)
                guest += 1
                hub_channel[soc]= (addr[0], name)
                clt_location[soc]="HUB"
                send(("CONNECT " + name), soc)
                nicks.append(name)
            else:
                send("ERR 7\n", soc)


        else: #the client is connected
            line = s_clt.recv(1500)
            
            if(len(line) == 0): #if a client leaves the server
                send_all("LEAVE " + hub_channel[s_clt][1], i)
                s_clt.close()
                sockets.remove(s_clt)
                nicks.remove(hub_channel[s_clt][1])
                hubClients.pop(s_clt)
                
            else: #the client send a command
                words = line.decode().split()
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
                
               
                    
            

