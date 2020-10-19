print("Starting ArVision")
import imutils
import numpy as np
import cv2
import time 
import digitalio
import board
import time
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageOps
import adafruit_rgb_display.st7735 as st7735 

############# OpenCV Setup 
cap = cv2.VideoCapture(0)

MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
fontCv = cv2.FONT_HERSHEY_SIMPLEX

age_list = ['(0, 2)', '(4, 6)', '(8, 12)', '(15, 20)', '(25, 32)', '(38, 43)', '(48, 53)', '(60, 100)']

gender_list = ['Male', 'Female']

age_net = cv2.dnn.readNetFromCaffe('deploy_age.prototxt', 'age_net.caffemodel')
gender_net = cv2.dnn.readNetFromCaffe('deploy_gender.prototxt', 'gender_net.caffemodel')

#return(age_net, gender_net)

#face haar cascade detection
face_cascade = cv2.CascadeClassifier("face.xml")

# FPS 
# used to record the time when we processed last frame 
prev_frame_time = 0
  
# used to record the time at which we processed current frame 
new_frame_time = 0

############# OpenCV Setup 
#############
############# Display Setup 
# First define some constants to allow easy resizing of shapes.
BORDER = 20
FONTSIZE = 24

# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D24)
reset_pin = digitalio.DigitalInOut(board.D25)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()


disp = st7735.ST7735R(
    spi,
    rotation=90,  
    height=160,
    width=120,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height

print("Width " + str(width) + " Height " + str(height))
image = Image.new("RGB", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)


# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image)

# First define some constants to allow easy positioning of text.
padding = -2
x = 0

# Load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)

############# Display Setup 

while True:
  
  ####OpenCV
  ret, frame = cap.read()
  if not ret: 
    break

  frame = imutils.resize(frame, width=200)
  frame = cv2.flip(frame, 0) 

  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  faces = face_cascade.detectMultiScale(gray, 1.3, 5)

  if(len(faces)>0):
   print("Found {} faces".format(str(len(faces))))

  for (x,y,w,h) in faces:
    gray = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
    
    
    # cv2.putText(gray,'FACE',(x, y-10), fontCv, 0.5, (11,255,255), 2, cv2.LINE_AA)
    # roi_gray = gray[y:y+h, x:x+w]

    # face_img = frame[y:y+h, h:h+w].copy()
    # blob = cv2.dnn.blobFromImage(face_img, 1, (227, 227), MODEL_MEAN_VALUES, swapRB=False)


    # gender_net.setInput(blob)
    # gender_preds = gender_net.forward()
    # gender = gender_list[gender_preds[0].argmax()]
    # print("Gender : " + gender)

    # age_net.setInput(blob)
    # age_preds = age_net.forward()
    # age = age_list[age_preds[0].argmax()]
    # print("Age Range: " + age)

    # overlay_text = "%s %s" % (gender, age)

    overlay_text = "test"
    cv2.putText(frame, overlay_text, (x, y), fontCv, 1, (255, 255, 255), 2, cv2.LINE_AA)
  ####OpenCV

  ####Display

  draw.rectangle((0, 0, width, height), outline=0, fill=0)

  

  
  ####Display

  # FPS Calculate
  new_frame_time = time.time()
  fps = 1/(new_frame_time-prev_frame_time) 
  prev_frame_time = new_frame_time 
  fps = int(fps) 
  fps = str(fps) 
  cv2.putText(frame, "FPS: " + fps, (20, 30), fontCv, 1, (255, 255, 255), 3, cv2.LINE_AA) 
  cv2.imshow('Video', frame)

  image = frame
  color_coverted = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

  draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))

  image = Image.fromarray(color_coverted)
  # Scale the image to the smaller screen dimension
  image_ratio = image.width / image.height
  screen_ratio = width / height
  if screen_ratio < image_ratio:
      scaled_width = image.width * height // image.height
      scaled_height = height
  else:
      scaled_width = width
      scaled_height = image.height * width // image.width
  image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

  # Crop and center the image
  x = scaled_width // 2 - width // 2
  y = scaled_height // 2 - height // 2
  image = image.crop((x, y, x + width, y + height))
  image = ImageOps.invert(image)
  disp.image(image)
  
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

cap.release()
cv2.destroyAllWindows() 
