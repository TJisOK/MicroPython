from machine import Pin, I2C, PWM
from ssd1306 import SSD1306_I2C
from button_functions import Button

import time
import framebuf
import random

'''Hardware init'''
# 6 buttons
sw_a = Button(16,5, 400)
sw_b = Button(17,5, 400)

sw_left = Button(21,5, 400)
sw_up = Button(20,5, 400)
sw_right = Button(19,5, 400)
sw_down = Button(18,5, 400)

# i2c config from machine module
i2c = I2C(0, scl=Pin(13), sda=Pin(12), freq=400000)

# display object from ssd1306 module
display = SSD1306_I2C(128, 64, i2c)
display.poweron()

# Buzzer
buzzer = PWM(Pin(28))
play_buzz = False 
which_sound = 0
time_stored = 0

# sound feedback ctrl
sound_sw_ab = False
sound_sw_dir = False
sound_eat = False
sw_sound_move = False
sound_false = False
sound_dead = False 

# when pressed: 0
sw_left_value = 1
sw_up_value = 1
sw_right_value = 1
sw_down_value = 1

# timmer for drawing snake
last_frame_time = 0
game_speed_index = 100 #100 -> 1
game_speed_bar_low = 100
game_speed_bar_high = 100

# food init
food_x = random.randint(1,31)
food_y = random.randint(1,15)

# list of tuples as the body of sake
snake = [(16, 8), (15, 8), (14, 8)]  #snake[3]: snake[0], snake[1]
direction = 'RIGHT'

# game factors
play_game_1 = False
you_are_dead = False
game_menu = 0
menu_index = 0
score = 0
# pointer_game_1 = '   '
# pointer_game_2 = '   '
# pointer_game_3 = '   '




''' about sound '''
def sound_feedback(freq, duty_in):
    buzzer.freq(freq)
    if duty_in == 0:
        buzzer.duty_u16(0)
    elif duty_in == 1:
        buzzer.duty_u16(32768)    
        
def sound_feedback_pack (select, trigger):
    if select == 0:
        sound_feedback(200, trigger)
    elif select == 1:
        sound_feedback(300, trigger)
    elif select == 2:
        sound_feedback(400, trigger)
    elif select == 3:
        sound_feedback(500, trigger)
    elif select == 4:
        sound_feedback(600, trigger)
    elif select == 5:
        sound_feedback(700, trigger)
    elif select == 6:
        sound_feedback(800, trigger)
        
    elif select == 7:
        sound_feedback(1500, trigger)
    elif select == 8:
        sound_feedback(2500, trigger)
    elif select == 9:
        sound_feedback(3500, trigger)

def sound_module(button_input, which, duration):
    global which_sound, play_buzz, time_stored
    
    time_now = time.ticks_ms()
    if button_input and not play_buzz:
        play_buzz = True
        time_stored = time_now
        which_sound = which
    
    if play_buzz and time.ticks_diff(time_now, time_stored) >= duration:
        time_stored = time_now
        play_buzz = False
        
    sound_feedback_pack(which_sound, play_buzz)
    

''' about Game play '''
def button_ctrl():
    global sw_left_value, sw_up_value, sw_right_value, sw_down_value, direction
    global sound_sw_ab, sound_sw_dir, sound_false # calim those are global, otherwise they will be local
    
#     raw value, un-debounced button value
    sw_left_value = sw_left.value()
    sw_up_value = sw_up.value()
    sw_right_value = sw_right.value()
    sw_down_value = sw_down.value()

    if  direction == 'LEFT' or  direction == 'RIGHT':
#         detecting up or down
        if sw_up.is_pressed():
            direction = 'UP'
            sound_sw_dir = True          
        elif sw_down.is_pressed():
            direction = 'DOWN'
            sound_sw_dir = True
        else:
            sound_sw_dir = False 
             
#         sound feeback: negative
        if sw_left.is_pressed() or sw_right.is_pressed():
            sound_false = True
        else:
            sound_false = False
            
        ''' good to learn elif'''         
    elif direction == 'UP' or direction == 'DOWN': # elif limit the detection has to be other thatn L or R
#         detecting left
        if sw_left.is_pressed():
            direction = 'LEFT'
            sound_sw_dir = True
        elif sw_right.is_pressed():
            direction = 'RIGHT'
            sound_sw_dir = True
        else :
            sound_sw_dir = False
        
#         sound feeback: negative            
        if sw_up.is_pressed() or sw_down.is_pressed():
            sound_false = True
        else:
            sound_false = False
            
    
def renew_food():
    global food_x,food_y
    food_x = random.randint(1,31)  # Re-generate food position
    food_y = random.randint(1,15)
    

def snake_control(direction, snake):
    global food_x, food_y
    global you_are_dead
    global sound_eat, sound_dead
    global game_speed_index, game_speed_bar_low,game_speed_bar_high, score
    
    head_x, head_y = snake[0] #get the 1st item in the array
    if direction == 'RIGHT':
        head_x += 1
    elif direction == 'LEFT':
        head_x -= 1
    elif direction == 'UP':
        head_y -= 1
    elif direction == 'DOWN':
        head_y += 1
        
    snake.insert(0, (head_x, head_y)) # constantly create a new snake[0] with manipulated headx,y
    
    if snake[0] == (food_x, food_y):
        renew_food()
#         sound
        sound_eat = True
        if game_speed_bar_low >= 10:
            game_speed_bar_low -= 10
            
        if game_speed_bar_high >= 2:
            game_speed_bar_high -= 2
            
        game_speed_index = random.randint( game_speed_bar_low, game_speed_bar_high)

    else:
        snake.pop()  # trim the last one in the list, when no food
#         sound
        sound_eat = False

#     detact if the head hit something
    if head_x <= -1 or head_x >= 32 or head_y <= -1 or head_y >= 16:
        you_are_dead = True
        sound_dead = True
        print('dead_1')
      
#     else: # useful when just dectectnig colision 
#         you_are_dead = False 
#         sound_dead = False
    snake_length = len(snake)
    for i in range(1, snake_length - 1): #last tuple of list is indexed list[n-1] 
        if snake[0] == snake[i]:
            you_are_dead = True 
            sound_dead = True
            print('dead_2')
            
    score = snake_length - 3
#         else :
#             sound_dead = False 
        
#         else:
#             you_are_dead = False
#             sound_dead = False
#             break  # Exit loop as collision is detected
#         
          
'''about Visual'''
def draw_snake(snake, color):
    for one_segment in snake: # for each snake[n], from snake[0] to snake[the last]
        x, y = one_segment  # 获取蛇身坐标
        a_new_pixel(x, y, color)  # 在屏幕上绘制每个蛇身部分

def food(x, y, r):
    x = 1+4*x
    y = 1+4*y 
    # Loop over the surrounding pixels
    for off_x_edge in range(-4, 5):   #  loop through -4 to 4
        if off_x_edge < -2 or off_x_edge > 2: # select range needed
            display.pixel(x + off_x_edge, y, r)
            
    for off_y_edge in range(-4, 5):   #  loop through -4 to 4
        if off_y_edge < -2 or off_y_edge > 2: # select range needed
            display.pixel(x, y + off_y_edge, r)

def a_pixel(x, y, r):
    for off_x in range(-1, 2):  
        for off_y in range(-1, 2):
            new_x = x + off_x
            new_y = y + off_y
            display.pixel(new_x, new_y, r)        
    
def a_new_pixel(x, y, r):
#   128//4 = 32
#   64//4 = 16
    x = 1+4*x
    y = 1+4*y
    a_pixel(x,y,r)
    
def snakeRate(eachframe_ms): # same as frame frame. but here is the interval defined
    global last_frame_time
    time_now = time.ticks_ms()
    if time.ticks_diff(time_now, last_frame_time) >= eachframe_ms:
        last_frame_time = time_now
        return True
    else:
        return False
def game_reset():
    global you_are_dead, food_x, food_y, snake, direction, game_speed_index
    global game_speed_bar_low, game_speed_bar_high
    you_are_dead = False
            # food init
    food_x = random.randint(1,31)
    food_y = random.randint(1,15)
    snake = [(16, 8), (15, 8), (14, 8)]  #snake[3]: snake[0], snake[1]
    direction = 'RIGHT'
    game_speed_index = 100
    game_speed_bar_low = 100
    game_speed_bar_high = 100



'''main'''
while True:
    
    if game_menu == 0:
        
#         button controll -> menu navigation
        if sw_up.is_pressed():
            menu_index -= 1
            sound_sw_dir = True
            
        elif  sw_down.is_pressed():
            menu_index += 1
            sound_sw_dir = True
            
        else:
            sound_sw_dir = False  
        
        if menu_index <0:
            menu_index = 2 #back to the last one
        if menu_index > 2:
            menu_index = 0 #back to the fisrt one

#         when a game has been selected
        if menu_index == 0:# Snake game
            if sw_a.is_pressed():
                game_menu = 1
                
        elif menu_index == 1:# Empaty game
            if sw_a.is_pressed():
                game_menu = 2
                
        elif menu_index == 2:# Empaty game
            if sw_a.is_pressed():
                game_menu = 3
                
#         Pointers Update
        pointer_game_1 = '<-' if menu_index == 0 else ' '
        pointer_game_2 = '<+' if menu_index == 1 else ' '
        pointer_game_3 = '<=' if menu_index == 2 else ' '
                
        print (menu_index)
        display.fill(0)
        display.text(f'1.SNAKE {pointer_game_1}',1,1,1)
        display.text(f'2.Game Slot {pointer_game_2}',1,10,1)
        display.text(f'3.Game Slot {pointer_game_3}',1,19,1)
        display.show()
        
#         sound feedbak
        sound_module(sound_sw_ab, 2, 10)
        sound_module(sound_sw_dir, 1, 10)
    if game_menu == 1:
#         mechanism to exit
        if sw_b.is_long_pressed():
            game_menu = 0
            game_reset()
            
        if not you_are_dead:
    #         data ctrl
            button_ctrl()
    #         visual module
            display.fill(0)
            display.text(f'{score}',1,55,1)
            food(food_x, food_y, 1)

            if snakeRate(game_speed_index):
                print(f'bar: {game_speed_bar_low}', f'bar: {game_speed_bar_high}', game_speed_index)
                snake_control(direction, snake)
            draw_snake(snake, 1)
                
            display.show()
            
        else:
            sound_dead = False
    #         invert display
            display.fill(1)
            draw_snake(snake, 0)
            display.text('YOU JUST DIED:p',1,1,0)
#             display.text('LOSER in 2024!',1,10,0)
            
            display.text('Press A: Again!',1,32,0)
            display.text('Hold B: Back',1,41,0)
            display.text(f'{score}',1,56,0)
            food(food_x, food_y, 0)
            
            display.show()
            if sw_a.is_pressed():
                game_reset()         
        
    #     print(you_are_dead)
    #         sound feedback module
        sound_module(sound_sw_ab, 2, 10)
        sound_module(sound_sw_dir, 1, 10)
        sound_module(sound_false, 0, 20)
        sound_module(sound_eat, 3, 10)
        sound_module(sound_dead, 0, 1000)
    
    if game_menu == 2:
        
        if sw_b.is_long_pressed():
            game_menu = 0
            
        display.fill(0)
        display.text('No Game Yet!',1,1,1)
        display.text('Hold B: Back',1,56,1)
        display.show()
        
    if game_menu == 3:
        
        if sw_b.is_long_pressed():
            game_menu = 0
            
        display.fill(0)
        display.text('No Game Yet!',1,1,1)
        display.text('Hold B: Back',1,56,1)
        display.show()

    
    






