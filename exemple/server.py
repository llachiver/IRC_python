import socket
import select
import datetime

PORT = 7777
clients = {} # socket : [adresse, nick]
lsocket=[]

#-----------------------------------------------------
s = socket.socket(socket.AF_INET6,socket.SOCK_STREAM,0) #socket d'écoute
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) #ferme la connection qd deconnexion
s.bind(('',PORT))
s.listen(1)

#-----------------------------------------------------

def log(data):
    f= open("log.txt","a+")
    print (str(datetime.datetime.now()),data)
    f.write(str(datetime.datetime.now())+"  :  "+data)
    f.close()

def send_all(data,source):
    log(data)
    for i in clients:
        if i!=source:
            i.send(data.encode())

def send(data,dest):
    log(data)
    dest.send(data.encode())
    
while(1):
    
    for i in clients:
        lsocket=lsocket.append(i)
    (sock_disp,_,_) = select.select(lsocket+[s],[],[])

    
    for clt in sock_disp:
        
        if(clt==s): #si socket d'écoute, clt vient de se connecter
            (client,client_addr) = clt.accept()
            clients[client]=[client_addr,""] #on l'ajoute à la liste des clients
            join = "JOIN "+client_addr[0]+"\n"
            send_all(join,clt)
            
        else: #sinon, nouveau message d'un client
            
            data = clt.recv(1500)

            if(len(data)==0):
                leave="LEAVE "+client_addr[0]+"\n"
                send_all(leave,clt)
                clt.close()
                clients.remove(clt)
                
            else:
                dataStr = data.decode()
                words = dataStr.split()
                
                if(words[0]=="MSG"):
                    data = "MSG "+client_addr[0]+" "+dataStr[4:]
                    send_all(data,clt)
                    '''
                elif(words[0]=="NICK"):
                    data = "NICK "+client_addr[0]+" "+dataStr[4:]
                    send_all(data,clt)



                    

                elif(words[0]=="LIST"):
                    for i in clients:
                        data = clients
                    data = "NICK "+client_addr[0]+" "+dataStr[4:]
                    send_all(data,clt)

                elif(words[0]=="KILL"):
                    data = "NICK "+client_addr[0]+" "+dataStr[4:]
                    send_all(data,clt)
                    
                else:
                    send("Erreur commande.\n",clt)'''
    




