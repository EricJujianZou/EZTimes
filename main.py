import pygame
import json
import time
import os

#initializing the screen
pygame.init()
screen = pygame.display.set_mode(size = (2560, 1400), flags = pygame.FULLSCREEN)
global currentScreen 
currentScreen = "main"

#initializing all of the fonts
baseFontLoc = pygame.font.match_font("calibri")
titleFont = pygame.font.Font(baseFontLoc, 36)
titleFont.bold = True
textFont = pygame.font.Font(baseFontLoc, 18)

class buttonData:
    def __init__(self, text, font, position, size):
        self.text = text
        self.font = font
        self.position = position
        self.size = size

#streams a json file and returns the python data
def readJsonFile(fileName):
    fileHandle = open(fileName, "r")
    fileData = json.loads(fileHandle.read())
    fileHandle.close()
    return fileData

#checks if a value is in a range
def checkBounds(min, max, value):
    return min <= value and value <= max

#returns a position so rect's top left vertex will be at variable pos
def leftAlignRect(rect, pos):
    return (rect.midtop[0] + pos[0], rect.midleft[1] + pos[1])

def drawText(txt, textFont, position, color):
    text = textFont.render(txt, True, color)
    textRect = text.get_rect()
    textRect.center = leftAlignRect(textRect, position)
    screen.blit(text, textRect)

def mainScreen():
    #main render task
    environment = os.environ
    global currentScreen

    #getting saved data from the manager
    username = environment["USERNAME"]
    currentTasks = readJsonFile("tasks.json")
    baseSchedule = readJsonFile("fixedSchedule.json")

    buttons = [
        buttonData("Daily Routine", titleFont, (10, 360), (200, 36))
    ]

    buttonHolderMap = {
        1: "routine",
        2: "tasks",
        3: "userdata"
    }

    while True:
        #drawing the title screen and sidebars
        screen.fill(0)
        drawText("EZTime", titleFont, (10, 10), (255, 255, 255))
        drawText(f"Welcome back, {username}!", titleFont, (400, 10), (255, 255, 255))
        drawText("Here is your schedule for today!", titleFont, (400, 40), (255, 255, 255))

        #rendering all buttons and checking hitboxes
        highlightedButton = 0
        mousepos = pygame.mouse.get_pos()
        bidx = 0
        for button in buttons:
            bidx += 1
            buttonPos = button.position
            buttonSize = button.size
            if checkBounds(buttonPos[0], buttonPos[0] + buttonSize[0], mousepos[0]) and checkBounds(buttonPos[1], buttonPos[1] + buttonSize[1], mousepos[1]):
                drawText(button.text, titleFont, buttonPos, (255, 255, 0))
                highlightedButton = bidx
            else:
                drawText(button.text, titleFont, buttonPos, (255, 255, 255))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: #exit the program once escape has been clicked
                    pygame.quit()
                    quit()

            elif event.type == pygame.MOUSEBUTTONDOWN: #handling button clicking
                if highlightedButton in buttonHolderMap:
                    currentScreen = buttonHolderMap[highlightedButton]
                    return; #leave the main screen and enter the new screen

def routineScreen(): #add and remove things to your daily routine
    global currentScreen
    buttons = [
        buttonData("Back", titleFont, (10, 10), (100, 36))
    ]

    buttonHolderMap = {
        1: "main"
    }

    while True:
        screen.fill(0)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    currentScreen = "main"
                    return

#initializing the 2d display engine
screenHolder = {
    "main": mainScreen,
    "routine": routineScreen
}

#constant application runtime task
while True:
    print(currentScreen)
    screenHolder[currentScreen]()