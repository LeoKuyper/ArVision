import speech_recognition as sr

r = sr.Recognizer()

print(sr.Microphone.list_microphone_names())

mic = sr.Microphone(device_index=0)

with mic as source:
    audio = r.listen(source)
    print(audio)


# harvard = sr.AudioFile('harvard.wav')
# with harvard as source:
#     audio = r.record(source)

type(audio)
print('Test sound')
print(r.recognize_google(audio))