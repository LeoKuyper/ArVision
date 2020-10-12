import imutils
import numpy as np
import cv2
import time 

cap = cv2.VideoCapture('http://192.168.1.250:8080/?action=stream')

MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
font = cv2.FONT_HERSHEY_SIMPLEX

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

while True:
  
  ret, frame = cap.read()
  if not ret: 
    break

  frame = imutils.resize(frame, width=800)

  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  faces = face_cascade.detectMultiScale(gray, 1.3, 5)

  if(len(faces)>0):
   print("Found {} faces".format(str(len(faces))))

  for (x,y,w,h) in faces:
    gray = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
    
    
    # cv2.putText(gray,'FACE',(x, y-10), font, 0.5, (11,255,255), 2, cv2.LINE_AA)
    # roi_gray = gray[y:y+h, x:x+w]

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
    cv2.putText(frame, overlay_text, (x, y), font, 1, (255, 255, 255), 2, cv2.LINE_AA)


  # FPS Calculate
  new_frame_time = time.time()
  fps = 1/(new_frame_time-prev_frame_time) 
  prev_frame_time = new_frame_time 
  fps = int(fps) 
  fps = str(fps) 
  cv2.putText(frame, "FPS: " + fps, (2, 30), font, 1, (255, 255, 255), 3, cv2.LINE_AA) 
  cv2.imshow('Video', frame)
  
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

cap.release()
cv2.destroyAllWindows() 
