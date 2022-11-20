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

#turns a string into a valid point in time of the day
def parseTime(string):
    ez = string.split(":")
    return (int(ez[0]), int(ez[1]))

#returns a new time fast forwarded x amount of minutes
def forwardTime(hour, minute, minutes):
    minute += minutes
    hour += minute // 60
    hour %= 24
    minute %= 60
    return hour, minute

#returns a display string so if there is only one digit in minutes, a zero will be appended
def minDisplay(minutes):
    if minutes < 10:
        return "0" + str(round(minutes))
    return str(round(minutes))
#returns how urgently a task needs to be done with 2 being the highest and 0 being the lowest
urgencyMap = ["Not Urgent", "Urgent", "Very Urgent"]
def calculateUrgency(task):
    dueDate = datetime.date(task["year"], task["month"], task["day"])
    currentDate = datetime.date.today()
    remainingDays = dueDate.toordinal() - currentDate.toordinal()
    reminaingLength = task["length"] - task["progress"]
    urgency = 1
    if remainingDays < 7:
        urgency += 1

    if reminaingLength / remainingDays > 3:
        urgency += 1

    return urgency


def mainScreen():
    #main render task
    environment = os.environ
    global currentScreen

    #getting saved data from the manager
    username = environment["USERNAME"]
    currentTasks = readJsonFile("tasks.json")
    baseSchedule = readJsonFile("fixedSchedule.json")
    userProfile = readJsonFile("userProfile.json")

    buttons = [
        buttonData("Task Manager", titleFont, (10, 360), (200, 36)),
        buttonData("Daily Routine", titleFont, (10, 410), (200, 36)),
        buttonData("Mark Completion", titleFont, (10, 460), (200, 36))
    ]

    buttonHolderMap = {
        1: "tasks",
        2: "routine",
    }

    #determine today's schedule based on the routine and tasks that need to be completed
    currentDate = datetime.date.today()
    dayRoutine = [] #first determine what routine items will occur today
    for routine in baseSchedule:
        if routine["recurring"] == "days":
            dayRoutine.append(routine)
        elif routine["recurring"] == "weeks": #check if the recurring day is today
            currentDay = currentDate.weekday() + 1
            for day in routine["recurData"]:
                if day == currentDay:
                    dayRoutine.append(routine)
                    break
        elif routine["recurring"] == "months": #check if today is in the days of the month specified by the routine
            recurData = routine["recurData"]
            startingDay = recurData[0]
            endingDay = startingDay + recurData[1]
            if checkBounds(startingDay, endingDay, currentDate.day):
                dayRoutine.append(routine)
        elif routine["recurring"] == "years": #check if it is on the specific date set by the year routine
            recurData = routine["recurData"]
            startingDate = datetime.date(currentDate.year, recurData[0], recurData[1]).toordinal()
            if checkBounds(startingDate, startingDate + recurData[2], currentDate.toordinal()):
                dayRoutine.append(routine)
    
    #sort every day routine by when they occur
    dlen = len(dayRoutine)
    if dlen > 0:
        mergeSort = []
        for item in dayRoutine:
            mergeSort.append([item])

        while len(mergeSort) != 1:
            newMerger = []
            for i in range(0, len(mergeSort), 2): #merge smaller tables together
                newTable = []
                oldA = mergeSort[i]
                oldB = mergeSort[i + 1]
                a = 0
                b = 0
                j = 0

                while a < len(oldA) or b < len(oldB):
                    ac = a < len(oldA)
                    bc = b < len(oldB)
                    if (ac and bc): #compare which item is smaller
                        ae = oldA[a]
                        be = oldB[b]
                        if (ae["hour"] * 60 + ae["minute"] < be["hour"] * 60 + be["minute"]):
                            newTable.append(ae)
                            a += 1
                        else:
                            newTable.append(be)
                            b += 1
                    elif ac:
                        newTable.append(ae)
                        a += 1
                    elif bc:
                        newTable.append(be)
                        b += 1

                    j += 1

                newMerger.append(newTable)
            
            mergeSort = newMerger
        
        dayRoutine = mergeSort[0]
    
    #get priority for every task
    vUrgent = []
    urgent = []
    nUrgent = []

    tidx = 0
    for task in currentTasks:
        urgency = calculateUrgency(task)
        if urgency == 3:
            vUrgent.append([tidx, urgency, task])
        elif urgency == 2:
            urgent.append([tidx, urgency, task])
        else:
            nUrgent.append([tidx, urgency, task])
        tidx += 1
    
    finalUrgency = vUrgent + urgent + nUrgent

    #find a routine that loops if it exists
    currHour = 0
    currMin = 0
    currRoutine = None
    loopSchedule = False
    for routine in dayRoutine:
        hour = routine["hour"]
        minute = routine["minute"]
        cHour, cMinute = forwardTime(hour, minute, routine["rtime"])
        if cHour < hour: #we must start the routine from here
            currHour = cHour
            currMin = cMinute
            currRoutine = routine["name"]
            loopSchedule = True

    #create daily schedule based on routine
    taskWorkload = []
    finalSchedule = [] #variable for displaying the final schedule
    if loopSchedule:
        finalSchedule.append(f"0:00 - {currRoutine}")

    for routine in dayRoutine: #determining where the free places are in the schedule
        hour = routine["hour"]
        minute = routine["minute"]
        if hour >= currHour and minute >= currMin: #check what free time lasts between
            freeMinutes = (hour - currHour) * 60 + (minute - currMin)
            #find the most urgent task
            if len(finalUrgency) > 0:
                task = finalUrgency[0][2]
                progressLeft = task["length"] - task["progress"]
                finalSchedule.append(f"{currHour}:{minDisplay(currMin)} - {task['name']}")
                if freeMinutes > progressLeft * 60:
                    fHour, fMin = forwardTime(currHour, currMin, freeMinutes - progressLeft * 60)
                    taskWorkload.append([finalUrgency[0][0], progressLeft])
                    finalSchedule.append(f"{fHour}:{minDisplay(fMin)} - Break")
                else:
                    taskWorkload.append([finalUrgency[0][0], freeMinutes / 60])
                
                finalUrgency.pop(0)
            else:
                finalSchedule.append(f"{currHour}:{minDisplay(currMin)} - Free Time")
            finalSchedule.append(f"{hour}:{minDisplay(minute)} - {routine['name']}")
            currHour, currMin = forwardTime(hour, minute, routine["rtime"])

    if not loopSchedule:
        finalSchedule.append(f"{currHour}:{minDisplay(currMin)} - Free Time")

    while True:
        #drawing the title screen and sidebars
        screen.fill(0)
        drawText("EZTime", titleFont, (10, 15), (255, 255, 255))
        drawText(f"Welcome back, {username}!", titleFont, (400, 15), (255, 255, 255))
        drawText("Here is your schedule for today!", titleFont, (400, 55), (255, 255, 255))

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

        #rendering all schedule items
        y = 95
        for t in finalSchedule:
            drawText(t, titleFont, (400, y), (255, 255, 255))
            y += 40

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
                    elif highlightedButton == 3: #marking completion
                        today = datetime.date.today().toordinal()
                        if userProfile["lastMarked"] != today:
                            userProfile["lastMarked"] = today
                            for tData in taskWorkload: #mark progress for every task
                                currentTasks[tData[0]]["progress"] += tData[1]

                            writeJsonFile("tasks.json", currentTasks)
                            writeJsonFile("userProfile.json", userProfile)
                            return

def taskScreen(): #add and remove things to your daily routine
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
                if selectedTask == tidx: #make the button look special and have specific task details
                    drawText(task["name"], titleFont, (400, displayY), (255, 0, 0))
                    drawText(f"Due Date: {task['year']}/{task['month']}/{task['day']}", bodyFont, (10, 300), (255, 255, 255))
                    drawText(f"Progress: {round(task['progress'] / task['length'])}%", bodyFont, (10, 330), (255, 255, 255))
                    drawText(f"Urgency: {urgencyMap[calculateUrgency(task)]}", bodyFont, (10, 360), (255, 255, 255))
                elif checkBounds(400, 1280, mousepos[0]) and checkBounds(displayY, displayY + 36, mousepos[1]):
                    hoverTask = tidx
                    drawText(task["name"], titleFont, (400, displayY), (255, 255, 0))
                else:
                    drawText(task["name"], titleFont, (400, displayY), (255, 255, 255))
                tidx += 1
                displayY += 50

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
                    elif highlightedButton == 5: #delete a task
                        currentTasks.pop(10 * (currentPage - 1) + selectedTask)
                        writeJsonFile("tasks.json", currentTasks)
                        return
                    #doing the part where button clicking works for the tasks
                    selectedTask = hoverTask

def routineScreen(): #give specifics about your day to day life
    global currentScreen
    currentPage = 1
    currentRoutine = readJsonFile("fixedSchedule.json")
    routinePages = tablePaging(currentRoutine, 10)
    pageCount = len(routinePages)
    selectedRoutine = -1
    weekMap = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    buttons = [
        buttonData("Back", titleFont, (10, 15), (100, 36)),
        buttonData("Forward", titleFont, (1100, 550), (150, 36)),
        buttonData("Back", titleFont, (400, 550), (100, 36)),
        buttonData("New", titleFont, (1100, 15), (80, 36)),
        buttonData("Delete Routine", titleFont, (10, 550), (250, 36))
    ]

    buttonHolderMap = {
        1: "main",
    }

    while True:
        screen.fill(0)
        drawText("This is your current routine!", titleFont, (400, 15), (255, 255, 255))
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

        #getting which routine button is currently being hovered over
        ridx = 0
        hoverRoutine = -1
        displayY = 55
        if pageCount > 0:
            for routine in routinePages[currentPage - 1]:
                if selectedRoutine == ridx: #make it look extra special and display routine data
                    drawText(routine["name"], titleFont, (400, displayY), (255, 0, 0))
                    drawText(f"Recurring: {routine['recurring']}", bodyFont, (10, 300), (255, 255, 255))
                    drawText(f"Starting time: {routine['hour']}:{routine['minute']}", bodyFont, (10, 330), (255, 255, 255))
                    fwdHour, fwdMinute = forwardTime(routine["hour"], routine["minute"], routine["rtime"])
                    drawText(f"Ending time: {fwdHour}:{fwdMinute}", bodyFont, (10, 360), (255, 255, 255))

                    recurData = routine["recurData"]
                    if routine["recurring"] == "weeks": #draw all the days where this event occurs
                        drawText(f"Active Days: ", bodyFont, (10, 390), (255, 255, 255))
                        height = 390
                        for day  in recurData:
                            height += 30
                            drawText(weekMap[day - 1], bodyFont, (10, height), (255, 255, 255))
                    elif routine['recurring'] == "months": #draw start to end day
                        drawText(f"Starting day: {recurData[0]}", bodyFont, (10, 390), (255, 255, 255))
                        drawText(f"Ending day: {recurData[0] + recurData[1]}", bodyFont, (10, 420), (255, 255, 255))
                    elif routine["recurring"] == "years":
                        eventDate = datetime.date(2022, recurData[0], recurData[1])
                        endDate = datetime.date.fromordinal(eventDate.toordinal() + recurData[2])
                        drawText(f"Starting date: {eventDate.year}/{eventDate.month}/{eventDate.day}", bodyFont, (10, 390), (255, 255, 255))
                        drawText(f"Ending Date: {endDate.year}/{endDate.month}/{endDate.day}", bodyFont, (10, 420), (255, 255, 255))
                        
                    
                elif checkBounds(400, 1280, mousepos[0]) and checkBounds(displayY, displayY + 36, mousepos[1]):
                    hoverRoutine = ridx
                    drawText(routine["name"], titleFont, (400, displayY), (255, 255, 0))
                else:
                    drawText(routine["name"], titleFont, (400, displayY), (255, 255, 255))
                ridx += 1
                displayY += 50

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: #return back to the main screen once things have been entered
                    currentScreen = "main"
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if highlightedButton in buttonHolderMap:
                        currentScreen = buttonHolderMap[highlightedButton]
                        return
                    elif highlightedButton == 4: #create a new routine item
                        windowTitle = "EZTime Routine Recorder"
                        name = simpledialog.askstring(title = windowTitle, prompt = "What is this routine?")
                        recurring = simpledialog.askstring(title = windowTitle, prompt = "What does this recur over? (Days, Weeks, Months, Years)").lower()
                        timestart = simpledialog.askstring(title = windowTitle, prompt = "What time does this event start at?")
                        rtime = simpledialog.askinteger(title = windowTitle, prompt = "How long does this last for (in minutes)")

                        try:
                            #getting extra recurring data based on the recurring time
                            recurData = []
                            if recurring == "years":
                                month = simpledialog.askinteger(title = windowTitle, prompt = "What month does this event take place on?")
                                day = simpledialog.askinteger(title = windowTitle, prompt = "What day does this event start on?")
                                length = simpledialog.askinteger(title = windowTitle, prompt = "How many days does this event last for?")
                                datetime.date(2022, month, day)
                                if length > 365:
                                    raise Exception("why did you set it to be all year ya doofus")
                                recurData = [month, day, length]
                            elif recurring == "months":
                                day = simpledialog.askinteger(title = windowTitle, prompt = "What day does this event start on?")
                                length = simpledialog.askinteger(title = windowTitle, prompt = "How many days does this event last for?")
                                if length > 28:
                                    raise Exception("month gap")
                                recurData = [day, length]
                            elif recurring == "weeks":
                                days = simpledialog.askstring(title = windowTitle, prompt = "What days does this event occur over (1 = Monday, 2 = Tuesday ... 7 = Sunday) (SEPARATE NUMBERS WITH COMMAS)")
                                dayTable = {}
                                for day in days.split(","):
                                    day = int(day)
                                    if day < 1 or day > 7:
                                        raise Exception("that's not a valid day lol")
                                    dayTable[day] = True
                                
                                for i in range(7):
                                    if i + 1 in dayTable:
                                        recurData.append(i + 1)

                            hour, minute = parseTime(timestart)

                            currentRoutine.append({
                                "name": name,
                                "recurring": recurring,
                                "hour": hour,
                                "minute": minute,
                                "rtime": rtime,
                                "recurData": recurData
                            })

                            writeJsonFile("fixedSchedule.json", currentRoutine)
                            return
                        except:
                            simpledialog.askstring("Invalid input given.")
                    elif highlightedButton == 3: #turn the pages back
                        currentPage = max(currentPage - 1, 1)
                    elif highlightedButton == 2: #turn the pages forward
                        currentPage = min(currentPage + 1, pageCount)
                    elif highlightedButton == 5: #delete a task
                        currentRoutine.pop(10 * (currentPage - 1) + selectedRoutine)
                        writeJsonFile("fixedSchedule.json", currentRoutine)
                        return
                    selectedRoutine = hoverRoutine
#initializing the 2d display engine
screenHolder = {
    "main": mainScreen,
    "tasks": taskScreen,
    "routine": routineScreen
}

#constant application runtime task
while True:
    screenHolder[currentScreen]()