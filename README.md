# IRC chat in Python

### by ROMAINPC & Picachoc

### Default port : 1459


## Available commands:

- /nick (nick)
- /list
- /join (channelName)
- /who
- /prv_msg (nick)
- /leave
- /bye

## Admins commands:
- /kick (nick)
- /kill (nick)
- /ban (nick)


## Protocol commands (Client to Serv):
- MSG (message)
- NICK (nick)
- LIST
- JOIN (channelname)
- WHO
- PRV_MSG (nick) (message)
- LEAVE
- BYE
- KICK (nick)
- KILL (nick)
- BAN (nick)

## Protocol commands (Serv to Client):
- MSG (nick) (message)
- ERR (code)
- NICK (oldNick) (newNick)
- LIST (channel1) ... (channelN)
- JOIN (newCommerNick) (currentAdmin)
- WHO (client1) ... (clientN)
- PRV_MSG (nick) (message)
- LEAVE (nick)
- KICK (adminNick) (nick)
- KILL (adminNick) (nick)
- BAN (adminNick) (nick)

## Possible server errors:
- ERR 0  wrong command
- ERR 1  unauthorized command (need admin privilege)
- ERR 2  Auto KILL/KICK/BAN
- ERR 3  nick already used
- ERR 4  selected user not on the channel
- ERR 5  try to send when not on a channel
- ERR 6  unexisting or closed channel