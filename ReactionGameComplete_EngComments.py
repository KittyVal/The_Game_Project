# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 10:44:33 2025

@author: [Redacted]
"""

#Importing the neccessary Libraries
import random
import time
import statistics
import sys
import threading
#Setting up the Ports
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

#Creating a List for easier Understanding of the Code
blaul=0
rotl=1
blaur=2
rotr=3
tasterl=4
tasterr=5

Reaktion=[4,18,23,24,16,20]

#Defining the Ports as In/Output
GPIO.setup(Reaktion[blaul],GPIO.OUT,initial=False)
GPIO.setup(Reaktion[rotl],GPIO.OUT,initial=False)
GPIO.setup(Reaktion[blaur],GPIO.OUT,initial=False)
GPIO.setup(Reaktion[rotr],GPIO.OUT,initial=False)
GPIO.setup(Reaktion[tasterl],GPIO.IN)
GPIO.setup(Reaktion[tasterr],GPIO.IN)

#Assigning the neccessary Variables
streak=0
troll=int(input("0/1"))
if troll != 1:
    troll=0
difficulty=1
reacttime=30

#creating Lists
timelist=[]
highscore=[0]
hardcorehs=[0]
#Spinning Cursor Icon for "Pausing time"
class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1: 
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False

#Subroutine "success", for randomized success messages
def success():
    messages=["Glückwunsch!", "Toll Gemacht!", "Bravo!", "Weiter so!", "Juhu!"]
    print(messages[random.randint(0,len(messages)-1)])

#Subroutine "Game Over", used for calculating the Highscore
def game_over():
    with Spinner():
        GPIO.output(Reaktion[blaul],False)
        GPIO.output(Reaktion[blaur],False)
        GPIO.output(Reaktion[rotl],False)
        GPIO.output(Reaktion[rotr],False)
        global streak
        global timelist
        global difficulty
        global hardcorehs
    print("Sie haben verloren!", f"Ihr Streak: {streak}", f"Ihre Durchschnittszeit: {statistics.median(timelist): .4f}", f"Highscore: {max(highscore)}", sep="\n")
    if difficulty==10:
        hardcorehs.append(streak)
        print(f"Der Hardcore-Highstreak liegt bei: {max(hardcorehs)}")
    o=4
    print("Bitte Warten...")
    with Spinner():
        for o in range(o,0,-1):
            GPIO.output(Reaktion[rotl],True)
            GPIO.output(Reaktion[rotr],True)
            time.sleep(0.2)
            GPIO.output(Reaktion[rotl],False)
            GPIO.output(Reaktion[rotr],False)
            time.sleep(0.2)
            o=o-1
        GPIO.output(Reaktion[blaul],True)
        GPIO.output(Reaktion[rotr],True)
        time.sleep(0.5)
        GPIO.output(Reaktion[blaul],False)
        GPIO.output(Reaktion[rotr],False)
        GPIO.output(Reaktion[blaur],True)
        GPIO.output(Reaktion[rotl],True)
        time.sleep(0.5)
        GPIO.output(Reaktion[blaul],False)
        GPIO.output(Reaktion[blaur],False)
        GPIO.output(Reaktion[rotl],False)
        GPIO.output(Reaktion[rotr],False)
    timelist=[]    
    streak=0
    print("----------------")
    Main()

#Subroutine "Stopwatch", used for measuring the time between LED light-up and button press
def start_stopwatch():
    global difficulty
    global reacttime
    ts=reacttime/difficulty
    if difficulty==10:
        ts=1
    start_time=time.time()
    while True:
        if GPIO.input(Reaktion[tasterl]) == GPIO.LOW:
            end_time=time.time()
            elapsed_time=end_time-start_time
            timelist.append(elapsed_time)
            statistics.median(timelist)
            if difficulty != 10:
                reacttime = reacttime - (random.randint(0,difficulty)/10)
            break
        elif GPIO.input(Reaktion[tasterr]) == GPIO.LOW:
            end_time=time.time()
            elapsed_time=end_time-start_time
            timelist.append(elapsed_time)
            statistics.median(timelist)
            if difficulty != 10:
                reacttime = reacttime - (random.randint(0, difficulty)/10)
            break
        ts=ts-0.01
        #Section "Time Up!", to set a time limit both for difficulty and resource management
        if ts<=0:
            end_time=time.time()
            elapsed_time=end_time-start_time
            timelist.append(elapsed_time)
            statistics.median(timelist)
            game_over()
            break
        time.sleep(0.01)
        
#Subroutine "Left Side", part of the Main code. This gets activated parallel to the "Stopwatch"-Program and the lightup of either "blaul" or "rotr"
def ls():
    global streak
    global troll
    while True:
        if GPIO.input(Reaktion[tasterl])==GPIO.LOW:
            GPIO.output(Reaktion[blaul],False)
            GPIO.output(Reaktion[rotr],False)
            if troll==1:
                success()
            else:
                pass
            break
        elif GPIO.input(Reaktion[tasterr])==GPIO.LOW:
            highscore.append(streak)
            game_over()

#Subroutine "Right Side", part of the Main code. This gets activated parallel to the "Stopwatch"-Program and the lightup of either "blaur" or "rotl"
def rs():
    global streak
    global troll
    while True:
        if GPIO.input(Reaktion[tasterr])==GPIO.LOW:
            GPIO.output(Reaktion[blaur],False)
            GPIO.output(Reaktion[rotl],False)
            if troll==1:
               success()
            else:
                pass
            break
        elif GPIO.input(Reaktion[tasterl])==GPIO.LOW:
            highscore.append(streak)
            game_over()
#Annotation to the subprograms ls() and rs(): They will never run simultaneously as they will oppose each other

#Main Program "Main", Core of the game. This part of the script is responsible for the randomized selection of the LEDs, as well as starting the subprograms ls(), rs() and start_stopwatch()
def Main():
    try:
        while True:
            global difficulty
            #Explaination of the Rules
            print("Regeln:", "Bei aufleuchten der blauen LEDs muss der Korrespondierende Taster gedrückt werden, bei roten LEDs der gegenteilige", "Wird der falsche Taster gedrückt, heißt es 'Game over!'", sep="\n")
            print()
            with Spinner():
                time.sleep(1)
            print("Beispiel:", "linke Blaue LED -> Linker Taster", "Rechte rote LED -> ebenfalls linker Taster", sep="\n" )
            print()
            with Spinner():
                time.sleep(1)
            i=5
            print("Press Enter to Start the Game")
            input()
            difficulty=int(input("Wählen Sie eine Schwierigkeitsstufe von 1 (Kinderspiel) bis 10 (fast unmöglich):", sep="\n"))
            if difficulty<1 or difficulty>10:
                print("Eingabe liegt außerhalb des festgelegten Bereiches!")
                game_over()
                break
            print("Spiel gestartet!", f"Der Highscore liegt bei: {max(highscore)}", sep="\n")
            if difficulty==10:
                print("Hardcore Mode!", "Viel Erfolg...", sep="\n")
                print(f"\t Der Hardcore-Highscore liegt momentan bei: {max(hardcorehs)}")
                with Spinner():
                    time.sleep(3)
            time.sleep(1)
            random.seed()
            while True:
                e=random.randint(1,4)
                if e==1:
                    GPIO.output(Reaktion[blaul],True)
                    start_stopwatch()
                    ls()
                elif e==2:
                    GPIO.output(Reaktion[rotl],True)
                    start_stopwatch()
                    rs()
                elif e==3:
                    GPIO.output(Reaktion[blaur],True)
                    start_stopwatch()
                    rs()
                elif e==4:
                    GPIO.output(Reaktion[rotr],True)
                    start_stopwatch()
                    ls()
                global streak
                streak=streak+1
                if difficulty==10:
                    time.sleep(0.7)
                else:
                    time.sleep(i)
                    i=i-(random.random()/10)
                    if i<=1:
                        i=1
    except KeyboardInterrupt:
        GPIO.cleanup()
        exit()

#Starting the Main code
Main()