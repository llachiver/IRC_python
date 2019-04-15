import socket
import select
import datetime
import tkinter
import sys

HOST = 'bush' #the parameter of the program call will be the chat's IP adress
PORT = 1459
nick = '' #user's nickname

#--------- CONNECTION -------------
s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
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

while(1):
    (l,_,_) = select.select([s,sys.stdin],[],[])
    
    for i in l:
        if(type(i) == socket.socket): #if we received sth from the socket
            data = s.recv(1024)
            print(str(data))
        else:
            msg = sys.stdin.readline()
            s.send(msg.encode())
            #print(nick + ' > ' + msg)
