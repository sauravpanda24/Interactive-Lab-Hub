import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import qwiic
import time
from adafruit_seesaw import seesaw, rotaryio, digitalio
import qwiic_joystick
import sys


def draw_text(text):
    oled.fill(0)
    # we just blanked the framebuffer. to push the framebuffer onto the display, we call show()
    oled.show()
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    # Draw a white background
    font = ImageFont.load_default()

    # Draw Some Text

    (font_width, font_height) = font.getsize(text)
    draw.text(
        (oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),
        text,
        font=font,
        fill=255,
    )
    oled.image(image)
    oled.show()

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
oled.fill(0)
# we just blanked the framebuffer. to push the framebuffer onto the display, we call show()
oled.show()
WIDTH = 128
HEIGHT = 32  # Change to 64 if needed
BORDER = 5
base_time = "00:00:00"
timer_started = False


print("VL53L1X Qwiic Test\n")
ToF = qwiic.QwiicVL53L1X()
if (ToF.sensor_init() == None):					 # Begin returns 0 on a good init
	print("Sensor online!\n")

seesaw = seesaw.Seesaw(board.I2C(), addr=0x36)

seesaw_product = (seesaw.get_version() >> 16) & 0xFFFF
print("Found product {}".format(seesaw_product))
if seesaw_product != 4991:
    print("Wrong firmware loaded?  Expected 4991")

seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
button = digitalio.DigitalIO(seesaw, 24)
button_held = False
is_updating = True
current_mode = 0
encoder = rotaryio.IncrementalEncoder(seesaw)
last_position = None

myJoystick = qwiic_joystick.QwiicJoystick()

if myJoystick.connected == False:
    print("The Qwiic Joystick device isn't connected to the system. Please check your connection", file=sys.stderr)

myJoystick.begin()

print("Initialized. Firmware Version: %s" % myJoystick.version)

while True:
    print("Curren modes:", current_mode, is_updating)
    if is_updating:
        all_time = base_time.split(':')
        all_time[current_mode] = "  "
        text = ':'.join(all_time)
    else:
        text = base_time

    draw_text(text)

    # negate the position to make clockwise rotation positive
    position = -encoder.position

    if position != last_position:
        last_position = position
        print("Position: {}".format(position))

    if myJoystick.button and not button_held:
        button_held = True
        if current_mode == 0 and is_updating == False:
            is_updating == True
        else:
            current_mode += 1
            if current_mode > 3:
                current_mode = 0
                is_updating = False

        print("Button pressed")

    if not myJoystick.button and button_held:
        button_held = False
        print("Button released")
    # try:
    #     ToF.start_ranging()  # Write configuration bytes to initiate measurement
    #     time.sleep(.005)
    #     distance = ToF.get_distance()  # Get the result of the measurement from the sensor
    #     time.sleep(.005)
    #     ToF.stop_ranging()
    #
    #     distanceInches = distance / 25.4
    #     distanceFeet = distanceInches / 12.0
    #
    #     print("Distance(mm): %s Distance(ft): %s" % (distance, distanceFeet))
    #
    # except Exception as e:
    #     print(e)
    print("X: %d, Y: %d, Button: %d" % ( \
        myJoystick.horizontal, \
        myJoystick.vertical, \
        myJoystick.button))

    time.sleep(.3)
    if is_updating:
        draw_text(base_time)
    time.sleep(.3)