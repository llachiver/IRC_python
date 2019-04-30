import socket
import select
import sys
import datetime
import os
import fnmatch

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
    #> client_socket -> [IP, nick, rank, current channel (string)]

#channels:
    #> type: dictionnary
    #> channelName (string) -> client_socket list (queue)

#admins:
    #> type: dictionnary
    #> channelName (string) -> set of admins

#joined: (not yet used, improve complexity in BYE and LEAVE but increase complexity in REN)
    #> type: dictionnary
    #> client_socket -> set of joined channels
        
clients = dict()
channels = {"HUB":[]}
waiting_room = {}         # socket -> IP

admins = {"HUB":set()}

channels_names = {"HUB"}

nicks = set()

file_transfered={}

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
def send_channel(string, clt_sender, self=False, channel=None):
    target = clients[clt_sender][3]
    if(channel != None):
        target = channel
    log(string + " IN " + target + "\n")
    string += "\n"
    
    for i in channels[target]:
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


def clt_change_channel(clt,new_channel, leaveOld = True):
    
    old_channel = clients[clt][3]
    clients[clt][3] = new_channel
    if(leaveOld or (old_channel == "HUB")):
        channels[old_channel].remove(clt)
    
    #[diffuseClient, (newAdmin), old_channel]
    result = [clt]
    
    #exit a channel:
    if(leaveOld):
        if (old_channel != "HUB"):
            if (channels[old_channel] == []):       #if the old channel becomes empty
                del channels[old_channel]
                del admins[old_channel]
                channels_names.remove(old_channel)
                result[0] = None
            else:
                if (clients[clt][2] == 1): #if he's admin of the channel
                    admins[old_channel].remove(clt)
                    if(len(admins[old_channel]) == 0): #if he was the LAST admin
                        clients[channels[old_channel][0]][2] = 1
                        admins[old_channel].add(channels[old_channel][0])
                        result.append(clients[channels[old_channel][0]][1])
                result[0] = channels[old_channel][0]
    
    clients[clt][2] = 0                    
    
    #enter in a channel:
    if (new_channel in channels_names):  #if the channel already exists
        if(not(clt in channels[new_channel])):
            channels[new_channel].append(clt)
        clients[clt][2] = 1 if (clt in admins[new_channel]) else 0
    else:                                       #else it is created
        channels[new_channel] = [clt]
        channels_names.add(new_channel)
        clients[clt][2] = 1             # the client becomes admin
        admins[new_channel] = set()
        admins[new_channel].add(clt)

    result.append(old_channel)
    return result


#find a file
def find(nick):
    path = os.path.dirname(os.path.realpath(__file__))   #current directory
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, nick):
                return os.path.join(name)
    
#--------------- PICROM FONCTIONS ----------------------


#SEND A FILE
# From client : SEND <nick> <filename>
# From server : SEND <0 : waiting | 1 : finished>


#------------ SEND FILE FUNCTIONS --------------
def picrom_send(clt, args):
    
    channel = clients[clt][3]
    
    if(channel == "HUB"):
        send("ERR 5", clt)
        return
    if(len(args) != 2):
        send("ERR 9", clt)
        return
    
    nick = args[0]      #nick -> personne à qui le clt veut envoyer le fichier
    filename = nick + "_" + args[1]

    if(find(nick+"_*")!=None):      #if a file has already been sent to this recipient
        send("ERR 14",clt)
        return
        
    targetSoc = find_soc_from_nick(nick, clients[clt][3])
    if(targetSoc == None):
        send("ERR 4", clt)
        return
    
    f = open(filename,'wb+')
    file_transfered[clt]=f
    send("SEND 0",clt)      #waiting for transfer



#LOOP FOR SENDING PACKAGES
def picrom_sendF(clt,data):
    f = file_transfered[clt]
    
    if(len(data)>6):   #if we have data after SENDF
        f.write(data[6:])
        clt.send("SENDF\n".encode())   #waiting for the following
        return
    
    nick_recipient = f.name.split('_')[0]
    targetSoc = find_soc_from_nick(nick_recipient, clients[clt][3]) #the client to whom the file is sent

    if(targetSoc == None):      #if he left the chat during the transfer
        send("ERR 4", clt)      #we send "user not found" to the sender
        os.remove(f.name)       #we remove the file
    else:
        send("SEND 1",clt)
        send("RECV "+clients[clt][1],targetSoc)  #else, we notify the recipient that he received a file
    del file_transfered[clt]
    f.close()


#------------ RECV FILE FUNCTIONS --------------
def picrom_recv(clt):
    
    channel = clients[clt][3]
    
    if(channel == "HUB"):
        send("ERR 5", clt)
        return

    nick = clients[clt][1]

    filename = find(nick+"_*")       #search for the file beggining by the nick
    if(filename == None):
        send("ERR 13",clt)
        return
    
    file = open(filename,'rb')
    file_transfered[clt]=file
    send("RECV",clt)                #confirms to the client that the file exist
    
    
def picrom_recvf(clt):

    l=file_transfered[clt].read(1024 - len("RECVF "))
    
    if(len(l) != 0):
        data = "RECVF ".encode()+l
        clt.send(data)
        return

    filename = file_transfered[clt].name
    file_transfered[clt].close
    os.remove(filename)

    del file_transfered[clt]
    
    send("RECVF", clt)
    

#LOOP FOR SENDING PACKAGES



#---------- OTHER PICROM FUNCTIONS ------------
    

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

    
    while(clients[clt][3] != "HUB"): #leave all channels not already leaved
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
    channelName = args[0]#the name of the channel he wants to join
    if((channelName in channels) and (clt in channels[channelName])):
        send("ERR 11", clt)
        return
    if(channelName == "HUB"):                               #rare case if try to join special channel "HUB"
        send("ERR 10", clt)
        return
    
    clt_change_channel(clt,channelName, current_location == "HUB")
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
    
    send_channel("MSG "  + clients[clt][3] + " " + str(clients[clt][2]) + " " + clients[clt][1] +" "+message,clt)
    



def picrom_prv_msg(clt, args):
    if (len(args) < 3):
        send("ERR 9", clt)
        return
    if(clients[clt][3] == "HUB"):
        send("ERR 5", clt)
        return

    try:
        nbTargets = int(args[0])
    except ValueError:
        send("ERR 9", clt)
        return
    if((len(args)) <= nbTargets + 1):
        send("ERR 9", clt)
        return
    
    message = ' '.join(word for word in args[(nbTargets + 1):])
    
    for i in range(1, nbTargets+1):
        target = args[i]
        if(target == clients[clt][1]):   #auto-msg
            send("ERR 2", clt)
            continue
        targetSoc = find_soc_from_nick(target, clients[clt][3])
        if(targetSoc == None):
            send("ERR 4", clt)
            continue
        send("PRV_MSG "  + clients[clt][3] + " " + str(clients[clt][2]) + " " + clients[clt][1] + " " +  message, targetSoc)


    
def picrom_who(clt):
    if(clients[clt][3] == "HUB"):
        send("ERR 5", clt)
        return
    string = "WHO"
    for i in channels[clients[clt][3]]:
        string += " " + ("1" if (i in admins[clients[clt][3]]) else "0") + " "+ clients[i][1]
    
    send(string, clt)



def picrom_list(clt):
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
    admins[newN] = admins.pop(oldN)
    
    send_channel(("REN "  + oldN + " " + clients[clt][1] + " " + newN), clt, True)



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
    
    send_channel(("KICK "  + clients[clt][3] + " " + clients[clt][1] + " " + str(clients[targetSoc][2]) + " " + clients[targetSoc][1]), clt, True)
    nextChan = "HUB"
    for i in channels:
        if((targetSoc in channels[i]) and (i != "HUB") and (i != clients[targetSoc][3])):
            nextChan = i
            break
    clt_change_channel(targetSoc,nextChan)



def picrom_leave(clt, brutal = False):
    if(clients[clt][3] == "HUB"):
        send("ERR 5", clt)
        return


    #changing current channel:
    nextChan = "HUB"
    for i in channels:
        if((clt in channels[i]) and (i != "HUB") and (i != clients[clt][3])):
            nextChan = i
            break
    
    result = clt_change_channel(clt,nextChan)
    if(result[0] == None):
        if(not brutal): #case if it leave because it has rage quit
            send(("LEAVE " + result[1] + " 1 " + clients[clt][1]), clt) #send only to exiter
    else:
        if(len(result) == 2):
            send_channel(("LEAVE "   + result[1] + " 0 " + clients[clt][1]), result[0], True, result[1]) #True important because broadcaster has changed
            if(not brutal):
                send(("LEAVE "   + result[1] + " 0 " + clients[clt][1]), clt)
        else:
            send_channel(("LEAVE "   + result[2] + " 1 " + clients[clt][1] + " " + result[1] ), result[0], True, result[2])
            if(not brutal):
                send(("LEAVE "   + result[2] + " 1 " + clients[clt][1] + " " + result[1] ), clt)

    


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

    filename = find(oldN+'_*')
    if(filename != None):      #if he's the recipient of a file
        os.rename(filename, newN+'_'+filename[len(oldN+'_'):])   #we rename it with the new nick
    
    send_all(("NICK " + str(clients[clt][2]) + " " + oldN + " " + newN), clt, True)



def picrom_current(clt, args):
    if(args != []): #client change his current channel, if args == [] client just check his current
        target = args[0]
        if(not (target in channels) or (not(clt in channels[target]))):
            send("ERR 6", clt)
            return
        if(target == clients[clt][3]):
            send("ERR 11", clt)
            return
        if(target == "HUB"):                               #rare case if try to join special channel "HUB"
            send("ERR 10", clt)
            return
        clients[clt][3] = target
        clients[clt][2] = 1 if (clt in admins[target]) else 0
    send("CURRENT " + clients[clt][3], clt)



def picrom_grant(clt, args):
    if (clients[clt][2] == 0):  #if not admin
        send("ERR 1", clt)
        return
    if (len(args) < 1):
        send("ERR 9", clt)
        return
    target = args[0]
    if(target == clients[clt][1]):   #auto-grant
        send("ERR 2", clt)
        return
    targetSoc = find_soc_from_nick(target, clients[clt][3])
    if(targetSoc == None):
        send("ERR 4", clt)
        return
    if(clients[targetSoc][2] == 1):
        send("ERR 12", clt)
        return
    clients[targetSoc][2] = 1
    admins[clients[clt][3]].add(targetSoc)
    send_channel("GRANT " + clients[clt][3] + " " + clients[clt][1] + " " + clients[targetSoc][1] , clt)



def picrom_revoke(clt, args):
    if (clients[clt][2] == 0):  #if not admin
        send("ERR 1", clt)
        return
    if (len(args) < 1):
        send("ERR 9", clt)
        return
    target = args[0]
    if(target == clients[clt][1]):   #auto-revoke
        send("ERR 2", clt)
        return
    targetSoc = find_soc_from_nick(target, clients[clt][3])
    if(targetSoc == None):
        send("ERR 4", clt)
        return
    if(clients[targetSoc][2] == 0):
        send("ERR 12", clt)
        return
    clients[targetSoc][2] = 0
    admins[clients[clt][3]].remove(targetSoc)
    send_channel("REVOKE " + clients[clt][3] + " " + clients[clt][1] + " " + clients[targetSoc][1] , clt)    


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
    (connected, _, _) = select.select( sockets + [serverSoc] + [sys.stdin], [], [])
    
    #browse all connected sockets
    for s_clt in connected:
        if(type(s_clt) != socket.socket): #case of input in server
            msg = sys.stdin.readline()
            print(msg)
            continue
        
        if (s_clt == serverSoc): #case of new connection
            
            (soc,addr) = serverSoc.accept()
            waiting_room[soc] = addr[0]
            sockets.append(soc)
            log(addr[0] + " joined the waiting room.\n")


        else: #the client is connected

            line = ""
            try:
                line = s_clt.recv(1024)
            except:
                picrom_bye(s_clt)
                continue
            
            if(len(line) == 0): #if a client leaves the server by send void data
                picrom_bye(s_clt)
                continue
                
            else: #the client send a command
                if(len(line)>=5):
                    header = line[0:5]
                    if(header == b'SENDF'):
                        picrom_sendF(s_clt,line)
                        continue  
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
                    elif(command == "CURRENT"):
                        picrom_current(s_clt, args)
                    elif(command == "GRANT"):
                        picrom_grant(s_clt, args)
                    elif(command == "REVOKE"):
                        picrom_revoke(s_clt, args)
                    elif(command == "SEND"):
                        picrom_send(s_clt, args)
                    elif(command == "RECV"):
                        picrom_recv(s_clt)
                    elif(command == "RECVF"):
                        picrom_recvf(s_clt)
                    else:
                        send("ERR 0", s_clt)                #unknown command
               
                    
