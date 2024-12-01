# TJ Chen learning with Chatgpt

from machine import Pin
import time

class Button: #class name always starts with capital letters
    
#     self is an object

#     __init__ is a 'spacial function' at lower level of uPy
    def __init__(self, pin_num, debounce_time, long_press_window):
#         a list of aspects of the instance will be created
#         interfacing i/o ths class Button
        self.button = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        self.debounce_time = debounce_time  # ms
        self.long_press_window = long_press_window # ms
        
#         private variables or attributes 
        self.last_state = 1
        self.last_time = 0
        self.current_time = 0
        self.current_state = 0
        self.button_value = 0
        

    def is_pressed(self):
        self.current_time = time.ticks_ms()
        self.current_state = self.button.value()
        if self.current_state == 0 and self.last_state == 1: # the moment it has been pressedd
            if time.ticks_diff(self.current_time, self.last_time) > self.debounce_time:
                self.last_time = self.current_time
                self.last_state = self.current_state
                return True
        self.last_state = self.current_state
        return False
    
    def is_long_pressed(self):
        self.current_time = time.ticks_ms()
        self.current_state = self.button.value()
        
        if self.current_state == 0 and self.last_state == 1: # the moment it has been pressedd
            if time.ticks_diff(self.current_time, self.last_time) > self.debounce_time: # after debounce_time
                self.last_time = self.current_time # reset the timmer only when pressed && exceeded debounce_time
            
        if self.current_state == 0 and time.ticks_diff(self.current_time, self.last_time) > self.long_press_window:
                return True
            
        self.last_state = self.current_state
        return False

    def value(self):
#         probably redundent here; just for practising 
        self.button_value = self.button.value()
        return self.button_value
