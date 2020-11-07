
import pynput 
import time
import random
from pynput.keyboard import Key, Listener, Controller
import threading
import cv2
import mss
import numpy
import ctypes
#importing necessary libraries

class Shiny_Controller: # class to manage input from Keyboard
    def __init__(self):
        self.direction = random.choice([1,-1]) # Choose to Positive Direction


        #Sets Flags to be adjusted by Listner and Watcher threads
        self.found_shiny = 0 
        self.in_battle = 0
        self.encounter_start = 0
        self.exit = 0

        #gets screen size from ctypes user32
        self.user32 = ctypes.windll.user32
        self.screensize = self.user32.GetSystemMetrics(0), self.user32.GetSystemMetrics(1)

        #imports the health image
        self.health_img = cv2.imread('temtem_healthbar.png',0)
        self.w_h, self.h_h = self.health_img.shape[::-1]

        #imports the luma image
        self.luma_img = cv2.imread('luma_data.png',0)
        self.w_l, self.h_l = self.luma_img.shape[::-1]

        #imports the luma image
        self.temtem_minimap = cv2.imread('temtem_minimap.png',0)
        self.w_m, self.h_m = self.temtem_minimap.shape[::-1]
    
    def watching(self): #threading function to watch screen
        with mss.mss() as sct:
            # monitor chooses what part of the screen to capture

            #Your Temtem
            #self.monitor = {'top': self.user32.GetSystemMetrics(1)//6 *3, 'left': self.user32.GetSystemMetrics(0)//16 * 0 , 'width': self.user32.GetSystemMetrics(0)//16 * 9, 'height': self.user32.GetSystemMetrics(1)//6 * 3}

            #Wid Temtem
            self.monitor = {'top': 0, 'left': self.user32.GetSystemMetrics(0)//16*9  , 'width': self.user32.GetSystemMetrics(0)//16*7, 'height': self.user32.GetSystemMetrics(1)//6 * 2}

            #Full Screen
            #self.monitor = {'top': 0, 'left': 0, 'width': self.user32.GetSystemMetrics(0), 'height': self.user32.GetSystemMetrics(1)}


            while True:# runs loop to detect screen changes

                        #gets time of loop to determine FPS
                        self.last_time = time.time()

                        # Get raw pixels from the screen, save it to a Numpy array
                        self.sct_img = sct.grab(self.monitor)
                        self.img = numpy.array(self.sct_img)

                        #converts screen img to GrayScale
                        self.img_g = cv2.cvtColor(self.img, cv2.COLOR_BGRA2GRAY)

                        #checks if minimap img appears on screen
                        self.res_m = cv2.matchTemplate(self.img_g,self.temtem_minimap,cv2.TM_CCOEFF_NORMED)

                        #threshold value for minimum threshold of img is a minimap
                        self.threshold_m = 0.9

                        #determines which locacation are minimap from threshold
                        self.loc_m = numpy.where( self.res_m >= self.threshold_m)

                        self.encounter_counter = 0

                        #loops through all location of minimap symbol
                        for pt in zip(*self.loc_m[::-1]):

                            #draws rectangle on minimap symbol
                            cv2.rectangle(self.img, pt, (pt[0] + self.w_m, pt[1] + self.h_m), (0,0,255), 2)

                            #counts how many times minmap symbol detected
                            self.encounter_counter += 1
                        
                        #sets flag to be in encounter or not
                        if self.encounter_counter >= 1: 
                            self.in_battle = 0
                        else:
                            self.in_battle = 1


                        if self.in_battle == 1:
                            #checks if luma img appears on screen
                            self.res = cv2.matchTemplate(self.img_g,self.luma_img,cv2.TM_CCOEFF_NORMED)

                            #threshold value for minimum threshold of img is a luma
                            self.threshold = 0.9

                            #determines which locacation are lumas from threshold
                            self.loc = numpy.where( self.res >= self.threshold)

                            #loops through all location of luma symbol
                            for pt in zip(*self.loc[::-1]):

                                #draws rectangle on luma symbol
                                cv2.rectangle(self.img, pt, (pt[0] + self.w_l, pt[1] + self.h_l), (0,0,255), 2)

                                #sets flag that shiny has been found
                                self.found_shiny = 1
                            


                    
                            #checks if health img appears on screen
                            self.res_h = cv2.matchTemplate(self.img_g,self.health_img,cv2.TM_CCOEFF_NORMED)

                            #threshold value for minimum threshold of img is a health
                            self.threshold_h = 0.9

                            #determines which locacation are health from threshold
                            self.loc_h = numpy.where( self.res_h >= self.threshold_h)

                            #loops through all location of health symbol
                            for pt in zip(*self.loc_h[::-1]):

                                #draws rectangle on health symbol
                                cv2.rectangle(self.img, pt, (pt[0] + self.w_h, pt[1] + self.h_h), (0,0,255), 2)

                                #sets flag that in battle
                                self.encounter_start = 1


                        # Display the picture
                        cv2.imshow('OpenCV/Numpy normal', self.img)

                        #print('fps: {0}'.format(1 / (time.time()-last_time)))

                        # If program is exiting destroy windows
                        if (cv2.waitKey(25) & 0xFF == ord('q')) or self.exit == 1:
                            cv2.destroyAllWindows()
                            break

    def on_press (self,key): #gets input of keys pressed
        k = str(key).replace("'","") #remove tick marks from string
        if k == Key.esc: # detect key to stop the program
            self.exit = 1
            print("manual overide program killed")
    def on_release(self,key): #gets input of keys released
        if key == Key.esc: # detect key to stop the program
            self.exit = 1

def Reactable_Sleep(): # Creates a Pause so actions happen within human reaction time and not instantly
    time.sleep(random.random() * 0.4+0.2) 


def key_to_index(key): #converts key to its index value
    switcher = { #dictionary of keys to their index
        'w': 0,
        'a': 1,
        's': 2,
        'd': 3,
    }
    return switcher.get(key,-1) # return correposnding index from key

def index_to_key(key): #converts index to its key value
    switcher = { #dictionary of indexes to their key
        0: 'w',
        1: 'a',
        2: 's',
        3: 'd',
    }
    return switcher.get(key,-1) # return correposnding key from index

def key_to_distance(key): # return the unit vector of each key
    switcher = { 
        # first value of tuple determines wether its positive or negative value second value determines wether its on x or y-axis
        # 1 for y-axis 0 for x-axis
        'w': [1,   1], 
        'a': [-1,   0],
        's': [-1,  1],
        'd': [1,    0],
    }
    return switcher.get(key,0)

def dice_roll(max,min): # generates random value in between a max and a min with similair probability spread as a double dice roll
    value = (max -min) / 2
    random_num = (random.random() * value) + (random.random() * value) + min
    return random_num

def getNumber(question,lowest,highest): # defines function which asks a question and get a number within a range
    num_true = False # sets num true to False
    while num_true == False: # runs while num true to False
        numbersz = input(question)# gets the number input from user
        if numbersz.isdigit() == True: # checks if input was a number
            numbersz = int(numbersz) #converts numbersz to an integer
            if numbersz > highest or numbersz < lowest: # checks if numbersz is within the range
                print('please input a number between ' + str(lowest) + ' and ' + str(highest)) #shows to user the highest and lowest value
            else: #runs if number is accpetable
                num_true = True # ends the loop by changing variable
        else: # runs if user did not input a number
            print('please input a number') # tells user to input a number
    return numbersz #returns value of numbers

def getOptionNumExit(question,array_of_options): # Asks a Question and gets The answer from list with vertical numbered menus and has exit button
    print(question)
    length_list = len(array_of_options) + 1 # gets the length of list and adds 1
    for list_number in range (1,length_list): # runs for length of array but every number the counter is increased by 1
        array_number = list_number - 1 # decrease list number by 1
        print(str(list_number) + ' - ' + array_of_options[array_number]) # prints the number with a corresponding number readable to user
    print(str(length_list) + ' - Exit') # prints out the button for the user to press exit
    item_use = getNumber('Enter: ',1,length_list) # gets the number that the user wants
    if item_use == length_list: #runs if user did not input exit
        item_use = None # gets appropriate answer and stores it
    else:
        item_use -= 1
    return item_use

control = Shiny_Controller() #creates class to control input
keyboard = Controller() # creates class to manipulate the keyboard

listener = pynput.keyboard.Listener(on_press = control.on_press, on_release = control.on_release) #create instance on listner to monitor keyboard
listener.start() # starts thread of listner

watcher = threading.Thread(target=control.watching,daemon=True) # create instance of watcher to monitor the screen for symbols
watcher.start() #starts thread of watcher

position_map = [0,0] #stores the trainers position on the x y  axis
pressed_keys = [0,0,0,0] # stores wether the keys w,a,s,d are pressed  0 for off 1 for on
pillars = ['w','a','s','d'] # used to keep track of which quadrant of the circle trainer is currently in

primary_key = pillars[1] # gets the primary key to get to the next quadrant
secondary_key = pillars[2] # gets the secondary key to get to the next quadrant

unit_vector_p = key_to_distance(primary_key) # finds unit vector of primary key
unit_vector_s = key_to_distance(secondary_key) # finds unit vector of secondary key

#Determine max and min random values for microbreak time
mb_t_max = 2 # 2 seconds
mb_t_min = 0.5 # 0.5 seconds

#Determine max and min random values for microbreak counter
mb_c_max = 120 # 2 minutes
mb_c_min = 45 # 45 seconds

#Determine max and min random values for shortbreak time
sb_t_max = 300 # 5 minutes
sb_t_min = 67 # 1 minute 7 seconds

#Determine max and min random values for shortbreak counter
sb_c_max = 4500 # 1 hour 15 minutes
sb_c_min = 1800 # 30 minutes

#Determine max and min random values for longbreak timer
lb_t_max = 2400 #40 minutes
lb_t_min = 1500 #25 minutes

#Determine max and min random values for longbreak countdown
lb_c_max = 18000 #5 hours
lb_c_min = 10800 # 3 hours

#Determine max and min random values for termination countdown
t_c_max = 21600 # 6 hours
t_c_min = 28800 # 8 hours

program_length = 0

# gets random value for timers and countdowns from max and mins through dice roll
#Countdown counts down while game is playing until it hits zero
# Then the input to the game is paused for the duration of the correponding time
Microbreak_time = dice_roll(mb_t_max,mb_t_min)
Microbreak_Countdown = dice_roll(mb_c_max,mb_c_min)

Shortbreak_time = dice_roll(sb_t_max,sb_t_min)
Shortbreak_Countdown = dice_roll(sb_c_max,sb_c_min)

Longbreak_time = dice_roll(lb_t_max,lb_t_min)
Longbreak_Countdown = dice_roll(lb_c_max,lb_c_min)

Termination_time = dice_roll(t_c_max,t_c_min)

#Store the time for Termination
Termination_Countdown = Termination_time








# store Default Max and min Values
max_pillar = 0.3
min_pillar = 0.1

max_walk_length = 0.45
min_walk_length = 0.1

key_duration_max = 0.05
key_duration_min = 0

#Generate random values for variables
key_release = dice_roll(key_duration_max,key_duration_min)
key_press = dice_roll(key_duration_max,key_duration_min)
walk_length = dice_roll(max_walk_length,min_walk_length)


#Generate Random Pillar lengths
pillarA = dice_roll(max_pillar,min_pillar)
pillarB = dice_roll(max_pillar,min_pillar)

#Determine the minimum length of Straight1
if (pillarB - pillarA) <= 0:
    straight1_min = 0
else:
    straight1_min = pillarB - pillarA

straight1 = dice_roll(pillarB,straight1_min) #Determine random value for straight1



#diagonal = (pillarB - straight1) * 1.41421356237 #Determine value for diagonal based on 
#straight2 = pillarA - (diagonal * 0.70710678118)

move_pattern = "straight1" #set current movement pattern to straight1

##################################################################################################################
print("Make Sure you are running Temtem on Primary Monitor in Full Screen") #
menu_question = "Which Pattern Would You like to run in"
array_of_running = ["Vertical","Horizontal","Circle"]
menu_option = getOptionNumExit(menu_question,array_of_running)

if menu_option == 0:
    pathing_option = 0
    positive_key = 'w'
    negative_key = 's'
    axis_dir = 1
    tile_msg = "Choose walk length in tiles: "


elif menu_option == 1:
    pathing_option = 0
    positive_key = 'd'
    negative_key = 'a'
    axis_dir = 0
    tile_msg = "Choose walk length in tiles: "
else:
    pathing_option = menu_option
    tile_msg = "Choose radius of circle in tiles: "

max_walk_length = 0.45
min_walk_length = 0.1

max_pillar = 0.3
min_pillar = 0.1

tile_choice = ""
tile_flag = False
while tile_flag == False:
    tile_choice = input(tile_msg)
    if tile_choice.isnumeric():
        if float(tile_choice) >= 0:
            tile_flag = True
            max_pillar = float(tile_choice) * 0.15
            max_walk_length = float(tile_choice) * 0.15
        else:
            print("Please enter a number greater than 0 ex: 2")

    else:
        print("Please enter a number greater than 0 ex: 2")


print("Program will start running in 5 sec, Press Esc to terminate program")
time.sleep(5)



# reset the timers
primary_time = time.time() 
secondary_time = time.time()
countdown_time = time.time()
################################################################################################################################



while control.exit == 0 and control.found_shiny == 0: # Main program loop
    # reduces the counters by the time that has passed
    Microbreak_Countdown -= (time.time()- countdown_time )
    Shortbreak_Countdown -=(time.time()- countdown_time )
    Longbreak_Countdown -= (time.time()- countdown_time )
    Termination_Countdown -= (time.time()- countdown_time )
    program_length += (time.time()- countdown_time )
    countdown_time = time.time()

    if Termination_Countdown <= 0: # checks if time has passed to terminate program and close Temtem
        
        print("program terminated Temtem after " +   str(Termination_time // 3600)  +"hrs " + str((Termination_time - ((Termination_time // 3600)* 3600))//60) + "mins ") 

        # releases movement keys
        for n in range (len(pressed_keys)): 
            if pressed_keys[n] == 1:
                pressed_keys[n] = 0
                keyboard.release(index_to_key(n))

        Reactable_Sleep()
        keyboard.press(Key.tab) # press tab to go to Menu
        Reactable_Sleep()
        keyboard.release(Key.tab)
        Reactable_Sleep()
        keyboard.press('a') # Press a to navigate to Options
        Reactable_Sleep()
        keyboard.release('a')
        Reactable_Sleep()
        keyboard.press('w') # Press w to navigate to Quit Game
        time.sleep(random.random() * 0.2+0.1) 
        keyboard.release('w')
        Reactable_Sleep()
        keyboard.press('f') # press f to quite game
        Reactable_Sleep()
        keyboard.release('f')
        Reactable_Sleep()
        keyboard.press('f') # press f to confirm quit game
        Reactable_Sleep()
        keyboard.release('f')
        control.exit = 1 # stop program from running

    elif Longbreak_Countdown <= 0: #check if longbreak should occur

        # releases movement keys
        for n in range (len(pressed_keys)):
            if pressed_keys[n] == 1:
                pressed_keys[n] = 0
                keyboard.release(index_to_key(n))

        print("program taken a long break: " +   str(program_length // 3600)  +"hrs " + str((program_length - ((program_length // 3600)* 3600))//60) + "mins ")
        time.sleep(Longbreak_time) # stop program running for long break

        #resets the break time counter and smaller break times
        Microbreak_time = dice_roll(mb_t_max,mb_t_min)
        Microbreak_Countdown = dice_roll(mb_c_max,mb_c_min)

        Shortbreak_time = dice_roll(sb_t_max,sb_t_min)
        Shortbreak_Countdown = dice_roll(sb_c_max,sb_c_min)

        Longbreak_time = dice_roll(lb_t_max,lb_t_min)
        Longbreak_Countdown = dice_roll(lb_c_max,lb_c_min)

        #resets timer
        primary_time = time.time()
        secondary_time = time.time()

    elif Shortbreak_Countdown <= 0: #check if short break should occur

        # releases movement keys
        for n in range (len(pressed_keys)):
            if pressed_keys[n] == 1:
                pressed_keys[n] = 0
                keyboard.release(index_to_key(n))

        print("program taken a short break: " +   str(program_length // 3600)  +"hrs " + str((program_length - ((program_length // 3600)* 3600))//60) + "mins ")
        time.sleep(Shortbreak_time) # stop program running for short break

        #resets the break time counter and smaller break times
        Microbreak_time = dice_roll(mb_t_max,mb_t_min)
        Microbreak_Countdown = dice_roll(mb_c_max,mb_c_min)

        Shortbreak_time = dice_roll(sb_t_max,sb_t_min)
        Shortbreak_Countdown = dice_roll(sb_c_max,sb_c_min)
        
        #resets timer
        primary_time = time.time()
        secondary_time = time.time()
    
    elif Microbreak_Countdown <= 0:  #check if micro break should occur

        # releases movement keys
        for n in range (len(pressed_keys)):
            if pressed_keys[n] == 1:
                pressed_keys[n] = 0
                keyboard.release(index_to_key(n))

        print("program taken a micro break: " +   str(program_length // 3600)  +"hrs " + str((program_length - ((program_length // 3600)* 3600))//60) + "mins ")
        time.sleep(Microbreak_time) # stop program running for micro break

        #resets the break time counter 
        Microbreak_time = dice_roll(mb_t_max,mb_t_min)
        Microbreak_Countdown = dice_roll(mb_c_max,mb_c_min)

        #resets timer
        primary_time = time.time()
        secondary_time = time.time()



    if pathing_option == 0:  #linear movement patter Horizontal or Vertical
        
        #If one key is pressed add its movement to the position map
        if sum(pressed_keys) == 1: 
            if control.direction == 1:
                position_map[axis_dir] +=  pressed_keys[key_to_index(positive_key)] * (time.time()-primary_time) #add positive direction if pressed
            elif control.direction == -1:
                position_map[axis_dir] +=  pressed_keys[key_to_index(negative_key)] * (time.time()-primary_time) * -1 #add negative direction if pressed

        primary_time = time.time() # reset timer

        if (position_map[axis_dir] >= walk_length) and control.direction == 1: #checks if travelled walk length when positive walking
            control.direction = -1 # switch to negative

            if random.random() > 0.7: # 30% chance to press negative key without releasing positive key

                keyboard.press(negative_key) # press negative
                pressed_keys[key_to_index(negative_key)] = 1 # store that negative is pressed
                primary_time = time.time() # reset timer

                key_release = dice_roll(key_duration_max,key_duration_min) # random interval of time until positive key is released

            else: #70% chance to release positive key

                key_press = dice_roll(key_duration_max,key_duration_min) # random interval of time until negative key is pressed

                keyboard.release(positive_key) # release positive key
                pressed_keys[key_to_index(positive_key)] = 0 # store that  positive key is released

            walk_length = dice_roll(max_walk_length,min_walk_length) # randomly determine walk length
            

        elif (position_map[axis_dir] <= walk_length * -1) and control.direction == -1: #checks if travelled walk length when negative walking
            control.direction = 1 # switch direction to positive

            if random.random() > 0.7: # 30% chance to press positive key without releasing negative key

                keyboard.press(positive_key) # press positive
                pressed_keys[key_to_index(positive_key)] = 1 # store that positive is pressed

                primary_time = time.time() # reset timer

                key_release = dice_roll(key_duration_max,key_duration_min)#determine random interval of time until negative key is released
            else: #70% chance to release negative key

                key_press = dice_roll(key_duration_max,key_duration_min) # determine random interval of time until positive is pressed
                keyboard.release(negative_key) # release negative key
                pressed_keys[key_to_index(negative_key)] = 0 # store that the negative key is released

            walk_length = dice_roll(max_walk_length,min_walk_length) # determine random walk length

        elif (sum(pressed_keys) > 1 ): # if more than 1 key is pressed
            key_release -= (time.time()-primary_time) # reduce key release timer
            if key_release <= 0: #if timer is done
                if control.direction == 1:
                    keyboard.release(negative_key) #release negative key if going positive
                    pressed_keys[key_to_index(negative_key)] = 0
                elif control.direction == -1:
                    keyboard.release(positive_key) #release positive key if going negative
                    pressed_keys[key_to_index(positive_key)] = 0

        elif sum(pressed_keys) == 0: # if no keys are being pressed
            key_press -= (time.time()-primary_time) #reduces key press time
            if key_press <= 0: # if timer is done
                if control.direction == 1:
                    keyboard.press(positive_key) # press positive key if going in positive direction
                    pressed_keys[key_to_index(positive_key)] = 1
                elif control.direction == -1:
                    keyboard.press(negative_key) # press negative key if going in negative direction
                    pressed_keys[key_to_index(negative_key)] = 1
                primary_time = time.time() # reset timer




    elif pathing_option == 2: # if pathing to go in circle

        if (sum(pressed_keys) > 1): # if pressing multiple direction slow down movment with diagonal factor
            diagonal_factor = 0.70710678118
        else:
            diagonal_factor = 1

        #add primary movement if key is pressed
        position_map[unit_vector_p[1]] +=  pressed_keys[key_to_index(primary_key)] * unit_vector_p[0] * (time.time()-primary_time) * diagonal_factor
        primary_time = time.time()  # reset timer

        #add secondary movement if key is pressed
        position_map[unit_vector_s[1]] +=  pressed_keys[key_to_index(secondary_key)] * unit_vector_s[0] * (time.time()-secondary_time) * diagonal_factor
        secondary_time = time.time() # reset timer


        if move_pattern == "straight1": # if movment is on straight 1
            if (abs(position_map[unit_vector_p[1]]) >= straight1): # checks if movment has passed straight 1

                keyboard.press(secondary_key) #press secondary key
                secondary_time = time.time() # reset timer

                #add primary movement
                position_map[unit_vector_p[1]] +=  pressed_keys[key_to_index(primary_key)] * unit_vector_p[0] * (time.time()-primary_time)
                primary_time = time.time() # reset timer
                
                pressed_keys[key_to_index(secondary_key)] = 1 # store key press
                move_pattern = "diagonal" # change movement pattern to diagonal

            elif pressed_keys[key_to_index(primary_key)]  == 0: # if primary key is not being pressed press it
                keyboard.press(primary_key) 
                pressed_keys[key_to_index(primary_key)] = 1 # store key press
                primary_time = time.time() # reset timer

        
        elif move_pattern == "diagonal": # if movment is on diagonal
            if (abs(position_map[unit_vector_p[1]]) >= pillarB):  #check if movment passed diagonal threshold

                #add primary movement
                position_map[unit_vector_p[1]] +=  pressed_keys[key_to_index(primary_key)] * unit_vector_p[0] * (time.time()-primary_time)
                keyboard.release(primary_key) # release primary key

                #add secondary movement
                position_map[unit_vector_s[1]] +=  pressed_keys[key_to_index(secondary_key)] * unit_vector_s[0] * (time.time()-secondary_time) * 0.70710678118
                secondary_time = time.time() #reset timer

                pressed_keys[key_to_index(primary_key)] = 0 #store primary key released
                move_pattern = "straight2" #change movment pattern to straight 2

            elif pressed_keys[key_to_index(primary_key)]  == 0: # if primary key is not pressed than press it

                keyboard.press(primary_key) #press primary key and then store it
                pressed_keys[key_to_index(primary_key)] = 1

                primary_time = time.time() # reset timer

            elif pressed_keys[key_to_index(secondary_key)]  == 0: # if secondary key is not pressed than press it

                keyboard.press(secondary_key)  #press secondary key and store it
                pressed_keys[key_to_index(secondary_key)] = 1

                secondary_time = time.time() # reset timer
        
        elif move_pattern == "straight2":# if movement pattern is straight 2
            if (position_map[unit_vector_s[1]] >= 0 and unit_vector_s[0] >= 0) or (position_map[unit_vector_s[1]] <= 0 and unit_vector_s[0] <= 0): # if passed straight 2 threshold
                move_pattern = "straight1" # change movement pattern to striaght 1
                pillarA = pillarB # set pillar A to old pillar B
                pillarB = dice_roll(max_pillar,min_pillar) # find new pillar B
                if (pillarB - pillarA) <= 0: #calculate staright 1 min
                    straight1_min = 0
                else:
                    straight1_min = pillarB - pillarA
                    # get new stright 1
                straight1 = dice_roll(pillarB,straight1_min)

                #diagonal = (pillarB - straight1) * 1.41421356237
                #straight2 = pillarA - (diagonal * 0.70710678118)

                pillars.append(pillars.pop(0))# pop out the first elemnt of pillars and add it to the end

                # get new primary and secondary key from pillars
                primary_key = pillars[1]
                secondary_key = pillars[2]

                #get unit vectors for primar and secondary key
                unit_vector_p = key_to_distance(primary_key)
                unit_vector_s = key_to_distance(secondary_key)

            elif pressed_keys[key_to_index(secondary_key)]  == 0:# if secondary key is not pressed
                keyboard.press(secondary_key) # press secondary key and store it
                pressed_keys[key_to_index(secondary_key)] = 1
                secondary_time = time.time() # reset timer
    
    
    if control.exit == 1:
        print("program manually exited") #checks if exit has been called
    elif control.in_battle == 1: # checks if battle has started
        #print("initiate battle")
        run_f_battle = 0 # flag is user has run from battle
        control.encounter_start  = 0 # flag is temtem have shown up on screen
        for n in range (len(pressed_keys)): # release presssed keys
            if pressed_keys[n] == 1:
                pressed_keys[n] = 0
                keyboard.release(index_to_key(n))

        while control.in_battle == 1 and control.exit == 0 and control.found_shiny == 0: #loops while in battle

            primary_time = time.time() # resets timer
            secondary_time = time.time() 
            if control.encounter_start == 1 and run_f_battle == 0: # runs when temtem are seen and not run from battle
                Reactable_Sleep() # wait before pressing buttons
                if control.exit == 1:
                    print("program manually exited") # exit if manual overide
                elif control.found_shiny == 1:
                    print("shiny found program will stop") # exit if shiny detected
                else:
                    #press 8 twice to run from battle
                    keyboard.press('8')
                    Reactable_Sleep()
                    keyboard.release('8')
                    Reactable_Sleep()
                    keyboard.press('8')
                    Reactable_Sleep()
                    keyboard.release('8')

                    run_f_battle = 1 # flag that has aldready run away
                    #print("fled from battle")

                    #reset timers
                    primary_time = time.time()
                    secondary_time = time.time()

#release all keys
for n in range (len(pressed_keys)):
    if pressed_keys[n] == 1:
        pressed_keys[n] = 0
        keyboard.release(index_to_key(n))