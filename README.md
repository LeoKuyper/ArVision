### 1 INTRODUCTION
I was tasked to create an AI-based project that would have a positive social impact,
with a "wow-factor". I had the freedom to use any platform or system that I wanted to
essentially.
Smart Glasses was created through Python3 and OpenCV. The system aims to help
people with visual impairments. Through giving voice feedback based on the mode
the user has selected.

### 2. CONCEPT (FEATURES + FUNCTIONS)
For this project, I decided to use ArGlasses which was a project I did for Wearable
Tech in a previous term. I felt there was more potential I wasn’t able to achieve the
last time, with this brief I was allowed to further explore the technologies I could use.
That is when ‘Smart Glasses’ came into existence.

1. Core Functionality
● Help people that are Visually Impaired
● Help people with Prosopagnosia (Face Blindness)
● Face detection with attributes
● Scene detection
● OCR (Text recognition)

2. Additional Functionality
● Voice recognition
● Voice feedback
● On display feedback

3. Potential Future Functionality
● Add Face Recognition - Which would allow the system to identify specific people
● Build a version without an onboard display which would strictly work with Voice Feedback

### 3. TECHNICAL PLANNING
From the beginning it was apparent that I would need to remake the internals of
ArGlasses which I did, I upgraded the system to a Raspberry Pi 4 Model B. Which
allowed me to use on-device processing rather than offloading it to a server or a PC.
Another consideration was how would people that are visually impaired be able to
‘interface’ with the unit. After some research, I determined that most visually
impaired users would use voice recognition and voice feedback as their main means
of ‘interfacing’.
I experimented with a lot of different libraries to see what would work best on the
Raspberry Pi and how I would in the end connect everything together. After
consulting with my Lecturer I was able to make my finale decision on what
frameworks I wanted to use.
### 4. FINAL OUTCOME AND IMPLEMENTATION
1. Implementation + Testing
My initial intent was to run all of the different recognitions at the same time.
But after my first test it was apparent I would not be able to do just that. I then
decided on splitting the different recognitions into modes, which would allow
the user to switch between them, which was, in the end, a way better design
choice. Voice recognition was also changed to run through Google’s voice
services rather than on-device recognition (Deepspeech). The problem with
the on-device recognition was it was really slowed when it ran with the other
processes which effectively made it unusable.

2. Highlights and Challenges
I really enjoyed learning how image processing works in conjunction with AI.
Python and OpenCV is just an amazing combination of technologies. Working
on a physical device was also fun and challenging especially the design
constraints I had to keep by.
The biggest challenge I had was performance. Which I was able to fix by
implementing a few different things. Firstly by implementing a multithreaded
approach to how OpenCV worked and processed the information, this allowed
OpenCV to use all of the cores available on the Raspberry Pi. Then finally
was implementing a method of skipping frames from the camera feed, which
allowed a more fluid experience.

### 3. Learning
I learned how to use a lot of different libraries on a low powered device and
how to code efficiently while keeping the functionality of the experience.
### 5. CONCLUSION
This was a wonderful experience working with all these different platforms and
libraries. At the beginning of the term, it was hard grasping and connecting
everything together but as time progressed it turned out to be really easy and fun.
I am happy with my end results as it turned out very successful.

