import pygame
import sys
import os
import random
import time
import socket

pygame.init()

img_path = './images/'

#length of wordbank
wb_len = 235971

#dimensions for window
height= 800
width = 600
#dimensions for image
imgx= 500
imgy= 500

#colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAYONE = 210 
GRAY = (210, 210, 210)

# Create a font object
font = pygame.font.Font(None, 32)
dispfont = pygame.font.Font(None, 64)
endgamefont = pygame.font.Font(None,128)

def load_images(path):
    scaled_images = {}
    for file in os.listdir(path):
        name, ext = os.path.splitext(file)
        if ext.lower() in ('.png', '.jpg', '.jpeg', '.gif'):
            image = pygame.image.load(os.path.join(path, file))
            scaled_images[name]= pygame.transform.scale(image, (imgx, imgy))
    return scaled_images

def chosen_word():
    with open("wordbank.txt", "r") as file:
        # Choose a random line number in the range
        random_line_num = random.randint(0, wb_len - 1)

        # Read the corresponding line from the file
        for i, line in enumerate(file):
            if i == random_line_num:
                random_line = line.strip()  # Remove the newline character from the end
                break
    
    print(random_line)
    
    if(len(random_line)<4 or len(random_line)>10):
        print('word is too short or long, go again')
        return chosen_word()
    elif(random_line[0].isupper()):
        print('word is uppercase, restart')
        return chosen_word()
    return random_line

def draw_lines(window,word):
    line_width = 40
    line_spacing = 10
    #x = (width - (len(word) * (line_width + line_spacing)))-150 // 2
    x= 64
    y = 475
    for i in range(len(word)):
        if i > 0:
            x += line_width + line_spacing
        pygame.draw.line(window, WHITE, (x, y), (x + line_width, y), 5)
        if i == len(word) - 1:
            x += line_width + line_spacing
        else:
            x += (line_width + line_spacing) // 2

def word_logic(word,guess,result):
    progress = 0
    finish = False
    x= 64
    y = 475
    #guess whole word
    if(len(guess)>1):
        if(guess==word):
            for i in range(len(result)):
                result[i]=1
            finish = True
            return True, finish
    #guess letter
    elif guess in word:
        for i in range(len(word)):
            if word[i]==guess: 
                result[i] =1
                progress= result.count(1)
                print(f'Progress is: {progress} / {len(word)}')
        print(result)
        if(progress>=len(word)):
            finish= True
        return True, finish
    return False, finish

def draw_words(window,word,result):
    x= 64
    y=475
    for index in range(len(result)):
        if result[index] ==1:
            letter_text = dispfont.render(word[index], True, WHITE)
            window.blit(letter_text, (x+10+index*75, y - 40))

def endgame(window,finish,alive,counter):
    if(finish==True):
        letter_text = endgamefont.render("YOU WIN!", True, (104, 248, 134))
        window.blit(letter_text, (width/2-150,height/2-200))
        if counter != 0:
            seconds = counter // 100
            milliseconds = counter % 100
            finalcounter = endgamefont.render(str(seconds) + "." + str(milliseconds)+"s", True, (104, 248, 134))
            window.blit(finalcounter, (width/2-50,height/2-100))
    elif(alive==False):
        letter_text = endgamefont.render("YOU LOSE!", True, (255, 135, 134))
        window.blit(letter_text, (width/2-150,height/2-200))   
    else:
        pass 

def mainmenubutton(window,mult=None):
    mainmenu = pygame.Rect(height-225,25,200,50)

    pygame.draw.rect(window, BLACK, mainmenu, 2)
    pygame.draw.rect(window, GRAY, mainmenu)

    # Add text to the button
    if mult == None:
        text = font.render("Main Menu", True, BLACK)
    else:
        text = dispfont.render("Quit", True, BLACK)
    text_rect = text.get_rect(center=mainmenu.center)
    window.blit(text, text_rect)

def singleplayer(gomain,word=None):
    #pygame.init()
    # Create a Pygame window
    window = pygame.display.set_mode((height, width))
    pygame.display.set_caption("Hangman Game")

    # Set the window background color
    window.fill((0, 0, 0))
    pygame.display.update()

    #load images
    hangman_images = load_images(img_path)

    #define textbox
    input_box = pygame.Rect(64, 525, 400, 40)
    text = ''
    active = False
    box_color = 210
    pygame.draw.rect(window, (box_color,box_color,box_color), input_box)
    #define main menu button
    mainmenu = pygame.Rect(height-225,25,200,50)
    #define restart

    #Game init
    game_state = 1
    alive= True
    if word == None:
        word= chosen_word()
    game_result= [0] * len(word)
    draw_lines(window,word)
    finish= False
    
    #time
    counter = 0
    clock = pygame.time.Clock()
    refresh = pygame.Rect(0,0,100,100)
    pygame.draw.rect(window, BLACK, refresh)
    FPS=100

    # Game loop
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("closing")
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the user clicked inside the input box
                if input_box.collidepoint(event.pos):
                    active = not active
                    if(active):
                        box_color = 255
                    else:
                        box_color = 210
                elif mainmenu.collidepoint(event.pos):
                    print("go back to main menu...")
                    gomain = True
                    return gomain
                else:
                    active = False
                    box_color = 210
            elif event.type == pygame.KEYDOWN:
                # Add or remove characters from the text input box
                if active and alive and finish==False:
                    if event.key == pygame.K_RETURN:
                        #print(text)
                        gameprogress,finish =word_logic(word,text,game_result)
                        text = ''
                        if(gameprogress==True):
                            if(finish==True):
                                print("you have won the game!")
                                break
                        else:
                            if(game_state<=7):
                                game_state+= 1
                                if(game_state==8):
                                    alive= False
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        if finish != True:
            counter += 1

        # Update the Pygame window
        #image render
        window.blit(hangman_images[str(game_state)], (75, 0))
        #line render
        draw_lines(window,word)
        #textbox render
        text_surface = font.render(text, True, (0, 0, 0))
        pygame.draw.rect(window, (box_color, box_color, box_color), input_box)
        window.blit(text_surface, (input_box.x + 5, input_box.y + 7))
        draw_words(window,word,game_result)
        endgame(window,finish,alive,counter)
        #clock render
        seconds = counter // 100
        milliseconds = counter % 100
        if finish != True and alive == True:
            pygame.draw.rect(window, BLACK, refresh)
            textrend = font.render(str(seconds) + "." + str(milliseconds), True, WHITE)
            window.blit(textrend, (25, 25))
            finalcount = counter
        #restart button render
        mainmenubutton(window)
        pygame.display.update()
        clock.tick(FPS)

def multiplayer(gomult,word,client_socket):
        #pygame.init()
    # Create a Pygame window
    window = pygame.display.set_mode((height, width))
    pygame.display.set_caption("Hangman Game")

    # Set the window background color
    window.fill((0, 0, 0))
    pygame.display.update()

    #load images
    hangman_images = load_images(img_path)

    #define textbox
    input_box = pygame.Rect(64, 525, 400, 40)
    text = ''
    active = False
    box_color = 210
    pygame.draw.rect(window, (box_color,box_color,box_color), input_box)
    #define main menu button
    mainmenu = pygame.Rect(height-225,25,200,50)
    #define restart

    #Game init
    game_state = 1
    alive= True
    if word == None:
        word= chosen_word()
    game_result= [0] * len(word)
    draw_lines(window,word)
    finish= False
    
    #time
    counter = 0
    clock = pygame.time.Clock()
    refresh = pygame.Rect(0,0,100,100)
    pygame.draw.rect(window, BLACK, refresh)
    FPS=100

    #network stuff
    message = "Hello world"
    client_socket.send(message.encode())
    #print(f"sending to server: {message}")
    data = client_socket.recv(1024)
    #print(f"receiving from server: {data}")
    winner = False

    # Game loop
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("closing")
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the user clicked inside the input box
                if input_box.collidepoint(event.pos):
                    active = not active
                    if(active):
                        box_color = 255
                    else:
                        box_color = 210
                elif mainmenu.collidepoint(event.pos):
                    print("go back to main lobby...")
                    command = 'midquit'
                    client_socket.send(command.encode())
                    gomult = True
                    return gomult
                else:
                    active = False
                    box_color = 210
            elif event.type == pygame.KEYDOWN:
                # Add or remove characters from the text input box
                if active and alive and finish==False:
                    if event.key == pygame.K_RETURN:
                        #print(text)
                        gameprogress,finish =word_logic(word,text,game_result)
                        text = ''
                        if(gameprogress==True):
                            if(finish==True):
                                print(f"you have won the game in {finalcount}s!")
                                finishtime = '$' + str(finalcount)
                                client_socket.send(finishtime.encode())
                                winner = True
                                break
                        else:
                            if(game_state<=7):
                                game_state+= 1
                                if(game_state==8):
                                    alive= False
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        #data = client_socket.recv(1024)
        #print(f"received from server: {data}")

        client_socket.send(message.encode())
        #print(f"sending to server: {message}")

        if finish != True:
            counter += 1

        # Update the Pygame window
        #image render
        window.blit(hangman_images[str(game_state)], (75, 0))
        #line render
        draw_lines(window,word)
        #textbox render
        text_surface = font.render(text, True, (0, 0, 0))
        pygame.draw.rect(window, (box_color, box_color, box_color), input_box)
        window.blit(text_surface, (input_box.x + 5, input_box.y + 7))
        draw_words(window,word,game_result)
        endgame(window,finish,alive,counter)
        #clock render
        seconds = counter // 100
        milliseconds = counter % 100
        if finish != True and alive == True:
            pygame.draw.rect(window, BLACK, refresh)
            textrend = font.render(str(seconds) + "." + str(milliseconds), True, WHITE)
            window.blit(textrend, (25, 25))
            finalcount = counter
        #restart button render
        mainmenubutton(window,1)
        
        clock.tick(FPS)

        #network stuff
        
        data = client_socket.recv(1024)
        #print(f"receving from server: {data}")
        
        if data[0:1] == b'2' and winner == False:
            print("you lost...")
            index= data.decode().index(".")
            winning_time = data[2:index].decode()
            gamewinner = data[index+1:].decode()
            print(f"winning time was: {winning_time} by {gamewinner}")

            letter_text = endgamefont.render("YOU LOSE!", True, (255, 135, 134))
            window.blit(letter_text, (width/2-150,height/2-200))

            seconds = int(winning_time) // 100
            milliseconds = int(winning_time) % 100
            timeblit = endgamefont.render(str(seconds) + "." + str(milliseconds)+"s", True, (255, 135, 134))
            window.blit(timeblit,(width/2-50,height/2-100)) #
            
            winnerblit = endgamefont.render(gamewinner, True, (255, 135, 134))
            window.blit(winnerblit, (width/2-130,height/2-25))
            alive = False   

        pygame.display.update()

if __name__ == '__main__':
    gomain = False
    while gomain == False:
        gomain = singleplayer(gomain)
        print(gomain)
    print("end of file")
