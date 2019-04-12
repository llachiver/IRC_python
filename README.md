# IRC_like chat in Python

### by ROMAINPC & Picachoc

### Default port : 1459

# PICROM Client:
## Available commands:
- /LIST
- /JOIN (channelName)
- /LEAVE
- /WHO
- (message)
- /MSG (nick) (private message)
- /BYE
- /KICK (nick)
- /NICK (newnick)

## Admins commands:
- /KILL (nick)
- /REN (newName)




# PICROM Protocol:
## Protocol commands (Client to Serv):
- (I) MSG (message)
- (I) PRV_MSG (nick) (message)
- (H) LIST
- (H) JOIN (channelname)
- (I) KICK (nick)
- (I) REN (new_channel_name)
- (I) WHO
- (I) LEAVE
- (H) BYE
- (E) NICK (nick)

(E) Everywhere

(H) Hub only

(I) Channel Only

## Protocol commands (Serv to Client):
- (B) ERR (code)
- (AS)CONNECT (firstNick)
- (C) MSG (R) (nick) (message)
- (T) PRV_MSG (R) (nick) (message)
- (B) LIST (channel1) ... (channelN)
- (CS)JOIN (R) (newCommerNick)
- (CS)KICK (adminNick) (R) (nick)
- (AS)REN (R) (nick) (oldName) (newName)
- (B) WHO (R)(client1) ... (R)(clientN)
- (CS) LEAVE (R) (nick)
- (A) BYE (nick)
- (AS)NICK (R) (oldNick) (newNick)

With (R) : rank, 0 if normal, 1 if admin

(A) server command send to all except requester

(C) server command send to channel except requester

(B) server command send to requester

(T) server command send to target client

(S) if server command send also to requester

## Possible server errors:
- ERR 0  wrong command
- ERR 1  unauthorized command (need admin privilege)
- ERR 2  Auto KILL/KICK/BAN
- ERR 3  nick already used
- ERR 4  selected user not on the channel
- ERR 5  unauthorized command (go to HUB or join a channel)
- ERR 7  limit of connexions reached
- ERR 8  channel name already used
- ERR 9 wrong args
- ERR 10 try to join HUB lol
- ERR 11 can't BYE in channel
