import time
import subprocess
import digitalio
import board
import datetime
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
import numpy as np
# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)


height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90


def roman_val(val):
    roman_single = ['','I','II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']
    units = ['', 'X', 'XX', 'XXX', 'XXXX', 'L', 'LX']
    out = ""
    if int(val) > 9:
        out += units[int(val[0])] + roman_single[int(val[1])]
    else:
        out += roman_single[int(val)]
    return out

draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)

padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()
image2 = Image.open('day-night.png')
image2 = image2.convert('RGB')
image2 = image2.resize((100, 100), Image.BICUBIC)
num2str = {
    0: "Tweleve",
    1: "One",
    2: "Two",
    3: "Three",
    4: "Four",
    5: "Five",
    6: "Six",
    7: "Seven",
    8: "Eight",
    9: "Nine",
    10: "Ten",
    11: "Eleven",
   12: "Tweleve"
}

mode_str = {
1: 'ROMAN Clock',
2: 'Time To Day Change',
3: 'Normal Time',
4: 'Stop Watch'
}

mode =1
button_pressed = 0
button_b = 0
button_b_was_pressed = 0
started = 0
t1 = "0:00"
while True:
    # Draw a black filled box to clear the image.
    #image = Image.new("RGB", (width, height))
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((x, top),"Mode: " + mode_str.get(mode, 'unknown'), font=font, fill="#FFFFFF")
    #TODO: Lab 2 part D work should be filled in here. You should be able to look in cli_clock.py and stats.py 
    current_time_str = datetime.datetime.now().strftime("%H:%M:%S")
    utc_str = datetime.datetime.utcnow().strftime("%H:%M:%S")
    print("mode : ", mode)
    if not buttonA.value:
        button_pressed += 1
    else:
        button_pressed = 0
    if button_pressed > 3:
        mode+= 1
        button_pressed = -5
    if mode > 4:
        mode = 1
    if mode == 1:
        y = top + 30
        draw.text((x, y),"Hour: " + roman_val(current_time_str.split(':')[0]), font=font_big, fill="#FFFFFF")
        y = top + 60
        draw.text((x,y), "Min: " + roman_val(current_time_str.split(':')[1]), font=font_big, fill="#0000FF")
        y = top + 90
        draw.text((x,y), "Sec: " + roman_val(current_time_str.split(':')[2]), font=font_big, fill="#0000FF")
    elif mode == 2:
        y = top + 30
        li = current_time_str.split(':')
        seconds = 86400 - 3600*int(li[0]) - 60*int(li[1]) - int(li[2])
        draw.text((x, y),f"Seconds : {seconds}", font=font, fill="#FFFFFF")
        y = top + 60
        draw.text((x, y),f"Minutes : {int(seconds/60)}", font=font, fill="#FFFFFF")
        y = top + 90
        draw.text((x, y),f"hours : {int(seconds/3600)}", font=font, fill="#FFFFFF")
    elif mode == 3:
        y = top + 30
        draw.text((x, y),"NYC: " + current_time_str, font=font, fill="#FFFFFF")
        y = top + 60
        draw.text((x,y), "UTC: " +  utc_str, font=font, fill="#0000FF")
    elif mode == 4:
        y = top + 30
        if buttonB.value:
            button_b = 1
        else:
            button_b = 0
        if button_b_was_pressed == 1 and button_b ==0 and not started:
            print("Starting sprint")
            start = datetime.datetime.now()
            started = 1
        elif button_b_was_pressed == 1 and button_b ==0:
            started = 0
            
        button_b_was_pressed = button_b
        if started:
            difference = datetime.datetime.now() - start
            t1 = f'{int(difference.seconds/60)}:{int(difference.seconds%60)}'
        y = top + 30
        draw.text((x,y), f"Time Elapsed", font=font_big, fill="#0000FF")
        y = top + 60
        draw.text((x,y), f"    mm:ss", font=font_big, fill="#0000FF")
        y = top + 90
        draw.text((x,y), f"     {t1}", font=font_big, fill="#0000FF")
        
    

    disp.image(image, rotation)
    time.sleep(0.5)
