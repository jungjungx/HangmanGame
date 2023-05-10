import socket
import threading
import serverclasses
import traceback
import random

#MUTEX LOCK
client_list_lock = threading.Lock()
lobby_list_lock = threading.Lock()
lobby_lock = threading.Lock()

#word logic for game
wb_len = 235971

def chosen_word():
    with open("wordbank.txt", "r") as file:
        # Choose a random line number in the range
        random_line_num = random.randint(0, wb_len - 1)

        # Read the corresponding line from the file
        for i, line in enumerate(file):
            if i == random_line_num:
                random_line = line.strip()  # Remove the newline character from the end
                break
    
    #print(random_line)
    
    if(len(random_line)<4 or len(random_line)>6):
        #print('word is too short or long, go again')
        return chosen_word()
    elif(random_line[0].isupper()):
        #print('word is uppercase, restart')
        return chosen_word()
    return random_line

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
                if lobby_to_join.gamestate ==0:
                    handle_lobby(lobby_list,lobby_to_join,client,client_list,lobby_to_join.get_lobbydata())
                else:
                    print("game in progress! cant join...")
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
                handle_lobby(lobby_list,a_lobby,client,client_list,lobbydata)

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

def handle_lobby(lobby_list,lobby,client,client_list,lobbydata):
    #print(f"THIS IS LOBBY DATA: {lobbydata}")
    client.clientsocket.send(lobbydata)
    midquit = 0
    starter = False
    while True:
        try:
            #print("in handle_lobby")
            userlist= lobby.players.userlist()
            if lobby.gameword == None:
                lobby.gameword = "null"
            data2 = userlist + ':' + str(lobby.gamestate) + ':' + lobby.gameword #THE DATA THAT IS SENT TO THE CLIENT
            #print(f"handle_lobby sending to client: {data2}")
            client.clientsocket.send(data2.encode('utf-8'))

            data = client.clientsocket.recv(1024)
            #print(f"receivng from client: {data}")

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
                print("breaking from handle lobby")
                break

            elif data == b'start':
                if len(lobby.players) > 0: #CHANGE IN FINAL VERSION TO 1
                    lobby.gameword = chosen_word()
                    lobby.gamestate = 1
                    print(f"the game word will be: {lobby.gameword}")
                    starter = True
                else:
                    print("not enough players")
                

            if lobby.gamestate == 1:
                    #new updates sent to the client
                    userlist= lobby.players.userlist()
                    if lobby.gameword == None:
                        lobby.gameword = "null"
                    data2 = userlist + ':' + str(lobby.gamestate) + ':' + lobby.gameword #THE DATA THAT IS SENT TO THE CLIENT
                    #print(f"sending to client: {data2}")
                    client.clientsocket.send(data2.encode('utf-8'))

                    data = client.clientsocket.recv(1024)
                    #print(f"receivng from client: {data}")
                    midquit = 0 
                    midquit = handle_game(lobby_list,client,lobby,client_list,data2,starter)
                    #print(midquit)
                    if midquit == 1:
                        print("midquitting")
                        lobby.players.remove_user(client.username)
                        with client_list_lock:
                            client_list.add(client)
                        with lobby_list_lock:
                            if lobby_list.find(lobby) != None:
                                lobby_list.remove(lobby)
                            print("empty lobby, terminating...")
                        return
                    else: handle_game(lobby_list,client,lobby,client_list,data2,starter)



        except Exception as e:
            print(f"Error with {client.username}: {e}")
            traceback.print_exc()
            with client_list_lock:
                lobby.players.remove(client)
                client_list.print()
            with lobby_list_lock:
                    if len(lobby.players) == 0:
                        lobby_list.remove(lobby)
                        print("empty lobby, terminating...")

            client.clientsocket.close()  # close the client socket
            break
    print("end of lobbythread.")

def handle_game(lobby_list,client,lobby,client_list,data2,starter):
    #print("inside handle_game")
    if starter == False:
        test = "0"
        #print(f"you are not the starter, {client.username}")
        client.clientsocket.send(test.encode('utf-8'))
        data = client.clientsocket.recv(1024)
        client.clientsocket.send(test.encode('utf-8'))
    gamedata = str(lobby.gamestate)
    print(gamedata)
    #print(f"receivng from client: {data}")
    #client.clientsocket.send(data2.encode('utf-8'))
    #print(f"sending to client: {data2}")

    winning_time = ''
    winner = ''
    while True:
        try:
            #print("inside loop")
            if lobby.winningtime == None:
                lobby.winningtime = ''
            if lobby.winner == None:
                lobby.winner = ''
            gamedata = str(lobby.gamestate) + ':' + str(lobby.winningtime) + '.' + str(lobby.winner)
            data = client.clientsocket.recv(1024)
            fchar = data[0:1]

            #print(f"receivng from client: {data}")
            client.clientsocket.send(gamedata.encode('utf-8'))
            #print(f"sending to client: {gamedata}")
            #print(data)

            if data ==b'midquit':
                return 1
            elif fchar == b'$':
                print(f"player finished in {data} time!")
                bwinning_time = data[1:].decode()
                lobby.winningtime = str(bwinning_time)
                lobby.winner = client.username
                print(f"{lobby.winner} with official winning time: {lobby.winningtime}")


                lobby.gamestate= 2

        except Exception as e:
            print(f"Error with {client.username}: {e}")
            traceback.print_exc()
            with client_list_lock:
                lobby.players.remove(client)
                client_list.print()
            with lobby_list_lock:
                    if len(lobby.players) == 0:
                        lobby_list.remove(lobby)
                        print("empty lobby, terminating...")

            client.clientsocket.close()  # close the client socket
            break
    print("end of game thread.")



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
 
