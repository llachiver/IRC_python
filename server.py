import socket
import select
import sys
import datetime


PORT = 1459 #default port for the chat
HOST = ''

#Each channel gathers its own clients.

#clt_location:
    #> type: dictionnary
    #> client_socket -> channelName (string)

#channel:
    #> type: dictionnary
    #> channelName (string) -> clients dictionnary

#client :
    #> type : dictionnary element
    #> client_socket -> (IP, nick, rank)

        
clt_location = {}
channels = {"HUB":{}}
channels_names = {"HUB"}
nicks = [] 
sockets = []
guest = 1
#-----------------------------------------------------
def log(data):
    f= open("log.txt","a+")
    print (str(datetime.datetime.now()),data[:-1])
    f.write(str(datetime.datetime.now())+"  :  "+data)
    f.close()

def send_channel(string, clt_sender): #send to all users of a channel -- work in progress
    log(string + " IN " + clt_location[clt_sender] + "\n")
    string += "\n"
    for i in clt_location[clt_sender]:
        if(i != clt_sender):
            i.send(string.encode())
    

def send(string, dest, defined = True):
    name = str(dest)
    if(defined):
        name = channels[clt_location[dest]][dest][1]
    log(string+" TO "+ name + "\n")
    string += "\n"
    dest.send(string.encode())

def send_all(string, clt_sender):
    log(string + "\n")
    string += "\n"
    for i in sockets:
        if(i != clt_sender):
            i.send(string.encode())
    
#-----------------------------------------------------
def picrom_new_co(clt, addr):
    global guest
    sockets.append(clt)
    if guest < sys.maxsize:#set default nick to newcomers
        name = "Guest" + str(guest)
        guest += 1
        channels["HUB"][clt] = (addr[0], name, 0)
        clt_location[clt] = "HUB"
        send(("CONNECT " + name), clt)
        send_all(("CONNECT " + name), clt)
        nicks.append(name)
    else:
        send("ERR 7", clt, False)





    '''        
def picrom_join(clt,args):
    channelName = args[0]                               #the name of the channel he wants to join
    if(channelName == "HUB"):
        
        currentChannel = clt_location[clt]                  #the channel where he's coming from
        this_client = channels[currentChannel][clt]         #(ip,nick)
        client_nick = this_client[1]

    del channels[currentChannel][clt]                   #we delete him from his current channel
    
    channels[channelName][clt]=this_client              #we add him to his new channel
    clt_location[clt] = channelName                     #we change the client's location
    
    currentAdmin = channels[channelName]
    data = "JOIN "+client_nick+
'''



def picrom_bye(clt):
    send_all("BYE " + channels["HUB"][clt][1], clt)
    sockets.remove(clt)
    nicks.remove(channels["HUB"][clt][1])
    channels["HUB"].pop(clt)
    clt.close()

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
