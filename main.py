import pygame
import json
import time
import os

#initializing the screen
pygame.init()
screen = pygame.display.set_mode(size = (2560, 1400), flags = pygame.FULLSCREEN)
currentScreen = "main"

#initializing all of the fonts
baseFontLoc = pygame.font.match_font("calibri")
titleFont = pygame.font.Font(baseFontLoc, 36)
titleFont.bold = True
textFont = pygame.font.Font(baseFontLoc, 18)

#streams a json file and returns the python data
def readJsonFile(fileName):
    fileHandle = open(fileName, "r")
    fileData = json.loads(fileHandle.read())
    fileHandle.close()
    return fileData

#returns a position so rect's top left vertex will be at variable pos
def leftAlignRect(rect, pos):
    return (rect.midtop[0] + pos[0], rect.midleft[1] + pos[1])

def drawText(txt, textFont, position):
    text = textFont.render(txt, True, (255, 255, 255))
    textRect = text.get_rect()
    textRect.center = leftAlignRect(textRect, position)
    screen.blit(txt, textRect)

def mainScreen():
    #main render task
    environment = os.environ

    #getting saved data from the manager
    username = environment["USERNAME"]
    currentTasks = readJsonFile("tasks.json")
    baseSchedule = readJsonFile("fixedSchedule.json")
    while True:
        #drawing the title screen and sidebars
        screen.fill(0)
        text = titleFont.render("EZProductivity", True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = leftAlignRect(textRect, (10, 10))
        screen.blit(text, textRect)

        text = titleFont.render(f"Welcome back, {username}!", True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = leftAlignRect(textRect, (400, 10))
        screen.blit(text, textRect)

        text = titleFont.render("Here is today's schedule!", True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = leftAlignRect(textRect, (400, 40))
        screen.blit(text, textRect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: #exit the program once escape has been clicked
                    pygame.quit()
                    quit()

#initializing the 2d display engine
screenHolder = {
    "main": mainScreen
}

#constant application runtime task
while True:
    screenHolder[currentScreen]()