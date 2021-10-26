import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import qwiic
import time
from adafruit_seesaw import seesaw, rotaryio, digitalio
import qwiic_joystick
import sys
import subprocess
from adafruit_bus_device.i2c_device import I2CDevice


def draw_text(text):
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    # Draw a white background
    font = ImageFont.load_default()

    # Draw Some Text
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    (font_width, font_height) = font.getsize(text)
    draw.text(
        (oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),
        text,
        font=font,
        fill=255,
    )
    oled.image(image)
    oled.show()


def get_distance():
    try:
        ToF.start_ranging()  # Write configuration bytes to initiate measurement
        time.sleep(.005)
        distance = ToF.get_distance()  # Get the result of the measurement from the sensor
        time.sleep(.005)
        ToF.stop_ranging()

        distanceInches = distance / 25.4
        distanceFeet = distanceInches / 12.0

        print("Distance(mm): %s Distance(ft): %s" % (distance, distanceFeet))
        return distanceFeet
    except Exception as e:
        print(e)


def read_register(dev, register, n_bytes=1):
    # write a register number then read back the value
    reg = register.to_bytes(1, 'little')
    buf = bytearray(n_bytes)
    with dev:
        dev.write_then_readinto(reg, buf)
    return int.from_bytes(buf, 'little')


def is_button_pressed():
    btn_status = read_register(device, STATUS)
    return btn_status&IS_PRESSED != 0
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

ToF = qwiic.QwiicVL53L1X()
if (ToF.sensor_init() == None):					 # Begin returns 0 on a good init
	print("Sensor online!\n")

seesaw = seesaw.Seesaw(board.I2C(), addr=0x36)

seesaw_product = (seesaw.get_version() >> 16) & 0xFFFF

seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
button = digitalio.DigitalIO(seesaw, 24)
button_held = True
is_updating = False
current_mode = 0
encoder = rotaryio.IncrementalEncoder(seesaw)
last_position = None
volume = 8
is_done = False

myJoystick = qwiic_joystick.QwiicJoystick()

if myJoystick.connected == False:
    print("The Qwiic Joystick device isn't connected to the system. Please check your connection", file=sys.stderr)

myJoystick.begin()

start_time = None
c_value = 0
timer_time = 0

# LED Button def
DEVICE_ADDRESS = 0x6f  # device address of our button
STATUS = 0x03 # reguster for button status
AVAILIBLE = 0x1
BEEN_CLICKED = 0x2
IS_PRESSED = 0x4


# The follow is for I2C communications
i2c = busio.I2C(board.SCL, board.SDA)
device = I2CDevice(i2c, DEVICE_ADDRESS)


while True:
    print("Current modes:", current_mode," || Is updating :", is_updating)
    position = -encoder.position
    if position != last_position:
        if last_position and last_position > position:
            print("volume down")
            volume -= 1
            if volume < 0:
                volume = 0
        if last_position and last_position < position:
            print("volume up")
            volume += 1
            if volume > 10:
                volume = 10
        last_position = position
        command = ["amixer", "sset", "Master", "{}%".format(volume*10)]
        subprocess.Popen(command)
        draw_text(f"Volume: {volume}")
        subprocess.run(['aplay', 'volume.wav'])
        time.sleep(.5)
        print("Position: {}".format(position))
    if is_done:
        text = "Ready!!"
        subprocess.run(['aplay', 'ready.wav'])
        draw_text(text)
        time.sleep(.2)
        if is_button_pressed():
            is_done = False
            timer_started = False
            base_time = "00:00:00"
        if get_distance() < 2:
            text = "Keep Distance"
            draw_text(text)
            subprocess.run(['aplay', 'distance.wav'])
            time.sleep(0.2)
        continue
    if timer_started and not is_updating:
        if not start_time:
            start_time = time.time()
            for i,v in enumerate(base_time.split(':')):
                timer_time += int(v)*(2-i)*60
                if i == 2:
                    timer_time += int(v)
        else:
            current_time = time.time()
            secs = int(current_time - start_time)
            left_time = timer_time - secs
            hr = left_time // 60 //60 %60
            hr = '0'+str(hr) if hr < 10 else str(hr)
            mm = left_time // 60 % 60
            mm = '0' + str(mm) if mm < 10 else str(mm)
            ss = left_time % 60
            ss = '0' + str(ss) if ss < 10 else str(ss)
            base_time = f'{hr}:{mm}:{ss}'
            if left_time < 1:
                is_done = True

    if is_updating:
        all_time = base_time.split(':')
        all_time[current_mode] = "  "
        text = ':'.join(all_time)
    else:
        text = base_time

    if is_updating:
        all_time = base_time.split(':')
        if c_value:
            all_time[current_mode] = '0'+str(c_value) if c_value < 10 else str(c_value)
        base_time = ':'.join(all_time)
    print("Current Base Time: ", base_time)
    draw_text(text)

    if is_button_pressed():
        timer_started = True

    # negate the position to make clockwise rotation positive
    position = -encoder.position

    if position != last_position:
        last_position = position
        print("Position: {}".format(position))

    if myJoystick.button and not button_held:
        button_held = True
        if current_mode == 0 and is_updating == False:
            is_updating = True
        else:
            current_mode += 1
            c_value = 0
            if current_mode > 2:
                current_mode = 0
                c_value = 0
                is_updating = False

        print("Button pressed")

    if not myJoystick.button and button_held:
        button_held = False
        print("Button released")

    if myJoystick.vertical < 250:
        c_value += 1
        if c_value > 60: c_value = 60
    if myJoystick.vertical > 750:
        c_value -= 1
        if c_value < 0: c_value = 0

    if myJoystick.horizontal > 750:
        c_value += 1
        if c_value > 60: c_value = 60
    if myJoystick.horizontal < 250:
        c_value -= 1
        if c_value < 0: c_value = 0


    time.sleep(.2)
    if is_updating:
        draw_text(base_time)
    time.sleep(.2)
