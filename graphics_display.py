# SPDX-FileCopyrightText: <text> 2020 Tony DiCola, James DeVito,
# and 2020 Melissa LeBlanc-Williams, for Adafruit Industries </text>

# SPDX-License-Identifier: MIT

# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!

import busio
import digitalio
from board import D4, SCL, SDA
from PIL import Image, ImageDraw, ImageFont

import adafruit_ssd1305

class Graphics():
    def __init__(self):

        # Define the Reset Pin
        oled_reset = digitalio.DigitalInOut(D4)

        # Create the I2C interface.
        i2c = busio.I2C(SCL, SDA)

        # Create the SSD1305 OLED class.
        # The first two parameters are the pixel width and pixel height.  Change these
        # to the right size for your display!
        self.disp = adafruit_ssd1305.SSD1305_I2C(128, 32, i2c, reset=oled_reset)

        # Clear display.
        self.disp.fill(0)
        self.disp.show()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self.width = self.disp.width
        self.height = self.disp.height
        image = Image.new("1", (self.width, self.height))

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(image)

        # Draw some shapes.
        # First define some constants to allow easy resizing of shapes.
        self.padding = -2
        self.top = self.padding
        self.bottom = self.height - self.padding
        # Move left to right keeping track of the current x position for drawing shapes.
        self.x = 0

        # Load default font.
        self.font = ImageFont.load_default()

        # Alternatively load a TTF font.  Make sure the .ttf font file is in the
        # same directory as the python script!
        # Some other nice fonts to try: http://www.dafont.com/bitmap.php
        # font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)

    def display_stops(self, train_data):

        # assumes stop_data is passed in in the following format:
        # [[predicted, time to go, closest stop, stops away, direction]] 
        # get the two closest trains going North/South
        stop_data = [0, 0, 0, 0]
        i_north = 0
        i_south = 2
        for train in train_data:
            if train[4]:
                if i_north < 2:
                    stop_data[i_north] = train[1]
                    i_north += 1
            else:
                if i_south < 4:
                    stop_data[i_south] = train[1]
                    i_south += 1

        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

        # Assumes that we only care about the two closest trains going North/South
        # That's also all I can fit on the display
        self.draw.text((self.x, self.top + 0), "Lynwood City Center: " + stop_data[0] + " min", font=self.font, fill=255)   
        self.draw.text((self.x, self.top + 8), "Lynwood City Center: " + stop_data[1] + " min", font=self.font, fill=255)   
        self.draw.text((self.x, self.top + 16), "Federal Way: " + stop_data[2] + " min", font=self.font, fill=255)   
        self.draw.text((self.x, self.top + 25), "Federal Way: " + stop_data[3] + " min", font=self.font, fill=255)   

        # Display image.
        self.disp.image(self.image)
        self.disp.show()
