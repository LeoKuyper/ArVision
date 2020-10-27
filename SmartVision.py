print("Starting ArVision")
import imutils
from imutils.video.pivideostream import PiVideoStream
import numpy as np
import cv2
import time 
import digitalio
import board
import time
import argparse
import os
import subprocess
import shlex
import getpass
import speech_recognition as sr
import pyttsx3
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont, ImageOps
import adafruit_rgb_display.st7735 as st7735 

mode = "none"

print("Setting up Voice")
engine = pyttsx3.init()

def speak(text):  
  engine.say(text)
  engine.runAndWait()

print("Warming up Camera")
############# OpenCV Setup 
cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)
time.sleep(2)
cap.set(15, -8.0)

def rescale_frame(frame, percent=75):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)


print(str(cap.get(3)) + " x " + str(cap.get(4))+ "  Exposure at " + str(cap.get(15)))
MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
fontCv = cv2.FONT_HERSHEY_SIMPLEX

age_list = ['(0, 2)', '(4, 6)', '(8, 12)', '(15, 20)', '(25, 32)', '(38, 43)', '(48, 53)', '(60, 100)']

gender_list = ['Male', 'Female']

age_net = cv2.dnn.readNetFromCaffe('deploy_age.prototxt', 'age_net.caffemodel')
gender_net = cv2.dnn.readNetFromCaffe('deploy_gender.prototxt', 'gender_net.caffemodel')
#return(age_net, gender_net)

#face haar cascade detection
face_cascade = cv2.CascadeClassifier("face.xml")

# construct the argument parse and parse the arguments


# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "monitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt.txt", "MobileNetSSD_deploy.caffemodel")
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

############# Button Setup 
BUTTON_GPIO = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
pressed = False
############# Button Setup 

speak("Glasses ready")

old = ""
new = ""

while True:
  os.system('cls' if os.name == 'nt' else 'clear')
  ####OpenCV
  ret, frameM = cap.read()
  if not ret: 
    break
  size = 160
  frame = rescale_frame(frameM, percent=100)
  frame = imutils.resize(frame, width=size)
  frame = cv2.flip(frame, 0) 
  frame = cv2.flip(frame, 2) 



  if (mode == "voice"):
    cv2.rectangle(frame,(0,0),(width,height),(0,0,0),130)
    cv2.putText(frame, "Listening", (5, 30), fontCv, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
      print("Say something!")
      # r.adjust_for_ambient_noise(source)
      audio = r.listen(source)
    # recognize speech using Sphinx
    try:
        #print("Sphinx thinks you said " + r.recognize_sphinx(audio))
        word= r.recognize_google(audio)
        print("You said " + word)
        if (word == "face"):
          mode = "face"
          speak("Switching mode to " + mode)
        if (word == "object"):
          mode = "object"
          speak("Switching mode to " + mode)
        if (word == "clear"):
          mode = "none"
          speak("Switching mode to " + mode)
        if (word == "stop"):
          
          speak("Stopping glasses")
          break
    except sr.UnknownValueError:
        print("I could not understand you")
        speak("I could not understand you")
    except sr.RequestError as e:
        print("Sphinx error; {0}".format(e))

  if (mode == "object"):
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (size, size)),
      0.007843, (size, size), 127.5)

    # pass the blob through the network and obtain the detections and
    # predictions
    net.setInput(blob)
    detections = net.forward()
      # loop over the detections
    for i in np.arange(0, detections.shape[2]):
      # extract the confidence (i.e., probability) associated with
      # the prediction
      confidence = detections[0, 0, i, 2]

      # filter out weak detections by ensuring the `confidence` is
      # greater than the minimum confidence
      if confidence > 0.2:
        # extract the index of the class label from the
        # `detections`, then compute the (x, y)-coordinates of
        # the bounding box for the object
        idx = int(detections[0, 0, i, 1])
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")

        # draw the prediction on the frame
        label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
        cv2.rectangle(frame, (startX, startY), (endX, endY), COLORS[idx], 2)
        y = startY - 15 if startY - 15 > 15 else startY + 15
        cv2.putText(frame, label, (startX, y),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
        new = CLASSES[idx]
        if (old != new):
          old = new
          speak(new)          

  if (mode == "face"):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    #####Face processing
    if(len(faces)>0):
      print("Found {} faces".format(str(len(faces))))

      for (x,y,w,h) in faces:
        
        gray = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
        
        gender = ""
        age = ""
        # cv2.putText(gray,'Person',(x, y-10), fontCv, 0.2, (255,255,255), 2, cv2.LINE_AA)


        face_img = frame[y:y+h, h:h+w].copy()
        blob = cv2.dnn.blobFromImage(face_img, 1, (227, 227), MODEL_MEAN_VALUES, swapRB=False)


        gender_net.setInput(blob)
        gender_preds = gender_net.forward()
        gender = gender_list[gender_preds[0].argmax()]
        print("Gender : " + gender)

        age_net.setInput(blob)
        age_preds = age_net.forward()
        age = age_list[age_preds[0].argmax()]
        print("Age Range: " + age)

        overlay_text = "%s %s" % (gender, age)

        # overlay_text = "test"
        cv2.putText(frame, overlay_text, (x, y), fontCv, 0.3, (255, 255, 255), 1, cv2.LINE_AA)
        if (old != gender):
          old = gender
          speak(gender)
        #####Face processing
  ####OpenCV

  ####Display

  draw.rectangle((0, 0, width, height), outline=0, fill=0)

  ####Display

  ####Button
  if not GPIO.input(BUTTON_GPIO):
    if not pressed:
        print("Button pressed!")
        pressed = True
        cv2.rectangle(frame,(0,0),(width,height),(0,0,0),130)
        cv2.putText(frame, "Listening", (5, 30), fontCv, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        speak("Listening")
        mode = "voice"
    # button not pressed (or released)
    else:
        pressed = False
  ####Button

  # FPS Calculate
  new_frame_time = time.time()
  fps = 1/(new_frame_time-prev_frame_time) 
  prev_frame_time = new_frame_time 
  fps = int(fps) 
  fps = str(fps) 
  # cv2.putText(frame, "FPS: " + fps, (5, 25), fontCv, 0.3, (255, 255, 255), 1, cv2.LINE_AA) 
  print("Fps: "+str(fps))
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
