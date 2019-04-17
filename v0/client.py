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


#--------- FUNCTIONS -------------

def send(msg,s):
    if(msg[0]=='/'):
        words = msg.split()
        cmd = words[0]
        if (cmd in cmd_list):
            if(cmd=="/MSG"):
                if(len(words)<3):
                    print('Erreur : la commande MSG attend 3 arguments minimum.')
                    return
                else:
                    data = msg[1:]
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
        data = "MSG " + msg
        
    s.send(data.encode())

    
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
            print(str(data))
        else:
            msg = sys.stdin.readline()
            send(msg,s)
            #print(nick + ' > ' + msg)
