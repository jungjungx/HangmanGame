import pygame
import socket


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
dispfont = pygame.font.Font(None, 64)

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

def lobby(client_socket):
    quitbutton = pygame.Rect(WIDTH-300,90,200,50)
    startbutton = pygame.Rect(WIDTH-300,190,200,50)
    lobby_users= "Online in Lobby:"
    data = client_socket.recv(1024)
    data = client_socket.recv(1024)
    create_data = get_create_data(data.decode('utf-8'))
    lobbyname = font40.render("Lobby Name:", True, GREEN)
    nameblit = font40.render(create_data[0], True, BLACK)


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                command = 'quit'
                client_socket.send(command.encode())
                message = 'Hello, server!'
                client_socket.send(message.encode())
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if quitbutton.collidepoint(event.pos):
                    command = 'quit'
                    client_socket.send(command.encode())
                    message = 'Hello, server!'
                    client_socket.send(message.encode())
                    return
                elif startbutton.collidepoint(event.pos):
                    command = 'start'
                    client_socket.send(command.encode())

        window.fill(WHITE)
   
        #gamestate = client_socket.recv(1024)
        
        userlistdata = client_socket.recv(1024)
        print(f"the gs is: {userlistdata}")
        userlist = userlistdata.decode()
        active_users= get_userlist(userlist)
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

        message = 'Hello, server!'
        client_socket.send(message.encode())

        pygame.display.update()

