from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf # it is actually included in ssd1306

# micropython documentation sucks
# MONO_HLSB: 1 pixel = 1 bit; 0xFF = 8 pixels is ON (depenends on the display mode)
# for compatibility, considering image2cpp, bitmap_d below is the best way to draw bitmap

# i2c config from machine module
i2c = I2C(0, scl=Pin(13), sda=Pin(12), freq=400000)

# scan the address of peripherals 
print('i2c address: ' + hex(i2c.scan()[0]).upper())

#display object from ssd1306 module
display = SSD1306_I2C(128, 64, i2c)
display.poweron()

# |
# |
# --- data study ---
# bin format
val = 0b11111111  # 255; 0xFF
val_1 = 0xFF  #  same as 0b11111111
val_2 = b'0xFF'
print('Dec: ', val, val_1, val_2)

# bytearray format
data = bytearray(8)   # an array called data; it has 8 bytes, 64bits; 2-digit Hex represents 8-digts Bin; 
data[0] = 0xFF        # Editing the first bit
data[3] = 0x0e        # Editing the 3rd bit
print('data: ', data) # print will show bytearray directly

# bytearray study
bitmap_1 = bytearray([
    0b11111111,  # all on
    0b00000000,  # all off
    0b10101010,  # on/off
    0b01010101,  # off/on
    
    0x00,        # all off # 0b,0x could be used together
    0xFF         # all on
])

# format:[]; it is a list of bytes
bitmap_a = bytearray([0xFF, 0xFF]) # list

# format:b' '; it is a list of bytes
bitmap_b = bytearray(b'\xFF\xFF') # data # freaking confusing

bitmap_c = bytearray([
    0b10100000, # even tho, only 3 bits; stil, 8 bits at least; because: 'byte'array
    0b01000000,
    0b10100000
])

bitmap_d = bytearray([
    0xa0, # hex version of bin
    0x40,
    0xa0
])

bitmap_e = bytearray(
    b'\xa0\x40\xa0'
)

# format:b''; it is a list of bytes
data_1 = bytearray(b'\x01\x02\x00\x00\x00')
data_1[1] = 255    # 修改第二个字节的值为 255（十六进制 0xFF）
print('data_1[0]: ', data_1[0])  # 输出：1（第一个字节的值）
print('data_1: ', data_1)      # 输出：bytearray(b'\x01\xff\x00\x00\x00')

# |
# |
# --- creating frame buffers ---
# to understand framebuf; fb_1 is a object stored 8 bytes data. the object is a buffer waiting to be blit()
buffer = bytearray(8)
fbuf = framebuf.FrameBuffer(buffer, 8, 8, framebuf.MONO_HLSB)

# comparison_1: same bytearray, differnt format
# because: each byte represent 8 pixels instead of 1 with 256depth
fb_1 = framebuf.FrameBuffer(bitmap_1, 8, 6, framebuf.MONO_HLSB)
fb_2 = framebuf.FrameBuffer(bitmap_1, 24, 1, framebuf.MONO_HLSB)

# comparison_2: bitmap_a vs. bitmap_b
fb_a = framebuf.FrameBuffer(bitmap_a, 16, 1, framebuf.MONO_HLSB)
fb_b = framebuf.FrameBuffer(bitmap_b, 8, 2, framebuf.MONO_HLSB)

# comparison_3: bitmap_c / d / e: differnet format of bitmap
fb_c = framebuf.FrameBuffer(bitmap_c, 3, 3, framebuf.MONO_HLSB)
fb_d = framebuf.FrameBuffer(bitmap_d, 3, 3, framebuf.MONO_HLSB)
fb_e = framebuf.FrameBuffer(bitmap_e, 3, 3, framebuf.MONO_HLSB)

# to display stuff
display.blit(fbuf, 0, 0)

# comparison_1:
display.blit(fb_1, 0, 0)
display.blit(fb_2, 20, 0)

# comparison_2:
display.blit(fb_a, 20, 10)
display.blit(fb_b, 20, 12)

# comparison_3:
display.blit(fb_c, 60, 0)
display.blit(fb_d, 66, 0)
display.blit(fb_e, 72, 0)

# there is no auto wrapping :/
display.text('Hi! This is a test for understanding MycroPython', 0, 20, 1)

display.show()
