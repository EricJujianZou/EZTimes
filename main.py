import pygame
import threading

#initializing the screen
pygame.init()
screen = pygame.display.set_mode(size = (2560, 1400), flags = pygame.FULLSCREEN)

#intializing the acquisition of inputs

while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                #exit the program if the escape key is pressed
                pygame.quit()