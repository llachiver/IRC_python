# IRC_like chat in Python

### by ROMAINPC & Picachoc

### Default port : 1459


## Available commands:

- /nick (nick)
- /list (hub only)
- /join (channelName) (hub only)
- /who
- /prv_msg (nick)
- /leave
- /bye (hub only)

## Admins commands:
- /kick (nick)
- /kill (nick)
- /ban (nick)

# PICROM Protocol:
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
- REN (new_channel_name)

## Protocol commands (Serv to Client):
- MSG (R) (nick) (message)
- ERR (code)
- NICK (R) (oldNick) (newNick)
- CONNECT (firstNick)
- LIST (channel1) ... (channelN)
- JOIN (R) (newCommerNick)
- WHO (R)(client1) ... (R)(clientN)
- PRV_MSG (R) (nick) (message)
- LEAVE (R) (nick)
- KICK (adminNick) (R) (nick)
- KILL (adminNick) (R) (nick)
- BAN (adminNick) (R) (nick)

With (R) : rank, 0 if normal, 1 if admin

## Possible server errors:
- ERR 0  wrong command
- ERR 1  unauthorized command (need admin privilege)
- ERR 2  Auto KILL/KICK/BAN
- ERR 3  nick already used
- ERR 4  selected user not on the channel
- ERR 5  unauthorized command (go to HUB or join a channel)
- ERR 6  unexisting or closed channel
- ERR 7  limit of connexions reached
- ERR 8  channel name already used
