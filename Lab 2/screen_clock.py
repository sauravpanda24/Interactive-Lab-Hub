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

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

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


while True:
    # Draw a black filled box to clear the image.
    #image = Image.new("RGB", (width, height))
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    #TODO: Lab 2 part D work should be filled in here. You should be able to look in cli_clock.py and stats.py 
    current_time_str = datetime.datetime.now().strftime("%H:%M:%S")
    utc_str = datetime.datetime.utcnow().strftime("%H:%M:%S")
    if not  buttonA.value and not buttonB.value:
        y = top
        draw.text((x, y),"NYC: " + current_time_str, font=font, fill="#FFFFFF")
        y = top + 50
        draw.text((x,y), "UTC: " +  utc_str, font=font, fill="#0000FF")
    elif not buttonA.value and buttonB.value:
        y = top
        #if int(current_time_str.split(':')[0]) > 12:
        text_time = num2str.get(int(current_time_str.split(':')[0])%12) 
        draw.text((x, y),f"{text_time} O' Clock", font=font, fill="#FFFFFF")
    elif buttonA.value and not buttonB.value:
        y = top 
        #if int(current_time_str.split(':')[0]) > 12:
       
        text_time = num2str.get(int(current_time_str.split(':')[0])%12)
        if int(current_time_str.split(':')[1]) >45:
            text_time = num2str.get((int(current_time_str.split(':')[0]) + 1)  %12)
            text_time = "Quater to " + text_time
        elif int(current_time_str.split(':')[1]) > 30:
            text_time = text_time + " Thirty"
        elif int(current_time_str.split(':')[1]) > 15:
            text_time = "Quater past "  + text_time
        AM_PM = "PM" if int(current_time_str.split(':')[0]) > 12 else "AM" 
        draw.text((x, y),f"{text_time} {AM_PM}", font=font, fill="#FFFFFF")
    else:
       y = top 
       draw.text((x, y),f"Btn A for AM/PM", font=font, fill="#FFFFFF")
       y = top + 50
       draw.text((x, y),f"Btn B for Clock time", font=font, fill="#FF0000")
       y = top + 100
       draw.text((x, y),f"BOTH Button for Dual time", font=font, fill="#FF00FF")

    disp.image(image, rotation)
    time.sleep(0.5)
