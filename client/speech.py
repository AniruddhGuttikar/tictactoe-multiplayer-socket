import pyttsx3

def speech(text):
    # Initialize the text-to-speech engine
    engine = pyttsx3.init()

    # Set properties (optional)
    engine.setProperty('rate', 160)  # Speed of speech

    # Convert the text to speech
    engine.say(text)

    # Wait for the speech to finish
    engine.runAndWait()
 
def praise(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  
    engine.setProperty('rate', 150)  # Speed of speech
    engine.say(text)
    engine.runAndWait()

def con(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  
    engine.setProperty('rate', 150)  # Speed of speech
    engine.say(text)
    engine.runAndWait()