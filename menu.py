import pygame
import sys
import os
import hangman
import multiplayer

# Define some constants for window size
WIDTH = 800
HEIGHT = 600

# Define some colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (210, 210, 210)


# Define the main menu options
options = ["Singleplayer", "Multiplayer", "Exit"]
selected_option = 0
inputbox = []
titlefont = pygame.font.Font(None,128)


def get_inputboxes():
    for i, option in enumerate(options):
        inputbox.append([WIDTH/2, HEIGHT/2 + i*40])
        #print(inputbox[i])
    return inputbox

def draw_menu(window):
    global selected_option
    gomain = False
    mouse_pos = pygame.mouse.get_pos()

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("closing")
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_option = (selected_option - 1) % len(options)
            elif event.key == pygame.K_DOWN:
                selected_option = (selected_option + 1) % len(options)
            elif event.key == pygame.K_RETURN:
                if options[selected_option] == "Singleplayer":
                    hangman.singleplayer(gomain)
                    return "singleplayer"
                elif options[selected_option] == "Multiplayer":
                    multiplayer.multi(gomain)
                    return "multiplayer"
                elif options[selected_option] == "Exit":
                    pygame.quit()
                    return None
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the mouse click is inside a button area
            for i, box in enumerate(inputbox):
                if pygame.Rect(box[0]-100, box[1]-20, 200, 40).collidepoint(event.pos):
                    if options[i] == "Singleplayer":
                        hangman.singleplayer(gomain)
                        return "singleplayer"
                    elif options[i] == "Multiplayer":
                        multiplayer.multi(gomain)
                        return "multiplayer"
                    elif options[i] == "Exit":
                        pygame.quit()
                        return None
        for i, box in enumerate(inputbox):  
            if pygame.Rect(box[0]-100, box[1]-20, 200, 40).collidepoint(mouse_pos):
                selected_option = i


    # Draw the menu options
    window.fill(WHITE)
    text = titlefont.render("HANGMAN", True, (0, 0, 0))
    text_x = (WIDTH - text.get_width()) // 2
    text_y = (HEIGHT - text.get_height()) // 2
    window.blit(text, (text_x,text_y-125)) 
    for i, option in enumerate(options):
        color = BLACK if i == selected_option else GRAY
        text = font.render(option, True, color)
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2 + i*40))
        window.blit(text, text_rect)

    # Update the display
    pygame.display.update()

    # Keep the same loop running until the user makes a selection
    return "menu"

if __name__ == '__main__':
    pygame.init()
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hangman Game")
    font = pygame.font.Font(None, 36)
    get_inputboxes()
    while True:
        draw_menu(window)
