import pyttsx3
import speech_recognition as sr
from datetime import*

ear = sr.Recognizer()

while True:
   with sr.Microphone() as mic:
      print("I'm listening to you")
      audio = ear.listen(mic)
   print("Brain: ...")

   try:
      you = ear.recognize_google(audio)
   except:
      you = " "
   print('You:', you)

   name = "Will"
   if you == "hello":
      brain = "Hello "+name
   elif you == "good morning":
      brain = "how's it going today!"
   elif you == "today":
      today = date.today()
      brain = today.strftime("%B %d, %Y")
   elif "time" in you:
      now = datetime.now()
      brain = now.strftime("%H:%M:%S")
   elif you == 'bye':
      brain = "have a good one"
      print(brain)
      engine = pyttsx3.init()
      engine.say(brain)
      engine.runAndWait()
      break

   print(brain)
   engine = pyttsx3.init()
   engine.say(brain)
   engine.runAndWait()