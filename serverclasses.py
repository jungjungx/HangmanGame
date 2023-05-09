class client_info(object):
    def __init__(self,username= None,address=None, clientsocket=None):
        self.address = address
        self.username = username
        self.clientsocket = clientsocket

class client_list(object):
    def __init__(self,clients=None):
        self.clients = []

    def __len__(self):
        return len(self.clients)
    
    def add(self, client):
        self.clients.append(client)
    
    def remove(self,client):
        self.clients.remove(client)

    def remove_user(self,username):
        for client in self.clients:
            if client.username == username:
                #print(f"Removing {client.username}...")
                self.clients.remove(client)
    
    def print(self):
        print("Here is the list of connected clients:")
        for client in self.clients:
            print(f'{client.username}, {client.address}')

    def userlist(self):
        userlist = ''
        for client in self.clients:
            userlist= client.username + ',' + userlist
        #print(userlist)
        return userlist

class lobby(object):
    def __init__(self,lobbyname=None, maxplayers=None, is_public=None, password=None,owner=None, players=None, gamestate=None):
        self.lobbyname = lobbyname
        self.maxplayers= maxplayers
        self.is_public = is_public
        self.password= password
        self.owner = owner
        self.players = players
        self.gamestate = gamestate
    
    def add_client(self,client):
        self.players.add(client)

    def print_users(self):
        self.players.print()

    def get_lobbydata(self):
        create_options= self.lobbyname
        create_options+= ':'
        create_options+=str(self.maxplayers)
        create_options+= ':'
        create_options+=str(self.is_public)
        create_options+= ':'
        if self.is_public == 1:
            password_msg= 'null'
        else:
            password_msg = self.password
        create_options+= password_msg
        lobbydata= create_options.encode('utf-8')
        return lobbydata

class lobby_list(object):
    def __init__(self,lobbies=None):
        self.lobbies = []    

    def add(self, lobby):
        self.lobbies.append(lobby)
    
    def remove(self,lobby):
        self.lobbies.remove(lobby)

    def find(self,name) -> lobby:
        for lobby in self.lobbies:
            if name == lobby.lobbyname:
                print("found lobby")
                return lobby
        return None

    def print(self):
        print("Here is the list of all lobbies:")
        for lobby in self.lobbies:
            print(f'{lobby.lobbyname} by, {lobby.owner.username}')
            print(f"Max p: {lobby.maxplayers}, Public: {lobby.is_public}, Password: {lobby.password}")

    def lobbylist(self):
        lobbylist = ''
        for lobby in self.lobbies:
            if lobby.gamestate == 0:
                lobbylist= lobby.lobbyname + ',' + lobbylist
        #print(f"the lobby list: {lobbylist}")
        return lobbylist
        