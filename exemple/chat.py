#!/usr/bin/python3
import socket
import select



clients = [] #(socket, addr, nick)


def sendToOthers(string, l, origin):
    for i in l:
        if(i[0] != origin):
            i[0].send(string.encode())
        
def getID(c):
    string = c[2]
    if(string == ""):
        string = c[1][0]+":"+str(c[1][1])
    return string



monSoc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
monSoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
monSoc.bind(('',7777))
monSoc.listen(1)
#Boucle d'écoute principale: 
while(True):
    clientsSocket = []
    for loop in clients:
        clientsSocket.append(loop[0])
    (l1,l2,l3) = select.select(clientsSocket + [monSoc],[],[])
    for i in l1:
        if(i == monSoc):
            (socEntrant,addrEntrante) = monSoc.accept()
            clients.append([socEntrant,addrEntrante,""])
            #connexion:
            print("JOIN " , addrEntrante)
            sendToOthers("JOIN " + addrEntrante[0]+":"+str(addrEntrante[1])+"\n", clients, socEntrant)
        else:
            c = ()
            for loop in clients:
                if(loop[0] == i):
                    c = loop
            data = c[0].recv(1500)
            
            if(len(data) == 0):
                #déconnexion:
                print("PART " , getID(c))
                sendToOthers("PART " + getID(c)+"\n", clients, c[0])
                c[0].close()
                clients.remove(c)
                
            else:
                #analyse du message : (commandes dispo: cf, TD)
                #Si aucune commande reconnue -> ERR renvoyé au client qui a tenté
                dataStr = data.decode()
                words = dataStr.split()
                if(len(words) > 0):
                    command = words[0]


                    
                    if(command == "MSG"):
                        #envoie d'un message (envoie à tout le monde):
                        #MSG ipExpéditeur message
                        print("MSG "+ getID(c)+" "+data.decode()[4:-1])
                        sendToOthers("MSG "+ getID(c)+" "+data.decode()[4:], clients, c[0])
                    elif(command == "NICK"):
                        #renommage:
                        print("NICK "+ c[1][0]+":"+str(c[1][1])+" "+data.decode()[5:-1])
                        sendToOthers("NICK "+ c[1][0]+":"+str(c[1][1])+" "+data.decode()[5:], clients, c[0])
                        c[2] = data.decode()[5:-1]
                    elif(command == "LIST"):
                        #récupère la liste des clients:
                        print("LIST "+ getID(c))
                        c[0].send(b"Connected users : (<IP>,<name>)\n")
                        for loop in clients:
                            string = "  -> "
                            string += loop[1][0]+":"+str(loop[1][1])
                            string += " "+ loop[2]
                            if(c == loop):
                                string += " (you) "
                            string += "\n"
                            c[0].send(string.encode())
                    elif(command == "KILL"):
                        target = c
                        for loop in clients:
                            if(data.decode()[5:-1] == loop[2] or data.decode()[5:-1] == (loop[1][0] + str(loop[1][1]))):
                                target = loop
                        if(target == c):
                            #code d'erreur 42 : tentative de suicide
                            c[0].send(b"ERR 42\n")
                        else:
                            print("KILL "+ getID(c)+" "+getID(target))
                            sendToOthers("KILL "+ getID(c)+" "+getID(target)+"\n", clients, c[0])
                            target[0].send(b"!!! Vous vous etes fait kicker connard !!!\n")
                            
                            target[0].close()
                            clients.remove(target)
                    else:
                        #code d'erreur 0 : commandes inconnue
                        c[0].send(b"ERR 0\n")
                else:
                    #code d'erreur 1 : données vides
                    c[0].send(b"ERR 1\n")


                
                                
                
monSoc.close()

















































monSoc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
monSoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
monSoc.bind(('',7777))
monSoc.listen(1)
clients = []
while(True):
    (l1,l2,l3) = select.select(clients + [monSoc],[],[])
    for i in l1:
        if(i == monSoc):
            (socEntrant,addrEntrante) = monSoc.accept()
            clients.append(socEntrant)          
            print(addrEntrante[0],"join the game.")
        else:
            data = i.recv(1500)
            if(len(data) == 0):
                print(addrEntrante[0],"left the game.")
                i.close()
                clients.remove(i)
            else:
                for j in clients:
                    if(i != j):
                        j.send(data)



monSoc.close()
    

    







