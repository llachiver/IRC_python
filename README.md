# IRC_like chat in Python

### by ROMAINPC & Picachoc

### Default port : 1459

# PICROM Client:

Using Tkinter for the GUI: http://tkinter.fdex.eu/

## Available commands:
- /LIST
- /JOIN (channelName)
- /LEAVE
- /WHO
- (message)
- /MSG (nick) (private message)
- /BYE
- /NICK (newNick)
- /CURRENT
- /CURRENT (newCurrentChannel)
- /SEND (nick) (fileName)
- /RECV (outputFileName)

## Admins commands:
- /KICK (nick)
- /REN (newName)
- /GRANT newAdmin
- /REVOKE noMoreAdmin



# PICROM Protocol:
## Protocol commands (Client to Serv):
- (I) MSG (message) : send in current channel
- (I) PRV_MSG N (nick1) (nick2) ... (nickN) (message) :
- (E) LIST
- (E) JOIN (channelname) : (set the current channel also)
- (I) KICK (nick)
- (I) REN (new_channel_name)
- (I) WHO
- (I) LEAVE : (leave the current channel)
- (H) BYE : (leave all channels if not done)
- (E) NICK (nick)
- (E) CURRENT (newCurrentChannel or void)
- (I) GRANT (newAdmin)
- (I) REVOKE (oldAdmin)
- (I) SEND (nick) (file_name)
- (I) SENDF (file_package or void) : will be sent untill the transfer is complete
- (I) RECV : demands to receive the file
- (I) RECVF : package reception ok, waiting for the following



(E) Everywhere

(H) Hub only

(I) Channel Only

## Protocol commands (Serv to Client):
- (B) ERR (code)
- (AS)CONNECT (firstNick)
- (C) MSG (channel) (R) (nick) (message) : receive all MSG from all joined channels
- (T) PRV_MSG (channel) (R) (nick) (message)
- (B) LIST (channel1) ... (channelN)
- (CS)JOIN (channel) (R) (newCommerNick)
- (CS)KICK (channel) (adminNick) (R) (nick)
- (CS)REN (channel) (adminNick) (newName)
- (B) WHO (R)(client1) ... (R)(clientN)
- (Cs) LEAVE (channel) (R) (nick) (newAdmin if (R) == 1)
- (A) BYE (nick)
- (AS)NICK (R) (oldNick) (newNick)
- (B)CURRENT (currentChannel)
- (CS)GRANT (channel) (adminNick) (newAdmin)
- (CS)REVOKE (channel) (adminNick) (oldAdmin)
- (B) SEND (0 : waiting for transfer | 1 : transfer complete)
- (B) SENDF : package reception ok, waiting for the following
- (T|B) RECV (sender_nick | void) : to notify the recipient he received a file from sender_nick | your are ready to RECVF
- (B) RECVF (file_package or void) : will be sent untill the transfer is complete

## Input commands (in Serv shell):
- GLOBAL (message): send a message to everyone



With (R) : rank, 0 if normal, 1 if admin

(A) server command sent to all except requester

(C) server command sent to channel except requester

(B) server command sent to requester

(T) server command sent to target client

(S) if server command send also to requester ((s) if send with a second command)


## Possible server errors:
- ERR 0  wrong command
- ERR 1  unauthorized command (need admin privilege)
- ERR 2  Auto KICK,PRV_MSG, GRANT or REVOKE
- ERR 3  nick already used
- ERR 4  selected user(s) not on the channel
- ERR 5  unauthorized command (go to HUB or join a channel)
- ERR 6 you don't have joined this channel, can't CURRENT
- ERR 7  Need do NICK command before
- ERR 8  channel name already used
- ERR 9 wrong args
- ERR 10 try to join or to current HUB lol
- ERR 11 you already JOIN this channel or its your CURRENT channel
- ERR 12 GRANT admin or REVOKE muggle
- ERR 13 don't have any file for the client
- ERR 14 a file has already been sent to this recipient
