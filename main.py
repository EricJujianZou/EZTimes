import pygame
import json
import os
import tkinter
import datetime
from tkinter import simpledialog

#setting up tkinter for user input
tkinter.Tk().withdraw()

#initializing the screen
pygame.init()
screen = pygame.display.set_mode(size = (1280, 600))
global currentScreen 
currentScreen = "main"

#initializing all of the fonts
baseFontLoc = pygame.font.match_font("calibri")
titleFont = pygame.font.Font(baseFontLoc, 36)
titleFont.bold = True
bodyFont = pygame.font.Font(baseFontLoc, 18)

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

#writes data to a json file
def writeJsonFile(fileName, data):
    fileHandle = open(fileName, "w")
    fileData = json.dumps(data)
    fileHandle.write(fileData)
    fileHandle.close()

#takes a table and returns a new table with pages of length N
def tablePaging(table, plen):
    counter = 0
    pager = []
    pages = []
    for item in table:
        pager.append(item)
        counter += 1
        if counter == plen:
            counter = 0
            pages.append(pager)
            pager = []

    if len(pager) > 0:
        pages.append(pager)
    
    return pages

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

#returns how urgently a task needs to be done with 1 being the highest and 3 being the lowest
def calculateUrgency(task):
    pass

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
        drawText("EZTime", titleFont, (10, 15), (255, 255, 255))
        drawText(f"Welcome back, {username}!", titleFont, (400, 15), (255, 255, 255))
        drawText("Here is your schedule for today!", titleFont, (400, 45), (255, 255, 255))

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
                if event.button == 1:
                    if highlightedButton in buttonHolderMap:
                        currentScreen = buttonHolderMap[highlightedButton]
                        return; #leave the main screen and enter the new screen

def routineScreen(): #add and remove things to your daily routine
    global currentScreen
    currentTasks = readJsonFile("tasks.json")
    taskPages = tablePaging(currentTasks, 10)
    currentPage = 1
    pageCount = len(taskPages)
    selectedTask = -1

    buttons = [
        buttonData("Back", titleFont, (10, 15), (100, 36)),
        buttonData("Forward", titleFont, (1100, 550), (150, 36)),
        buttonData("Back", titleFont, (400, 550), (100, 36)),
        buttonData("New", titleFont, (1100, 15), (80, 36)),
        buttonData("Delete Task", titleFont, (10, 550), (250, 36))
    ]


    buttonHolderMap = {
        1: "main",
    }

    while True:
        #drawing text elements to the screen
        screen.fill(0)

        #rendering all buttons and checking hitboxes
        drawText("Here are all of your outstanding tasks!", titleFont, (400, 15), (255, 255, 255))
        drawText(f"Page {currentPage}", titleFont, (750, 550), (255, 255, 255))

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

        #doing task selection for the deleter to figure out what is going on
        tidx = 0
        hoverTask = -1
        displayY = 55
        if pageCount > 0:
            for task in taskPages[currentPage - 1]: #go through all tasks in the current page, render and check hovering
                if selectedTask == tidx:
                    drawText(task["name"], titleFont, (400, displayY), (255, 0, 0))
                elif checkBounds(400, 1280, mousepos[0]) and checkBounds(displayY, displayY + 36, mousepos[1]):
                    hoverTask = tidx
                    drawText(task["name"], titleFont, (400, displayY), (255, 255, 0))
                else:
                    drawText(task["name"], titleFont, (400, displayY), (255, 255, 255))
                tidx += 1
                displayY += 50

        #if there is a specific task selected details about it should be displayed
        drawText(f"Due Date: {task['year']}/{task['month']}/{task['day']}", bodyFont, (10, 300), (255, 255, 255))
        drawText(f"Progress: {round(task['progress'] / task['length'])}%", bodyFont, (10, 330), (255, 255, 255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    currentScreen = "main"
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if highlightedButton in buttonHolderMap:
                        currentScreen = buttonHolderMap[highlightedButton]
                        return
                    elif highlightedButton == 4: #Create a task
                        #using tkinter to get user input
                        windowTitle = "EZTime Task Creator"
                        taskName = simpledialog.askstring(title = windowTitle, prompt = "Task Name")
                        taskYear = simpledialog.askinteger(title = windowTitle, prompt = "Year Due")
                        taskMonth = simpledialog.askinteger(title = windowTitle, prompt = "Month Due (1-12)")
                        taskDay = simpledialog.askinteger(title = windowTitle, prompt = "Day Due")
                        taskIntensity = simpledialog.askfloat(title = windowTitle, prompt = "Average Hours Daily")

                        #check if a given input is valid
                        try:
                            taskDate = datetime.date(taskYear, taskMonth, taskDay)
                            completionDays = taskDate.toordinal() - datetime.date.today().toordinal()
                            if completionDays <= 0:
                                raise Exception("stinky")
                            elif taskIntensity <= 0 or taskIntensity >= 24:
                                raise Exception("bad task intensity")
                            else: #adding a task to the json file
                                currentTasks.append({
                                    "name": taskName, 
                                    "year": taskYear, 
                                    "month": taskMonth, 
                                    "day": taskDay,
                                    "length": taskIntensity * completionDays,
                                    "progress": 0
                                })
                                writeJsonFile("tasks.json", currentTasks)
                                return #refresh the gui so that the new task can be displayed
                        except: #tell the user that they messed up
                            simpledialog.askstring(title = windowTitle, prompt = "Invalid task data given.")
                    elif highlightedButton == 3: #turn the pages back
                        currentPage = max(currentPage - 1, 1)
                    elif highlightedButton == 2: #turn the pages forward
                        currentPage = min(currentPage + 1, pageCount)
                    #doing the part where button clicking works for the tasks
                    selectedTask = hoverTask
                        

#initializing the 2d display engine
screenHolder = {
    "main": mainScreen,
    "routine": routineScreen,
}

#constant application runtime task
while True:
    screenHolder[currentScreen]()