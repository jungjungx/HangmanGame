import pygame
import socket
import time
import hangman

pygame.init()
# Define some constants for window size
WIDTH = 800
HEIGHT = 600

# Define some colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (210, 210, 210)
GREEN = (34, 139, 34)

window = pygame.display.set_mode((WIDTH,HEIGHT))

pygame.display.set_caption("Hangman game")

#FONT STUFF
font = pygame.font.Font(None, 32)
font40 = pygame.font.Font(None, 40)
font120 = pygame.font.Font(None, 80)
dispfont = pygame.font.Font(None, 220)

def get_create_data(string):
    #print(f"the string is: {string}")
    data = string.split(":")
    name= data[0]
    maxp = int(data[1])
    is_public = int(data[2])
    password= data[3]
    return name,maxp,is_public,password

def get_userlist(response):
    userlist= response.split(",")
    return userlist

def get_data(incoming):
    data = incoming.split(":")
    userlistdata = str(data[0])
    userlist = get_userlist(userlistdata)
    gamestate = data[1]
    gameword = data[2]
    return userlist, gamestate, gameword

def exit(window):
    button = pygame.Rect(WIDTH-300,90,200,50)
    pygame.draw.rect(window, GRAY, button)
    text = font40.render("QUIT", True, BLACK)
    text_rect = text.get_rect(center=button.center)
    window.blit(text, text_rect)
    BORDER_WIDTH = 5
    pygame.draw.rect(window, GREEN, button, BORDER_WIDTH)

def start(window):
    button = pygame.Rect(WIDTH-300,190,200,50)
    pygame.draw.rect(window, GRAY, button)
    text = font40.render("START", True, BLACK)
    text_rect = text.get_rect(center=button.center)
    window.blit(text, text_rect)
    BORDER_WIDTH = 5
    pygame.draw.rect(window, GREEN, button, BORDER_WIDTH)

def countdown(window):
    start_time = pygame.time.get_ticks()
    countdown_time = 5000 
    run = True
    gamestart = "Game starts in: "
    gametext = font120.render(gamestart,True,BLACK)
    window.blit(gametext, [30, 450])
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        # Calculate the time left in the countdown
        elapsed_time = pygame.time.get_ticks() - start_time
        time_left = max(countdown_time - elapsed_time, 0)
        
        # Render the countdown text
        text = dispfont.render(str(int(time_left / 1000) + 1), True, BLACK)
        text_rect = pygame.Rect(500,370,200,200)
        pygame.draw.rect(window, WHITE, text_rect)
        window.blit(text, text_rect)
        
        # Check if the countdown is finished
        if elapsed_time >= countdown_time:
            run = False
        
        pygame.display.update()

def lobby(client_socket):
    quitbutton = pygame.Rect(WIDTH-300,90,200,50)
    startbutton = pygame.Rect(WIDTH-300,190,200,50)
    lobby_users= "Online in Lobby:"
    data = client_socket.recv(1024)
    data = client_socket.recv(1024)
    create_data = get_create_data(data.decode('utf-8'))
    lobbyname = font40.render("Lobby Name:", True, GREEN)
    nameblit = font40.render(create_data[0], True, BLACK)
    message = 'Hello, server!'
    command = ''
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                command = 'quit'
                client_socket.send(command.encode())
                #message = 'Hello, server!'
                #client_socket.send(message.encode())
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if quitbutton.collidepoint(event.pos):
                    print("quit")
                    command = 'quit'
                    client_socket.send(command.encode())
                    a = client_socket.recv(1024)
                    #message = 'Hello, server!'
                    #client_socket.send(message.encode())
                    return
                elif startbutton.collidepoint(event.pos):
                    command = 'start'
                    print(f"sending to server: {command}")
                    client_socket.send(command.encode())
                    #a = client_socket.recv(1024)
                else:
                    client_socket.send(b'okay')

        window.fill(WHITE)
   
        data = client_socket.recv(1024)
        #print(f"received from server: {data}")
        active_users, gamestate, gameword =get_data(data.decode())
        #print(f"the au is: {active_users}")
        #print(f"gamestate is {gamestate}")
        #print(f"gameword is :{gameword}")

        lobbyblit = font40.render(lobby_users, True, GREEN)

        #visuals
        for i,guy in enumerate(active_users):
            userblit = font40.render(guy, True, BLACK)
            window.blit(userblit, [30, 130+i*25])
        window.blit(lobbyblit, [30, 100])
        window.blit(lobbyname, [30, 50])
        window.blit(nameblit, [220, 50])
        exit(window)
        start(window)

        #print(gamestate)
        if gamestate == '1':
            go2lobby = False
            print("starting game!!!")
            countdown(window)
            go2lobby =hangman.multiplayer(go2lobby,gameword,client_socket)
            if go2lobby:
                break


            

        #HELLO SERVER!
        client_socket.send(message.encode())

        pygame.display.update()

