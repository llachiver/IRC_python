import socket
import select
import datetime
#import tty
import sys
import time
import fileinput

HOST = '127.0.0.1' #the parameter of the program call will be the chat's IP adress
PORT = 1459
nick = '' #user's nickname
cmd_list={"/HELP":0,"/LIST":0,"/JOIN":1,"/LEAVE":0,"/WHO":0,"/MSG":-1,"/BYE":0,"/KICK":1,"/REN":1} #available commands with their number of arguments 
help_msg = "* /HELP: print this message\n* /LIST: list all available channels on server\n* /JOIN <channel>: join (or create) a channel\n* /LEAVE: leave current channel\n* /WHO: list users in current channel\n* <message>: send a message in current channel\n* /MSG <nick> <message>: send a private message in current channel\n* /BYE: disconnect from server\n* /KICK <nick>: kick user from current channel [admin]\n* /REN <channel>: change the current channel name [admin]"

#--------- FUNCTIONS -------------

def send(msg,s):
    if(msg[0]=='/'):
        words = msg.split()
        cmd = words[0]
        if (cmd in cmd_list):
            if(cmd=="/HELP"):
                print(help_msg)
                return
            if(cmd=="/MSG"):
                if(len(words)<3):
                    print('Erreur : la commande MSG attend 3 arguments minimum.')
                    return
                else:
                    data = "PRV_MSG " + msg[5:]
                    print(data)
            else:
                if(cmd_list[cmd]!=len(words)-1):
                    print('Erreur : la commande %s attend %d argument(s).' % (cmd,cmd_list[cmd]))
                    return
                else:
                    data = msg[1:]

        else:
            print('Erreur : commande inconnue.')
            return
    else:
        if(len(msg)>1):
            data = "MSG " + msg
        else:
            return
        
    s.send(data.encode())


def display(data):
    data += 'bananier'
    return
    print(data+"\n")
    
#--------- CONNECTION -------------
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# Nickname loop
while(nick == ''):
    msg = input('Entrez votre nick : ')
    if(msg!=''):
        s.send(('NICK ' + msg).encode())
        data = s.recv(1024)
        command = data.decode().split()[0]
        if(command == 'ERR'):
            print('Pseudo deja utilise.')
        else:
            nick = msg

#--------- MAIN LOOP -------------

# tty.setraw(sys.stdin) -> désactiver entrée canonique (le message sera envoyé char par char)
#tty.setraw(sys.stdin)
while(1):

    (l,_,_) = select.select([s,sys.stdin],[],[])
    
    for i in l:
        if(type(i) == socket.socket): #if we received sth from the socket
            data = s.recv(1024)
            display(data.decode()[:-1])
        else:
            msg = sys.stdin.readline()
            send(msg,s)
            #print(nick + ' > ' + msg)
