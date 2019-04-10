import socket
import select
import datetime
import tkinter

'''if(len(sys.argv)==0):
    printf("Error : please specify the chat's IP adress.")'''

HOST = "::1" #the parameter of the program call will be the chat's IP adress
PORT = 1459
nick = "" #user's nickname

# Encode the client 
def string_to_PICROM(string):
    if(string[0]=='/'):
        return (string)[1:].upper().encode() #we delete the '/' and turn the string into capital letters
    return ('MSG'+string).upper().encode()


def PICROM_to_string(data):
    data.decode()

    

with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    #The server gives us a first nick.
    data = s.recv(1024)
    nick = data.decode().split()[1]
    print("Server "+HOST+". Welcome, "+nick+" !")
    while(1):
        msg=input(nick + ': ')
        s.send(string_to_PICROM(msg)) 

    print('Received', repr(data))
