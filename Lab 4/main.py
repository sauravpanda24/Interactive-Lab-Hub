import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import qwiic
import time

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)


print("VL53L1X Qwiic Test\n")
ToF = qwiic.QwiicVL53L1X()
if (ToF.sensor_init() == None):					 # Begin returns 0 on a good init
	print("Sensor online!\n")

oled.fill(0)
# we just blanked the framebuffer. to push the framebuffer onto the display, we call show()
oled.show()
WIDTH = 128
HEIGHT = 32  # Change to 64 if needed
BORDER = 5

while True:
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    # Draw a white background
    font = ImageFont.load_default()

    # Draw Some Text
    text = "Hello World!"
    (font_width, font_height) = font.getsize(text)
    draw.text(
        (oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),
        text,
        font=font,
        fill=255,
    )
    oled.image(image)
    oled.show()
    try:
        ToF.start_ranging()  # Write configuration bytes to initiate measurement
        time.sleep(.005)
        distance = ToF.get_distance()  # Get the result of the measurement from the sensor
        time.sleep(.005)
        ToF.stop_ranging()

        distanceInches = distance / 25.4
        distanceFeet = distanceInches / 12.0

        print("Distance(mm): %s Distance(ft): %s" % (distance, distanceFeet))

    except Exception as e:
        print(e)