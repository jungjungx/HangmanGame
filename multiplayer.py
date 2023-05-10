import pygame
import socket
import time
import lobbywindow

pygame.init()

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (210, 210, 210)
LGRAY = (230, 230, 230)
BLUE = (0,0,139)
GREEN = (0,100,0)

# Set the width and height of the screen [width, height]
WIDTH = 800
HEIGHT = 600
BORDER_WIDTH = 3

window = pygame.display.set_mode((WIDTH,HEIGHT))

pygame.display.set_caption("Hangman game")

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Create a new client socket
#client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
server_address = ('localhost', 9999) # Replace with your server's IP address and port number


#FONT STUFF
font = pygame.font.Font(None, 32)
font40 = pygame.font.Font(None, 40)
dispfont = pygame.font.Font(None, 64)
text_surface_attempt = dispfont.render("Attempting to connect to server...", True, (0, 0, 0))
text_x_attempt = (WIDTH - text_surface_attempt.get_width()) // 2
text_y_attempt = (HEIGHT - text_surface_attempt.get_height()) // 2 -100

text_surface_fail = dispfont.render("Failed to connect to server!", True, (0, 0, 0))
text_x_fail = (WIDTH - text_surface_fail.get_width()) // 2
text_y_fail = (HEIGHT - text_surface_fail.get_height()) // 2 -100

#circle 
circle_color = (34, 139, 34)
circle_radius = 18

def mainmenubutton(window,connected):
    if connected==False:
        mainmenu = pygame.Rect(HEIGHT/2,WIDTH/2-100,200,50)
    else:
        mainmenu = pygame.Rect(10,10,200,50)

    #pygame.draw.rect(window, BLACK, mainmenu, 2)
    pygame.draw.rect(window, GRAY, mainmenu)

    # Add text to the button
    text = font.render("Main Menu", True, BLACK)
    text_rect = text.get_rect(center=mainmenu.center)
    window.blit(text, text_rect)
    BORDER_WIDTH = 5
    pygame.draw.rect(window, BLACK, mainmenu, BORDER_WIDTH)

def get_userlist(response):
    userlist= response.split(",")
    return userlist

def get_full_list(response):
    #print(f"fulllist: {response}")
    full_list= []
    if ":" in response:
        full_list= response.split(":")
    else:
        return response, 'null'
    return full_list[0],full_list[1]

def createlobby(window):
    create_button = pygame.Rect(550,500,200,50)
    #pygame.draw.rect(window, BLACK, create_button, 2)
    pygame.draw.rect(window, GRAY, create_button)
    # Add text to the button
    text = font.render("Create Lobby", True, BLACK)
    text_rect = text.get_rect(center=create_button.center)
    window.blit(text, text_rect)
    BORDER_WIDTH = 5
    pygame.draw.rect(window, BLACK, create_button, BORDER_WIDTH)

def joinlobby(window):
    join_button = pygame.Rect(300,500,200,50)
    #pygame.draw.rect(window, BLACK, join_button, 2)
    pygame.draw.rect(window, GRAY, join_button)
    # Add text to the button
    text = font.render("Join Lobby", True, BLACK)
    text_rect = text.get_rect(center=join_button.center)
    window.blit(text, text_rect)
    BORDER_WIDTH = 5
    pygame.draw.rect(window, BLACK, join_button, BORDER_WIDTH)

def lobbybox(window):
    lobbybox = pygame.Rect(250,125,500,350)
    #pygame.draw.rect(window, BLACK, lobbybox, 2)
    pygame.draw.rect(window, LGRAY, lobbybox)
    BORDER_WIDTH = 3
    pygame.draw.rect(window, BLACK, lobbybox, BORDER_WIDTH)

def multi(gomain):
    connected= False
    first_connection= True
    window.fill(WHITE)
    mainmenu = pygame.Rect(HEIGHT/2,WIDTH/2-100,200,50)
    mainmenuC = pygame.Rect(10,10,200,50)
    create_button = pygame.Rect(550,500,200,50)
    join_button = pygame.Rect(300,500,200,50)
    circles = [None] * 7
    for i in range(7):
        circles[i] = pygame.Rect(700 - circle_radius, 150+i*50 - circle_radius, circle_radius*2, circle_radius*2)
    selected_lobby = 0


    active = "Active Users:" 
    lobbies = "Lobbies:"
    create_msg = ''
    command = ''

    window.blit(text_surface_attempt, (text_x_attempt,text_y_attempt))
    pygame.display.update()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(server_address)
        connected = True
    except ConnectionRefusedError:
        print("Could not connect to server!")
        connected = False
    #time.sleep(5)

    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mainmenu.collidepoint(event.pos) and connected == False:
                    print("go back to main menu...")
                    gomain = True
                    return gomain
                if mainmenuC.collidepoint(event.pos) and connected == True:
                    print("go back to main menu...")
                    gomain = True
                    connected == False
                    command = 'CLOSE'
                    client_socket.send(command.encode())
                    client_socket.close()
                    return gomain
                if join_button.collidepoint(event.pos) and connected == True:
                    if len(oplobbies) > 1:
                        command = 'JOIN'
                        client_socket.send(command.encode())
                        #print(f"joining lobby: {oplobbies[selected_lobby]}")
                        lobbyname = oplobbies[selected_lobby]
                        client_socket.send(lobbyname.encode())
                        lobbywindow.lobby(client_socket)

                if create_button.collidepoint(event.pos) and connected == True:
                    create_msg = create_window()
                    if create_msg != 'nope':
                        command = 'CREATE'
                        client_socket.send(command.encode())
                        client_socket.send(create_msg.encode())
                        lobbywindow.lobby(client_socket)
                for i in range(len(circles)):
                    if circles[i].collidepoint(event.pos) and connected == True:
                        if i <= len(oplobbies)-2:
                            selected_lobby = i
                            print(i)
                        else: print("too high!")

        if connected:
            window.fill(WHITE)
            if first_connection==True:
                data = client_socket.recv(1024)
                username= data.decode()
                username_display = f"Welcome, {username}"
                #print("first connection no more")
                first_connection= False
            else :
                #userlistdata = client_socket.recv(1024)
                #userlist = userlistdata.decode()
                #active_users= get_userlist(userlist)
                fulllistdata = client_socket.recv(1024)
                full_list = fulllistdata.decode()

                userlist,open_lobbies = get_full_list(full_list)
                active_users= get_userlist(userlist)
                #print(f"list of active users: {active_users}")
                oplobbies = get_userlist(open_lobbies)

                #visuals
                for i,guy in enumerate(active_users):
                    userblit = font40.render(guy, True, BLACK)
                    window.blit(userblit, [20, 125+i*25])

                activeblit = font40.render(active, True, BLACK)
                lobbyblit = font40.render(lobbies, True, BLACK)
                usernameblit = font40.render(username_display, True, BLACK)

                window.blit(usernameblit, [300, 25])
                window.blit(activeblit, [20, 95])
                window.blit(lobbyblit, [260, 95])


                joinlobby(window)
                createlobby(window)
                lobbybox(window)

                for i,guy in enumerate(oplobbies):
                    if guy != "null":
                        lobbiesblit = font40.render(guy, True, BLACK)
                        #250 125 for lobby box
                        window.blit(lobbiesblit, [275, 140+i*50])
                        if guy !='':
                            if i == selected_lobby:
                                pygame.draw.circle(window, GREEN,[700,150+i*50], circle_radius) # 700, 150 + i * 40 for circles
                            else:
                                pygame.draw.circle(window, WHITE,[700,150+i*50], circle_radius) # 700, 150 + i * 40 for circles


            message = 'Hello, server!'
            client_socket.send(message.encode())

            # Wait for a short time to control the frame rate
            clock.tick(190)
        else:
            window.fill(WHITE)
            window.blit(text_surface_fail, (text_x_fail,text_y_fail))
        # Update the display
        mainmenubutton(window,connected)
        pygame.display.update()

def exit(window):
    x_button = pygame.Rect(WIDTH-275,40,100,50)
    #pygame.draw.rect(window, BLACK, join_button, 2)
    pygame.draw.rect(window, GRAY, x_button)
    # Add text to the button
    text = font.render("Cancel", True, BLACK)
    text_rect = text.get_rect(center=x_button.center)
    window.blit(text, text_rect)
    BORDER_WIDTH = 3
    pygame.draw.rect(window, BLUE, x_button, BORDER_WIDTH)

#create button
def create(window):
    create = pygame.Rect(WIDTH/2-150,450,200,50)
    #pygame.draw.rect(window, BLACK, join_button, 2)
    pygame.draw.rect(window, GRAY, create)
    # Add text to the button
    text = font40.render("Create", True, BLACK)
    text_rect = text.get_rect(center=create.center)
    window.blit(text, text_rect)
    BORDER_WIDTH = 3
    pygame.draw.rect(window, BLUE, create, BORDER_WIDTH)   

#the create textbox
def create_box(window):
    createbox = pygame.Rect(50,25,WIDTH-200,HEIGHT-100)
    #pygame.draw.rect(window, BLACK, lobbybox, 2)
    pygame.draw.rect(window, WHITE, createbox)
    BORDER_WIDTH = 5
    pygame.draw.rect(window, BLUE, createbox, BORDER_WIDTH)

def send_create(name,maxplayers,is_public,password):
    create_options= name
    create_options+= ':'
    create_options+=str(maxplayers)
    create_options+= ':'
    create_options+=str(is_public)
    create_options+= ':'
    if is_public == 1:
        password_msg= 'null'
    else:
        password_msg = password
    create_options+= password_msg
    #print(create_options)
    return create_options

def create_window():
    x_button = pygame.Rect(WIDTH-275,40,100,50)
    input_box = pygame.Rect(190, 140, 350, 40)
    pass_input_box = pygame.Rect(230, 320, 300, 40)
    create_button = pygame.Rect(WIDTH/2-150,450,200,50)
    name_text = ''
    pass_text = ''
    naming_active = False
    pass_active = False
    box_color = (210,210,210)
    passbox_color = (210,210,210)

    title= "Creating a Lobby:"
    naming= "Set Name:"
    max_players= "Max # of Players:"
    mpoptions = ['2','3','4','5']
    mp_select = 0
    mp_chosen = 0
    private_public = "Private or Public:"
    ppoptions = ["Private","Public"]
    pp_select = 1
    pp_chosen = 1
    password = "Set Password:"

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if create_button.collidepoint(event.pos):
                    lobbyname = name_text
                    chosen_playercount = mp_chosen+2
                    chosen_password = pass_text
                    is_public = pp_chosen
                
                    if lobbyname != '':
                        msg = send_create(lobbyname,chosen_playercount,is_public,chosen_password)  
                        return msg
                elif x_button.collidepoint(event.pos):
                    return 'nope'
                if input_box.collidepoint(event.pos):
                    naming_active = not naming_active
                    pass_active = False
                elif pass_input_box.collidepoint(event.pos):
                    pass_active = not pass_active
                    naming_active = False         
                else:
                    naming_active = naming_active
                    pass_active = pass_active
                    box_color = (210,210,210)      
                #editing the textbox colors              
                if(pass_active):
                    passbox_color = (255,255,255)
                else:
                    passbox_color = (210,210,210)     
                if(naming_active):
                    box_color = (255,255,255)
                else:
                    box_color = (210,210,210)
                #the suboptions of the options
                for i,options in enumerate(mpoptions):
                    if pygame.Rect(290+i*40,200,40,40).collidepoint(event.pos):
                        mp_chosen = i
                for i,options in enumerate(ppoptions):
                    if pygame.Rect(290+i*100, 150+120,100,40).collidepoint(event.pos):
                        pp_chosen = i
            elif event.type == pygame.KEYDOWN:
                # Add or remove characters from the text input box
                if naming_active:
                    if event.key == pygame.K_BACKSPACE:
                        name_text = name_text[:-1]
                    elif len(name_text) < 16:
                        name_text += event.unicode
                elif pass_active:
                    if event.key == pygame.K_BACKSPACE:
                        pass_text = pass_text[:-1]
                    elif len(pass_text) < 12:
                        pass_text += event.unicode                   
            for i,options in enumerate(mpoptions):
                if pygame.Rect(290+i*40,200,40,40).collidepoint(mouse_pos):
                    mp_select = i
            for i,options in enumerate(ppoptions):
                if pygame.Rect(290+i*100, 150+120,100,40).collidepoint(mouse_pos):
                    pp_select = i

        #window.fill(WHITE)
        create_box(window)
        exit(window)
        create(window)

        #textbox
        text_surface = font.render(name_text, True, (0, 0, 0))
        pygame.draw.rect(window, box_color, input_box)
        pygame.draw.rect(window, BLACK, input_box, BORDER_WIDTH)
        window.blit(text_surface, (input_box.x + 5, input_box.y + 7))

        #pass textbox
        passtext_surface = font.render(pass_text, True, (0, 0, 0))
        if pp_chosen ==0:
            pygame.draw.rect(window, passbox_color, pass_input_box)
            pygame.draw.rect(window, BLACK, pass_input_box, BORDER_WIDTH)
            window.blit(passtext_surface, (pass_input_box.x + 5, pass_input_box.y + 7))

        titleblit = font40.render(title, True, BLACK)
        namingblit = font.render(naming, True, BLACK)
        maxpblit = font.render(max_players, True, BLACK)
        ppblit = font.render(private_public,True,BLACK)
        passcolor = BLACK if pp_chosen == 0 else GRAY
        passblit = font.render(password,True,passcolor)

        for i,options in enumerate(mpoptions):
            color = BLACK if i == mp_select else GRAY
            if mp_chosen == i:
                color = GREEN
            numblit = font.render(mpoptions[i],True,color)
            window.blit(numblit, [290+i*40, 150+60])

        for i, options in enumerate(ppoptions):
            color = BLACK if i == pp_select else GRAY
            if pp_chosen == i:
                color = GREEN
            privblit = font.render(options,True,color)
            window.blit(privblit, [290+i*100, 150+120])

        sep = 60
        window.blit(titleblit, [75, 50])
        window.blit(namingblit, [75, 150])
        window.blit(maxpblit, [75, 150+sep*1])
        window.blit(ppblit, [75, 150+sep*2])
        window.blit(passblit, [75, 150+sep*3])

        #box =pygame.Rect(290+i*40,200,40,40)
        #pygame.draw.rect(window, BLACK, box)

        pygame.display.update()

if __name__ == '__main__':
    gomain= False
    multi(gomain)