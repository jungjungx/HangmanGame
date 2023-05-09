import socket
import threading
import serverclasses
import traceback


#MUTEX LOCK
client_list_lock = threading.Lock()
lobby_list_lock = threading.Lock()
lobby_lock = threading.Lock()

def get_username(addr):
    username= 'user' + str(addr[1])
    return username

def get_create_data(string):
    data = string.split(":")
    name= data[0]
    maxp = int(data[1])
    is_public = int(data[2])
    password= data[3]
    return name,maxp,is_public,password

def handle_client(client_list,client):
    # send the username of the client 
    client.clientsocket.send(client.username.encode('utf-8'))
    create_lobby = b''
    # loop to receive messages from the client
    while True:
        try:
            # receive data from the client
            data = client.clientsocket.recv(1024)
            
            if data==b'CLOSE':
                # client disconnected
                print("Client disconnected via main menu: {}".format(addr))
                with client_list_lock:
                    client_list.remove_user(client.username)


                client.clientsocket.close()  # close the client socket
                break
            elif data==b'JOIN':
                lobbynameb = client.clientsocket.recv(1024)
                lobbyname= lobbynameb.decode('utf-8')
                lobby_to_join = lobby_list.find(lobbyname)
                with lobby_lock:
                    lobby_to_join.add_client(client)
                lobby_to_join.print_users()
                with client_list_lock:
                    client_list.remove_user(client.username)
                handle_lobby(lobby_list,lobby_to_join,client,lobby_to_join.get_lobbydata())
            elif data==b'CREATE':
                #print(f"{client.username} is creating a lobby!")
                lobbydata= client.clientsocket.recv(1024)
                #print(lobbydata)
                create_lobby_data = get_create_data(lobbydata.decode('utf-8'))
                
                with client_list_lock:
                    players= serverclasses.client_list() #list of all players in lobby
                    players.add(client) #add the creating player to the lobby
                    a_lobby = serverclasses.lobby(create_lobby_data[0],create_lobby_data[1],create_lobby_data[2],create_lobby_data[3],client,players, 0)
                    client_list.remove_user(client.username)
                with lobby_list_lock:
                    lobby_list.add(a_lobby)
                    #lobby_list.print()
                    lobby_list.lobbylist()
                handle_lobby(lobby_list,a_lobby,client,lobbydata)

            elif not data:
                # client disconnected
                with client_list_lock:
                    client_list.remove_user(client.username)


                client.clientsocket.close()  # close the client socket
                break

            # broadcast the message to all connected clients
            #for client in client_list.clients:
            userlist= client_list.userlist()
            lobbylist = lobby_list.lobbylist()
            #print(lobbylist)
            if lobbylist == '':
                lobbylist = 'null'
            full_list = userlist + ':' + lobbylist
            client.clientsocket.send(full_list.encode('utf-8'))
            #client.clientsocket.send(lobbylist.encode('utf-8'))
            #print(lobbylist)
            

        except Exception as e:
            print(f"Error with {client.username}: {e}")
            traceback.print_exc()
            with client_list_lock:
                client_list.remove_user(client.username)


            client.clientsocket.close()  # close the client socket
            break
     # close the client connection
    #client.clientsocket.close()
    print("end of thread.")

def handle_lobby(lobby_list,lobby,client,lobbydata):
    #print(f"THIS IS LOBBY DATA: {lobbydata}")
    client.clientsocket.send(lobbydata)
    while True:
        try:
            #gs= str(lobby.gamestate)
            #client.clientsocket.send(gs.encode('utf-8'))
            userlist= lobby.players.userlist()
            client.clientsocket.send(userlist.encode('utf-8'))

            data = client.clientsocket.recv(1024)

            if data == b'quit':
                # client disconnected
                print("quitting")
                lobby.players.remove_user(client.username)
                with client_list_lock:
                    client_list.add(client)
                with lobby_list_lock:
                    if len(lobby.players) == 0:
                        lobby_list.remove(lobby)
                        print("empty lobby, terminating...")
                break
            elif data == b'start':
                lobby.gamestate = 1

        except Exception as e:
            print(f"Error with {client.username}: {e}")
            traceback.print_exc()
            with client_list_lock:
                lobby.players.remove(client)
                client_list.print()

            client.clientsocket.close()  # close the client socket
            break

# create a socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#serversocket.settimeout(10) #for testing p

# set server
port = 9999
host = 'localhost'

# bind the socket to a public host and port
serversocket.bind((host, port))

# listen for incoming connections
serversocket.listen(20) #20 max connections 
print("Server listening on {}:{}".format(host, port))

#list of active clients
client_list = serverclasses.client_list()
lobby_list = serverclasses.lobby_list()

while True:
    try:
        # establish a connection with a client
        clientsocket, addr = serversocket.accept()
        username= get_username(addr)
        tempclient= serverclasses.client_info(username,addr,clientsocket)
        #add client to the list of clients and start thread
        with client_list_lock:
            client_list.add(tempclient)
        
        print("Got a connection from %s" % str(addr))
        client_list.print()

        client_thread = threading.Thread(target=handle_client, args=(client_list,tempclient))
        client_thread.start()
    except KeyboardInterrupt:
        print("Program interrupted by user. Exiting...")  
        break
 
