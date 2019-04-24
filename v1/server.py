import socket
import select
import sys
import datetime

'''
IRC-like chat server

using PICROM Protocol

by Picachoc & ROMAINPC

For more information about protocol:
see README file at:
https://github.com/picachoc/IRC_python


'''

PORT = 1459 #default port for the chat
if(len(sys.argv) == 2):
    try:
        PORT = int(sys.argv[1])
    except:
        print("Unreadable arg !")
        PORT = 1459
HOST = ''

#Each channel gathers its own clients.

#clients:
    #> type: dictionnary
    #> client_socket -> [IP, nick, rank, location (string)]

#channels:
    #> type: dictionnary
    #> channelName (string) -> client_socket list (queue)


        
clients = dict()
channels = {"HUB":[]}
channels_names = {"HUB"}
waiting_room = {}         # socket -> IP
nicks = set()
sockets = []
guest = 1

#-----------------------------------------------------
#Display and save server information
def log(data):
    f= open("log.log","a+")
    print (str(datetime.datetime.now()),data[:-1])
    f.write(str(datetime.datetime.now())+"  :  "+data)
    f.close()


#--------------- SEND FONCTIONS ----------------------
    
#Send to all users connected to the sender's channel.
def send_channel(string, clt_sender, self=False):
    log(string + " IN " + clients[clt_sender][3] + "\n")
    string += "\n"
    for i in channels[clients[clt_sender][3]]:
        if(i != clt_sender):
            i.send(string.encode())
    if(self):
        clt_sender.send(string.encode())
    
#Send to a specific user
def send(string, dest, defined = True):
    name = ""
    if(defined):
        name = clients[dest][1]
    else:
        name = str(waiting_room[dest])
    log(string+" TO "+ name + "\n")
    string += "\n"
    dest.send(string.encode())

#Send to all connected users
def send_all(string, clt_sender, self=False):
    log(string + "\n")
    string += "\n"
    for i in clients:
        if(i != clt_sender):
            i.send(string.encode())
    if(self):
        clt_sender.send(string.encode())


#--------------- PROGRAM FONCTIONS ----------------------

#Returns nickname from a client socket
def find_soc_from_nick(nick, chan):
    for i in channels[chan]:
        if(clients[i][1] == nick):
            return i
    return None


def clt_change_channel(clt,new_channel):
    
    old_channel = clients[clt][3]
    clients[clt][3] = new_channel
    channels[old_channel].remove(clt)
    
    #[diffuseClient, (newAdmin)]
    result = [clt]
    
    #exit a channel:
    if (old_channel != "HUB"):
        if (channels[old_channel] == []):       #if the old channel becomes empty
            del channels[old_channel]
            channels_names.remove(old_channel)
            result[0] = None
        else:
            if (clients[clt][2] == 1):                 #if he's the admin of the channel
                clients[channels[old_channel][0]][2] = 1
                result.append(clients[channels[old_channel][0]][1])
            result[0] = channels[old_channel][0]
    
    clients[clt][2] = 0                      #we can't be admin in the HUB
    
    #enter in a channel:
    if (new_channel in channels_names):       #if the channel already exists
        channels[new_channel].append(clt)
    else:                                       #else it is created
        channels[new_channel] = [clt]
        channels_names.add(new_channel)
        clients[clt][2] = 1                     # the client becomes admin    
    
    return result
    
#--------------- PICROM FONCTIONS ----------------------
    
def picrom_connect(clt, nick):
    addr = waiting_room[clt]
    clients[clt] = [addr[0], nick, 0, "HUB"]
    channels["HUB"].append(clt)
    nicks.add(nick)
    del waiting_room[clt]
    
    send_all(("CONNECT " + nick), clt, True)



def picrom_bye(clt):
    sockets.remove(clt)

    if(clt in waiting_room): #case if the disconnected is in the waiting room
        log(waiting_room[clt] + " leaved the waiting room.\n")
        del waiting_room[clt]
        return

    if(clients[clt][3] != "HUB"): #case if connexion cutted when client is in a channel
        picrom_leave(clt, True)
    
    send_all("BYE " + clients[clt][1], clt)
    nicks.remove(clients[clt][1])
    channels[clients[clt][3]].remove(clt)
    clients.pop(clt)
    clt.close()


        
def picrom_join(clt,args):
    global channels_names
    current_location = clients[clt][3]
    
    if (len(args) < 1):
        send("ERR 9", clt)
        return
    if(current_location != "HUB"):
        send("ERR 5", clt)
        return
    channelName = args[0]                                   #the name of the channel he wants to join
    if(channelName == "HUB"):                               #rare case if try to join special channel "HUB"
        send("ERR 10", clt)
        return
    
    clt_change_channel(clt,channelName)
    #send information, client can know with admin rank if the channel was created
    send_channel(("JOIN " + channelName +" "+ str(clients[clt][2]) + " " + clients[clt][1]), clt, True)
        


def picrom_msg(clt,args):
    if (len(args) < 1):
        send("ERR 9", clt)
        return
    if(clients[clt][3] == "HUB"):
        send("ERR 5", clt)
        return
    
    message = ' '.join(word for word in args)
    
    send_channel("MSG "  + str(clients[clt][2]) + " " + clients[clt][1] +" "+message,clt)
    



def picrom_prv_msg(clt, args):
    if (len(args) < 2):
        send("ERR 9", clt)
        return
    if(clients[clt][3] == "HUB"):
        send("ERR 5", clt)
        return
    
    target = args[0]
    if(target == clients[clt][1]):   #auto-msg
        send("ERR 2", clt)
        return
    targetSoc = find_soc_from_nick(target, clients[clt][3])
    if(targetSoc == None):
        send("ERR 4", clt)
        return
    
    message = ' '.join(word for word in args[1:])
    
    send("PRV_MSG "  + str(clients[clt][2]) + " " + clients[clt][1] + " " +  message, targetSoc)


    
def picrom_who(clt):
    if(clients[clt][3] == "HUB"):
        send("ERR 5", clt)
        return
    string = "WHO"
    for i in channels[clients[clt][3]]:
        string += " " + str(clients[i][2]) + " "+ clients[i][1]
    
    send(string, clt)



def picrom_list(clt):
    if(clients[clt][3] != "HUB"):
        send("ERR 5", clt)
        return
    string = "LIST"
    for i in channels:
        if(i != "HUB"):
            string += " " + i
    
    send(string, clt)



def picrom_ren(clt,args):
    if (clients[clt][2] == 0):
        send("ERR 1", clt)
        return
    if (len(args) < 1):
        send("ERR 9", clt)
        return
    if(clients[clt][3] == "HUB"):
        send("ERR 5", clt)
        return
    oldN = clients[clt][3]
    newN = args[0]
    if(newN in channels_names):
        send("ERR 8", clt)
        return
    for i in channels[clients[clt][3]]:
        clients[i][3] = newN
    channels_names.remove(oldN)
    channels_names.add(newN)
    channels[newN] = channels.pop(oldN)
    
    send_channel(("REN " + clients[clt][1] + " " + oldN + " " + newN), clt, True)



def picrom_kick(clt,args):
    if (clients[clt][2] == 0):  #if not admin
        send("ERR 1", clt)
        return
    if (len(args) < 1):
        send("ERR 9", clt)
        return
    target = args[0]
    if(target == clients[clt][1]):   #auto-kick
        send("ERR 2", clt)
        return
    targetSoc = find_soc_from_nick(target, clients[clt][3])
    if(targetSoc == None):
        send("ERR 4", clt)
        return
    
    send_channel(("KICK " + clients[clt][1] + " " + str(clients[targetSoc][2]) + " " + clients[targetSoc][1]), clt, True)
    clt_change_channel(targetSoc,"HUB")



def picrom_leave(clt, brutal = False):
    if(clients[clt][3] == "HUB"):
        send("ERR 5", clt)
        return

    result = clt_change_channel(clt,"HUB")
    if(result[0] == None):
        if(not brutal): #case if it leave because it has rage quit
            send(("LEAVE 1 " + clients[clt][1]), clt, True) #send only to exiter
    else:
        if(len(result) == 1):
            send_channel(("LEAVE 0 " + clients[clt][1]), result[0], True)
            if(not brutal):
                send(("LEAVE 0 " + clients[clt][1]), clt, True)
        else:
            send_channel(("LEAVE 1 "+ clients[clt][1] + " " + result[1] ), result[0], True)
            if(not brutal):
                send(("LEAVE 1 "+ clients[clt][1] + " " + result[1] ), clt, True)



def picrom_nick(clt,args):
    if (len(args) < 1):
        send("ERR 9", clt)
        return
    oldN = clients[clt][1]
    newN = args[0]
    if(newN in nicks):
        send("ERR 3", clt)
        return
    
    clients[clt][1] = newN
    nicks.remove(oldN)
    nicks.add(newN)
    
    send_all(("NICK " + str(clients[clt][2]) + " " + oldN + " " + newN), clt, True)






#starting server
#-----------------------------------------------------
serverSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) #socket d'écoute
serverSoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #ferme la connection qd deconnexion
serverSoc.bind((HOST, PORT))
serverSoc.listen(1)
log("<========= START SERVER on port "+ str(PORT) + " =========>\n")
#-----------------------------------------------------
    

#LOOPBACK:
while(True):
    (connected, _, _) = select.select( sockets + [serverSoc], [], [])
    
    #browse all connected sockets
    for s_clt in connected:
        if (s_clt == serverSoc): #case of new connection
            
            (soc,addr) = serverSoc.accept()
            waiting_room[soc] = addr[0]
            sockets.append(soc)
            log(addr[0] + " joined the waiting room.\n")


        else: #the client is connected

            line = ""
            try:
                line = s_clt.recv(1500)
            except:
                picrom_bye(s_clt)
                break
            
            if(len(line) == 0): #if a client leaves the server by send void data
                picrom_bye(s_clt)
                break
                
            else: #the client send a command
                
                words = line.decode().split()
                command = ""
                args = ""
                if(len(words) > 0):
                    command = words[0]
                    args = words[1:]

                if(s_clt in waiting_room):
                    if (command == "NICK"):
                        if (len(args) > 0):
                            nick = args[0]
                            if(nick in nicks):              #nick already used
                                send("ERR 3",s_clt, False)
                            else:
                                picrom_connect(s_clt, nick)
                        else:
                            send("ERR 9",s_clt, False)
                    else:
                        send("ERR 7",s_clt, False)

                else:
                    if(command == "JOIN"):
                        picrom_join(s_clt, args)
                    elif(command == "MSG"):
                        picrom_msg(s_clt, args)
                    elif(command == "PRV_MSG"):
                        picrom_prv_msg(s_clt, args)
                    elif(command == "LIST"):
                        picrom_list(s_clt)
                    elif(command == "WHO"):
                        picrom_who(s_clt)
                    elif(command == "KICK"):
                        picrom_kick(s_clt, args)
                    elif(command == "REN"):
                        picrom_ren(s_clt, args)
                    elif(command == "LEAVE"):
                        picrom_leave(s_clt)
                    elif(command == "BYE"):
                        if(clients[s_clt][3] != "HUB"):
                            send("ERR 5",s_clt)
                        else:
                            picrom_bye(s_clt)
                    elif(command == "NICK"):
                        picrom_nick(s_clt, args)
                    else:
                        send("ERR 0", s_clt)                #unknown command
               
                    
