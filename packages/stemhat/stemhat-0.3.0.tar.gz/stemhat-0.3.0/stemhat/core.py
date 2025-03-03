import smbus2 as smbus
from gpiozero import Button,DigitalOutputDevice, DigitalInputDevice
import time
import adafruit_ssd1306
from busio import I2C
from board import SCL, SDA
from PIL import Image, ImageDraw, ImageFont
import importlib.resources
from adafruit_apds9960.apds9960 import APDS9960

import os

STEMHAT_ADDRESS         = 0x08   #Stemhat Address
OLED_ADDRESS            = 0x3c   #OLED    Address
AHT20_ADDRESS           = 0x38   #AHT20   Address 

I2C_REG_FIRMWARE_REV    = 0x00
I2C_REG_SRV1            = 0x01
I2C_REG_SRV2            = 0x02
I2C_REG_SRV3            = 0x03
I2C_REG_SRV4            = 0x04
I2C_REG_M1A             = 0x05
I2C_REG_M1B             = 0x06
I2C_REG_M2A             = 0x07
I2C_REG_M2B             = 0x08
I2C_REG_R0              = 0x09 
I2C_REG_G0              = 0x0A  
I2C_REG_B0              = 0x0B  
I2C_REG_R1              = 0x0C 
I2C_REG_G1              = 0x0D  
I2C_REG_B1              = 0x0E 
I2C_REG_AN0             = 0x0F
I2C_REG_AN1             = 0x10
I2C_REG_LIGHT           = 0x11
I2C_REG_VIN             = 0x12
I2C_REG_BUZZER          = 0x13
I2C_REG_RST             = 0x14

bus = smbus.SMBus(1)

def SetLED(led,red,blue,green):
    if led not in [0, 1]:
        raise ValueError("LED must be 0 or 1")
    if not (0 <= red <= 255):
        raise ValueError("Red value must be between 0 and 255")
    if not (0 <= blue <= 255):
        raise ValueError("Blue value must be between 0 and 255")
    if not (0 <= green <= 255):
        raise ValueError("Green value must be between 0 and 255")
    
    if led == 0:
        bus.write_byte_data(STEMHAT_ADDRESS,I2C_REG_R0,red)
        bus.write_byte_data(STEMHAT_ADDRESS,I2C_REG_B0,blue)
        bus.write_byte_data(STEMHAT_ADDRESS,I2C_REG_G0,green)
    else:
        bus.write_byte_data(STEMHAT_ADDRESS,I2C_REG_R1,red)
        bus.write_byte_data(STEMHAT_ADDRESS,I2C_REG_B1,blue)
        bus.write_byte_data(STEMHAT_ADDRESS,I2C_REG_G1,green)

def SetBuzzer(frequency):
    if not (0 <= frequency <= 2550):
        raise ValueError("Frequency must be between 0 and 2550")
    bus.write_byte_data(STEMHAT_ADDRESS,I2C_REG_BUZZER,int(frequency/10))

def SetMotors(LeftMotorSpeed,RightMotorSpeed):
    if not (-100 <= LeftMotorSpeed <= 100):
        raise ValueError("Left motor speed must be between -100 and 100")
    if not (-100 <= RightMotorSpeed <= 100):
        raise ValueError("Right motor speed must be between -100 and 100")

    speed1 = int(abs(LeftMotorSpeed) * 2.55)
    speed2 = int(abs(RightMotorSpeed) * 2.55)

    if LeftMotorSpeed > 0:
        bus.write_byte_data(STEMHAT_ADDRESS, I2C_REG_M1A, speed1)
        bus.write_byte_data(STEMHAT_ADDRESS, I2C_REG_M1B, 0)
    elif LeftMotorSpeed < 0:
        bus.write_byte_data(STEMHAT_ADDRESS, I2C_REG_M1A, 0)
        bus.write_byte_data(STEMHAT_ADDRESS, I2C_REG_M1B, speed1)
    else:
        bus.write_byte_data(STEMHAT_ADDRESS, I2C_REG_M1A, 0)
        bus.write_byte_data(STEMHAT_ADDRESS, I2C_REG_M1B, 0)

    if RightMotorSpeed > 0:
        bus.write_byte_data(STEMHAT_ADDRESS, I2C_REG_M2A, speed2)
        bus.write_byte_data(STEMHAT_ADDRESS, I2C_REG_M2B, 0)
    elif RightMotorSpeed < 0:
        bus.write_byte_data(STEMHAT_ADDRESS, I2C_REG_M2A, 0)
        bus.write_byte_data(STEMHAT_ADDRESS, I2C_REG_M2B, speed2)
    else:
        bus.write_byte_data(STEMHAT_ADDRESS, I2C_REG_M2A, 0)
        bus.write_byte_data(STEMHAT_ADDRESS, I2C_REG_M2B, 0)

def SetServo(servo,angle):
    if servo not in [1, 2, 3, 4]:
        raise ValueError("Servo must be 1, 2, 3 or 4")
    if not (0 <= angle <= 180):
        raise ValueError("Angle must be between 0 and 180")
    
    if servo == 1:
        bus.write_byte_data(STEMHAT_ADDRESS,I2C_REG_SRV1,angle)
    elif servo == 2:
        bus.write_byte_data(STEMHAT_ADDRESS,I2C_REG_SRV2,angle)
    elif servo == 3:
        bus.write_byte_data(STEMHAT_ADDRESS,I2C_REG_SRV3,angle)
    else:
        bus.write_byte_data(STEMHAT_ADDRESS,I2C_REG_SRV4,angle)

def GetAnalog(analog):

    if analog not in [0, 1]:
        raise ValueError("Analog must be 0 or 1")
    
    if analog == 0:
        bus.read_byte_data(STEMHAT_ADDRESS,I2C_REG_AN0)
        return bus.read_byte_data(STEMHAT_ADDRESS,I2C_REG_AN0)
    else:
        bus.read_byte_data(STEMHAT_ADDRESS,I2C_REG_AN1)
        return bus.read_byte_data(STEMHAT_ADDRESS,I2C_REG_AN1)

def GetLightSensor():
    bus.read_byte_data(STEMHAT_ADDRESS,I2C_REG_LIGHT)
    value = bus.read_byte_data(STEMHAT_ADDRESS,I2C_REG_LIGHT)
    return value

def GetVoltage():
    bus.read_byte_data(STEMHAT_ADDRESS,I2C_REG_VIN)
    return bus.read_byte_data(STEMHAT_ADDRESS,I2C_REG_VIN)

trig = DigitalOutputDevice(20)
echo = DigitalInputDevice(26, pull_up=False)
def GetUltrasonic():
    trig.off()
    time.sleep(0.001)
    trig.on()
    time.sleep(0.00001)
    trig.off()

    start_time = time.time()
    timeout = start_time + 0.3
    while echo.is_active == 0:
        if time.time() > timeout:
            return -1
    start_time = time.time()

    timeout = start_time + 0.3
    while echo.is_active == 1:
        if time.time() > timeout:
            return -1
    end_time = time.time()

    duration = (end_time - start_time) * 1_000_000
    distance = duration / 58

    return int(distance)


def GetTemperature():
    data = bus.read_i2c_block_data(AHT20_ADDRESS,0x71,1)
    if (data[0] | 0x08) == 0:
        print('Initialization error')

    bus.write_i2c_block_data(AHT20_ADDRESS,0xac,[0x33,0x00])
    time.sleep(0.05)

    data = bus.read_i2c_block_data(AHT20_ADDRESS,0x71,7)

    Traw = ((data[3] & 0xf) << 16) + (data[4] << 8) + data[5]
    temperature = 200*float(Traw)/2**20 - 50
    return temperature

def GetHumidity():
    data = bus.read_i2c_block_data(AHT20_ADDRESS,0x71,1)
    if (data[0] | 0x08) == 0:
        print('Initialization error')

    bus.write_i2c_block_data(AHT20_ADDRESS,0xac,[0x33,0x00])
    time.sleep(0.05)

    data = bus.read_i2c_block_data(AHT20_ADDRESS,0x71,7)

    Hraw = ((data[3] & 0xf0) >> 4) + (data[1] << 12) + (data[2] << 4)
    humidity = 100*float(Hraw)/2**20
    return humidity

def Reset():
    OledClear()
    OledUpdate()
    bus.write_byte_data(STEMHAT_ADDRESS,I2C_REG_RST,0xA5)


# ------------------------------------ Button ------------------------------------
# --------------------------------------------------------------------------------
buttons = [Button(5), Button(6)]
buttonStates = [False, False]

def buttonPressed0():
    buttonStates[0] = True

def buttonReased0():
    buttonStates[0] = False
    
def buttonPressed1():
    buttonStates[1] = True

def buttonReased1():
    buttonStates[1] = False

buttons[0].when_pressed = buttonPressed0
buttons[0].when_released = buttonReased0

buttons[1].when_pressed = buttonPressed1
buttons[1].when_released = buttonReased1

def GetButton(button):
    if button not in [5, 6]:
        raise ValueError("Button must be 5 or 6")
    return buttonStates[button-5]


# ------------------------------------- OLED -------------------------------------
# --------------------------------------------------------------------------------
i2c = I2C(SCL, SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)



def get_font_path():
    with importlib.resources.path("stemhat", "Arial.ttf") as font_path:
        return str(font_path)
font_path = get_font_path()


def OledRectangle(x, y, height, width, fill, outline_width):
    if not (0 <= x < oled.width and 0 <= y < oled.height):
        raise ValueError("x and y must be within the range of the OLED dimensions(128*64")
    if not (isinstance(height, int) and height > 0):
        raise ValueError("Height must be a positive integer")
    if not (isinstance(width, int) and width > 0):
        raise ValueError("Width must be a positive integer")
    if not (isinstance(outline_width, int) and outline_width > 0):
        raise ValueError("Outline width must be a positive integer")
    if not (fill in [0, 1]):
        raise ValueError("fill must be 0 (outline) or 1 (solid)")

    
    if(fill == 0):
        draw.rectangle((x, y, height, width), outline=1, width=outline_width)
    else:
        draw.rectangle((x, y, height, width), outline=1,fill=1, width=outline_width)

def OledLine(x1,y1,x2,y2):
    if not (0 <= x1 < oled.width and 0 <= y1 < oled.height):
        raise ValueError("x1 and y1 must be within the range of the OLED dimensions (128*64)")
    if not (0 <= x2 < oled.width and 0 <= y2 < oled.height):
        raise ValueError("x2 and y2 must be within the range of the OLED dimensions (128*64)")
    draw.line((x1, y1, x2, y2), fill=1)

def OledPoint(x,y,color):
    if not (0 <= x < oled.width and 0 <= y < oled.height):
        raise ValueError("x and y must be within the range of the OLED dimensions (128*64)")
    if not (color in [0, 1]):
        raise ValueError("Color must be 0 (black) or 1 (white)")
    draw.point((x, y), fill=color)

def OledCircles(x,y,radius,outline,outline_width):
    if not (0 <= x < oled.width and 0 <= y < oled.height):
        raise ValueError("x and y must be within the range of the OLED dimensions (128*64)")
    if not (isinstance(radius, int) and radius > 0):
        raise ValueError("Radius must be a positive integer")
    if not (isinstance(outline_width, int) and outline_width > 0):
        raise ValueError("Outline width must be a positive integer")
    if not (outline in [0, 1]):
        raise ValueError("Outline must be 0 (outline) or 1 (solid)")
    if(outline == 0):
        draw.circle((x,y),radius,outline=outline,width=outline_width)
    else:
        draw.circle((x,y),radius,outline=outline,fill=1,width=outline_width)

def OledText(x,y,text,size,color):
    if not (0 <= x < oled.width and 0 <= y < oled.height):
        raise ValueError("x and y must be within the range of the OLED dimensions (128*64)")
    if not isinstance(text, str):
        raise ValueError("Text must be a string")
    if not (isinstance(size, int) and size > 0):
        raise ValueError("Size must be a positive integer")
    if not (color in [0, 1]):
        raise ValueError("Color must be 0 (black) or 1 (white)")
    size = size+9
    draw.text((x, y), text, font=ImageFont.truetype(font_path, size), fill=color)

def OledImage(x, y, img_path, scale, invert):
    if not (0 <= x < oled.width and 0 <= y < oled.height):
        raise ValueError("x and y must be within the range of the OLED dimensions (128*64)")
    if not isinstance(img_path, str):
        raise ValueError("Image path must be a string")
    if not os.path.isfile(img_path):
        raise ValueError("Image file does not exist")
    if not (scale in [0, 1]):
        raise ValueError("Scale must be 0 (no scaling) or 1 (scaling)")
    if not (invert in [0, 1]):
        raise ValueError("Invert must be 0 (no inversion) or 1 (inversion)")
    
    try:
        bmp_image = Image.open(img_path).convert("1")
    except Exception as e:
        raise ValueError(f"Failed to open or convert image: {e}")


    if scale == 1:
        bmp_image = bmp_image.resize((oled.width, oled.height), Image.LANCZOS)
    else:
        if bmp_image.width > oled.width or bmp_image.height > oled.height:
            bmp_image = bmp_image.crop((0, 0, oled.width, oled.height))
        
    if invert == 0:
        bmp_image = Image.eval(bmp_image, lambda x: 255 - x)
    

    # Draw the image at the specified x and y coordinates
    draw.bitmap((x, y), bmp_image, fill=1)

def OledScroll(direction,speed, start_page, end_page):
    if not (0 <= direction <= 1):
        raise ValueError("Direction must be 0 (left) or 1 (right)")
    if not (0 <= speed <= 8):
        raise ValueError("Speed must be between 0 and 8")
    if not (0 <= start_page <= 7):
        raise ValueError("Start page must be between 0 and 7")
    if not (0 <= end_page <= 7):
        raise ValueError("End page must be between 0 and 7")
    if start_page >= end_page:
        raise ValueError("Start page must be less than end page")

    if direction == 0:
        oled.write_cmd(0x27)
    else:
        oled.write_cmd(0x26)
    oled.write_cmd(0x00)
    oled.write_cmd(start_page)
    oled.write_cmd(speed)
    oled.write_cmd(end_page)
    oled.write_cmd(0x00)
    oled.write_cmd(0xFF)
    oled.write_cmd(0x2F)

def OledScrollStop():
    oled.write_cmd(0x2E)

def OledClear():
    draw.rectangle((0,0,127,63),0,1,0)

def OledUpdate():
    oled.image(image)
    oled.show()



apds = 0
def APDSsetMode(mode):
    if mode==1:
        apds = APDS9960(i2c)
        apds.enable_proximity = True   
        apds.enable_gesture = False
        apds.enable_color = False 
    elif mode==2:
        apds = APDS9960(i2c)
        apds.enable_proximity = True  
        apds.enable_gesture = True
        apds.enable_color = False
    elif mode==3:
        apds = APDS9960(i2c)
        apds.enable_proximity = False   
        apds.enable_gesture = False
        apds.enable_color = True
        

def APDSread_gesture():
    """Return the detected gesture or 0 if no gesture detected."""
    gesture = apds.gesture()
    return gesture if gesture else 0

def APDSread_color():
    """Return (R, G, B, Clear) values or None if no valid reading."""
    if apds.color_data_ready:
        return apds.color_data
    return None

def APDSread_proximity():
    """Return proximity value (0-255)."""
    return apds.proximity

