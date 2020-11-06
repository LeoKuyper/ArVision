print("Starting ArVision")
import imutils
import multiprocessing
from imutils.video.pivideostream import PiVideoStream
from imutils.object_detection import non_max_suppression
from gpiozero import CPUTemperature
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
import pandas as pd
import getpass
import speech_recognition as sr
import pyttsx3
import RPi.GPIO as GPIO
import spur
import pytesseract
from PIL import Image, ImageDraw, ImageFont, ImageOps
import adafruit_rgb_display.st7735 as st7735 

###### Present Mode
present = True

###### Temp Monitor
def temp():
    cpu = CPUTemperature()
    print("CPU Temp: " + str(cpu.temperature))
    return str(cpu.temperature)

temp()




print("Setting up Voice")
engine = pyttsx3.init()

def speak(text):
    print(text)
    if (present):
        #will play sound on ssh connected mac for demonstration
        shell.spawn(["say", text])
    else:
        engine.say(text)
        engine.runAndWait()


speak("Your Smart Glasses are getting ready")

############# Camera Setup 
print("Warming up Camera")
cap = cv2.VideoCapture(0, cv2.CAP_V4L)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FPS, 20)
cap.set(cv2.CAP_PROP_POS_FRAMES , 1)
cap.set(3,480)
cap.set(4,480)
time.sleep(2)
# cap.set(15, -8.0)

def rescale_frame(frame, percent):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)

print(str(cap.get(3)) + " x " + str(cap.get(4))+ "  Exposure at " + str(cap.get(15)))
############# Camera Setup 

############# Models Setup 
print("Loading models")
MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
fontCv = cv2.FONT_HERSHEY_SIMPLEX
age_list = ['(0, 2)', '(4, 6)', '(8, 12)', '(15, 20)', '(25, 32)', '(38, 43)', '(48, 53)', '(60, 100)']
gender_list = ['Male', 'Female']
age_net = cv2.dnn.readNetFromCaffe('deploy_age.prototxt', 'age_net.caffemodel')
gender_net = cv2.dnn.readNetFromCaffe('deploy_gender.prototxt', 'gender_net.caffemodel')
face_cascade = cv2.CascadeClassifier("face.xml")
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat","bottle", "bus", "car", "cat", "chair", "cow", "table", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "monitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt.txt", "MobileNetSSD_deploy.caffemodel")
############# Models Setup 

############# FPS Setup
prev_frame_time = 0
new_frame_time = 0
############# FPS Setup

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

############# Var Setup 
old = ""
new = ""
checked = ""
mode = "none"
prev_frame_time = 0
new_frame_time = 0
fps = 0
size = 400

counter = 0

age_preds = None
gender_preds = None
detections = None
############# Var Setup 
temp()
speak("Your Smart Glasses are ready")

if (present):
    time.sleep(2)
    speak("Presentation mode is active")
time.sleep(2)

speak("Please select a mode")

while True:
    os.system('cls' if os.name == 'nt' else 'clear')

    ####OpenCV
    ret, frameM = cap.read()
    frame = rescale_frame(frameM, percent=80)
    frame = imutils.resize(frame, width=size)
    frame = cv2.flip(frame, 0) 
    frame = cv2.flip(frame, 2) 
    WFrame = frame

    cv2.putText(frame, "CPU: " + str(temp()), (5, 15), fontCv, 0.5, (255, 255, 255), 1, cv2.LINE_AA)  

    cv2.putText(frame, "Mode: " + mode, (5, 380), fontCv, 1, (255, 255, 255), 1, cv2.LINE_AA) 


    ####Mode selection

    if (mode == "voice"):
        cv2.rectangle(frame,(0,0),(size,size),(0,0,0),400)
        cv2.putText(frame, "Listening", (5, 50), fontCv, 1, (255, 255, 255), 1, cv2.LINE_AA)
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
            counter = 5
            if ("face" in word):
                mode = "face"
                speak("Switching mode to " + mode)
            elif ("object" in word):
                counter = 20
                mode = "object"
                speak("Switching mode to " + mode)
            elif ("read" in word):
                mode = "word"
                speak("Switching mode to reading")
            elif ("add" in word):
                mode = "add"
                speak("Switching mode to " + mode)
            elif ("clear" in word):
                mode = "none"
                speak("Clearing mode")
            elif ("stop" in word):          
                speak("Stopping Smart Glasses")
                time.sleep(2)
                speak("Goodbye")
                break
            else:
                speak("Mode was not found")
        except sr.UnknownValueError:
            speak("I could not understand you")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))


    if (mode == "word"):
        if (counter == 5):
            print("word")
            image = WFrame
            # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        #   image = rescale_frame(image, percent=50)

            gray = image[:, :, 2]
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            gray = cv2.medianBlur(gray, 3)
            # image = cv2.medianBlur(image,5)

            new = pytesseract.image_to_string(gray)
            print(new)
            if (old == new):
                if (checked == old):
                    counter = 0
                else:                    
                    speak(new)
                    counter = 0
                
                checked = old

            old = new
                        
            # time.sleep(1)
            counter = 0
        else:
            counter = counter + 1

    if (mode == "object"):
        if (counter == 20):
            (h, w) = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (size, size)), 0.007843, (size, size), 127.5)

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
                if confidence > 0.7:
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
                    if (old == new):
                        if (checked == old):
                            counter = 0
                        else:                    
                            speak(new)
                            counter = 0
                        
                        checked = old
                    old = new
            counter = 0
        else:
            (h, w) = frame.shape[:2]
            for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the prediction
                confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
                if confidence > 0.7:
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
                    
                    if (old == new):
                        if (checked != old):                 
                            speak(new)                        
                        checked = old
                    old = new
            counter = counter + 1

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

    ####Mode selection


    ####Button
    if not GPIO.input(BUTTON_GPIO):
        if not pressed:
            print("Button pressed!")            
            pressed = True
            cv2.rectangle(frame,(0,0),(size,size),(0,0,0),400)
            cv2.putText(frame, "Listening", (5, 50), fontCv, 1, (255, 255, 255), 1, cv2.LINE_AA)
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
    cv2.putText(frame, "FPS: " + fps, (5, 30), fontCv, 0.5, (255, 255, 255), 1, cv2.LINE_AA) 
    print("Fps: "+str(fps))
    cv2.imshow('Video', frame)
    # FPS Calculate

    # Ar Display    
    image = frame
    color_coverted = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(color_coverted)
    # Scale the image to the smaller screen dimension
    scaled_width = width
    scaled_height = image.height * width // image.width
    image = image.resize((scaled_width, scaled_height), Image.BICUBIC)
    # Crop and center the image
    x = scaled_width // 2 - width // 2
    y = scaled_height // 2 - height // 2
    image = image.crop((x, y, x + width, y + height))
    image = ImageOps.invert(image)
    disp.image(image)
    # Ar Display

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows() 