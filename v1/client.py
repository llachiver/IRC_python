import socket
import select
import datetime
import sys
import time
import os

'''
IRC-like chat client

using PICROM Protocol

by Picachoc & ROMAINPC

For more information about client commands:
see README file_send at:
https://github.com/picachoc/IRC_python


'''


HOST = '127.0.0.1' #the parameter of the program call will be the chat's IP adress
PORT = 1459
if(len(sys.argv) == 3):
    try:
        PORT = int(sys.argv[2])
        HOST = sys.argv[1]
    except:
        print("Unreadable arg !")
        PORT = 1459
        HOST = '127.0.0.1'

print("Connexion au serveur à l'adresse " + HOST + ":" + str(PORT))

nick = '' #user's nickname
channel = "HUB"

file_send = None

file_recv = None


cmd_list={"/HELP":0,"/LIST":0,"/JOIN":1,"/LEAVE":0,
          "/WHO":0,"/MSG":-1,"/BYE":0,"/KICK":1,"/REN":1,"/CURRENT":-1,"/NICK":1,"/GRANT":1,"/REVOKE":1,"/SEND":2,"/RECV":1} #available commands with their number of arguments

help_msg = "* /HELP: print this message\n* /LIST: list all available channels on server\n* /JOIN <channel>: join (or create) a channel\n* /LEAVE: leave current channel\n* /WHO: list users in current channel\n* <message>: send a message in current channel\n* /MSG <nick> <message>: send a private message in current channel\n* /BYE: disconnect from server\n* /KICK <nick>: kick user from current channel [admin]\n* /REN <channel>: change the current channel name [admin]"

err_msg={"ERR 0": "Erreur : commande inconnue.",
         "ERR 1": "Erreur : cette commande nécessite les droits d'administrateur.",
         "ERR 2": "Erreur : vous ne pouvez pas vous cibler.",
         "ERR 3": "Erreur : ce pseudo est déjà utilisé.",
         "ERR 4": "Erreur : utilisateur introuvable.",
         "ERR 5": "Erreur : cette commande n'est pas autorisée ici. Faites /LEAVE ou /JOIN <channel>",
         "ERR 6": "Erreur : ce channel n'existe pas.",
         "ERR 8": "Erreur : ce channel existe déjà.",
         "ERR 9": "Erreur : mauvais arguments. Faites /HELP.",
         "ERR 10": "Erreur : vous ne pouvez pas rejoindre le HUB (Créé en projet Réseau en 2019, le HUB est un channel particulier. Son statut particulier de \"HUB\" fait que ce channel est en fait tout simplement la zone d'attente avant de rejoindre un autre channel autre que le HUB qui est, rappelons le, un channel avant tout particulier. Par conséquent une décision particulière et nécessaire par nos soins a été adoptée, il est en conséquence particulièrement impossible d'envoyer des messages depuis le HUB. De toute manière pour savoir ce qu'il est possible de faire dans le HUB ou en dehors(zone non particulière) référez vous particulièrement au README du projet parceque si vous êtes encore là c'est que vous êtes particulièrement au chomage et que nous cassez particulièrement les sockets.)",
         "ERR 11": "Erreur : vous ne pouvez pas JOIN votre propre channel.",
         "ERR 12": "Erreur : cet utilisateur a déjà ce statut.",
         "ERR 13": "Erreur : il n'y a aucun fichier qui vous est destiné.",
         "ERR 14": "Erreur : un fichier a déjà été envoyé à ce client. Veuillez réessayer plus tard."}

#--------- FUNCTIONS -------------


def send(msg,s):
    global file_send
    global file_recv
    leave=0
    
    if(msg[0]=='/'):        #if it's a command
        words = msg.split()
        cmd = words[0]
        
        if (cmd in cmd_list):
            
            if(cmd=="/HELP"):
                print(help_msg)
                return
            
            elif(cmd=="/MSG"):
                if(len(words)<3):
                    print('Erreur : la commande MSG attend 3 arguments minimum.')
                    return
                else:
                    data = "PRV_MSG " + msg[5:]
                    
            elif(cmd=="/BYE"):
                exit()
                
            elif(cmd=="/CURRENT"):
                if(len(words)>2):
                    print('Erreur : la commande CURRENT attend maximum 1 argument.')
                    return
                else:
                    data = msg[1:]
                    
            elif(cmd=="/SEND"):
                try:
                    file_send = open(words[2],'rb')
                except:
                    print("Erreur : fichier introuvable.")
                    return
                data = "SEND "+words[1]+" "+words[2].split('/')[-1]
                
            elif(cmd=="/RECV"):
                if(len(words)!=2):
                    print(err_msg["ERR 9"])
                    return
                filename = words[1]
                file_recv = open(filename,'wb+')
                data = "RECV 0" #waiting for the transfer from the server
                
            else:
                if(cmd_list[cmd]!=len(words)-1):
                    print('Erreur : la commande %s attend %d argument(s).' % (cmd,cmd_list[cmd]))
                    return
                else:
                    if(cmd=="/LEAVE"):
                        leave=1
                    data = msg[1:]

        else:
            print(err_msg["ERR 0"])  #unknown command
            return
    else:
        if(len(msg)>1):     #if it's a message
            data = "MSG " + msg
        else:
            return          #if the client type enter like a retard, we don't do anything

    s.send(data.encode())

    if(leave==1):           #when the user leaves a channel, we display its current location
        s.send("CURRENT".encode())

def picrom_sendf(s):
    global file_send
    l=file_send.read(1024)
    while(l):
        data = "SENDF ".encode()+l
        print(data)
        time.sleep(0.01)        #for letting the time to the program
        s.send(data)
        l=file_send.read(1024)
    s.send("SENDF".encode())

def picrom_recvf(s,data):
    global file_recv
    if(len(data)>6):   #if we have data after RECVF
        file_recv.write(data[6:])
    else:
        print("Téléchargement de "+file_recv.name+"  terminé.")
        s.send("RECV 1".encode())
        file_recv.close()



#----------------- DISPLAY FUNCTIONS -------------------


def display_rank(char,nick): #usefull function to quick generate admin symbol by reading rank integer provided by protocol.
    if(char == "1"):
        return "@"+nick+"@"
    return nick

def display_chan(chan): #usefull function to quick generate admin symbol by reading rank integer provided by protocol.
    return "#"+chan+" | "


def display(s,data):
    
    global file_recv
    
    if(data[0:5] == b"RECVF"):
        picrom_recvf(s,data)
        
    else:
        data = data.decode()[:-1]
        words = data.split()
        cmd = words[0]
        if(cmd == "ERR"):
            if(words[1] == "13"):
                os.remove(file_recv.name)
            data = err_msg[data]
        elif(cmd == "CONNECT"):
            data = words[1] + " a rejoint le serveur."
        elif(cmd == "MSG"):
            data =  display_chan(words[1]) + display_rank(words[2],words[3]) + " > " + (' '.join(data for data in words[4:]))
        elif(cmd == "PRV_MSG"):
            data = display_chan(words[1]) + display_rank(words[2],words[3]) + ' (vous chuchute) > ' + (' '.join(data for data in words[4:]))
        elif(cmd == "LIST"):
            data = "Channels actifs :\n- " + ('\n- '.join(data for data in words[1:]))
        elif(cmd == "JOIN"):
            j_channel, j_rank, j_nick = words[1:]
            if(j_rank=="0"):
                if(j_nick == nick):
                    data = display_chan(words[1]) + "Vous avez rejoint le channel."
                else:
                    data = display_chan(words[1]) + j_nick + " a rejoint le channel."
            else:
                data = "Vous venez de créer le channel " + j_channel

        elif(cmd == "KICK"):
            k_adminNick, k_rank, k_nick = words[2:]
            if(k_nick==nick):
                data = display_chan(words[1]) + display_rank("1",k_adminNick) + " vous a kické !"
            else:
                if(k_adminNick==nick):
                    data = display_chan(words[1]) + "Vous avez kické " + display_rank(k_rank,k_nick) + "."
                else:
                    data = display_chan(words[1]) + display_rank("1",k_adminNick) + " a kické "+  display_rank(k_rank,k_nick) + "."

        elif(cmd == "REN"):
            data = display_chan(words[1]) + display_rank("1",words[2]) + " a renommé le channel en " + words[3]+ "."
            
        elif(cmd == "WHO"):
            string = "Utilisateurs sur le channel :"
            for i in range(1, len(words), 2):
                string += "\n- " + display_rank(words[i],words[i+1]) 
            data = string
            
        elif(cmd == "LEAVE"):
            if(words[3] == nick):
                data = "Vous venez de quitter le channel "+words[1]+"."
            else:
                data = words[3] + " a quitté le channel."
                if(words[2] == "1"):
                    if(words[3] == nick):
                        data += " Vous devenez administrateur."
                    else:
                        data += " " + words[4] +" devient administrateur."
                        
        elif(cmd == "BYE"):
            data = words[1] + " a quitté le serveur."
            
        elif(cmd == "CURRENT"):
            data = "Vous êtes dans le channel "+words[1]+"."
            
        elif(cmd == "NICK"):
            rank,oldNick,newNick = words[1:]
            if(oldNick == nick):
                data = "Vous vous êtes renommé en " + newNick + "."
            else:
                data = oldNick + " s'est renommé en " + newNick + "."
            
        elif(cmd == "GRANT"):
            chan, adminNick, newAdmin = words[1:]
            if(newAdmin == nick):
                data = display_chan(chan) + display_rank("1",adminNick) + " vous a OPé."
            else:
                data = display_chan(chan) + display_rank("1",adminNick) + " a OPé " + newAdmin + "."
            
        elif(cmd == "REVOKE"):
            chan, adminNick, oldAdmin = words[1:]
            if(oldAdmin == nick):
                data = display_chan(chan) + display_rank("1",adminNick) + " vous a dé-OPé."
            else :
                data = display_chan(chan) + display_rank("1",adminNick) + " a dé-OPé " + oldAdmin + " admin."

        elif(cmd == "SEND"):
            global file_send
            state = words[1]
            if(state=='0'):
                print('Démarrage du transfert de '+file_send.name+'.')
                picrom_sendf(s)
            if(state == "1"):
                print('Transfert de '+file_send.name+' terminé !')
                file_send.close()

        elif(cmd == "RECV"):
            print(words[1] + " vous a envoyé un fichier. Faites /RECV <filename> pour le télécharger.")
            
        print(data)
    
#--------- CONNECTION -------------
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((HOST, PORT))
except:
    print("Connexion impossible au serveur " + HOST + ":" + str(PORT))
    exit()
    
# Nickname loop
while(nick == ''):
    msg = input('Entrez votre nick : ')
    if(msg!=''):
        s.send(('NICK ' + msg).encode())
        data = s.recv(1024)
        command = data.decode().split()[0]
        if(command == 'ERR'):
            print(err_msg['ERR 3'])
        else:
            nick = msg
            print("Connecté au serveur "+ HOST +". Bienvenue, "+nick+" !")

#--------- MAIN LOOP -------------

# tty.setraw(sys.stdin) -> désactiver entrée canonique (le message sera envoyé char par char)
#tty.setraw(sys.stdin)
while(1):

    (l,_,_) = select.select([s,sys.stdin],[],[])
    
    for i in l:
        if(type(i) == socket.socket): #if we received sth from the socket
            data = s.recv(1024)
            if (len(data) != 0):
                display(s,data) #displays coming data
        else:
            msg = sys.stdin.readline()
            send(msg,s)
            #print(nick + ' > ' + msg)
