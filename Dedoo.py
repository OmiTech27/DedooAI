import pyttsx3
import speech_recognition as sr
import google.generativeai as genai
import datetime
import requests  # Import for weather API
import re

# Replace with your actual Gemini API key
GENENI_API_KEY = "YOUR GEMNINI API KEY"

# Configure Gemini API
genai.configure(api_key=GENENI_API_KEY)

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-GB_HAZEL_11.0')
    print("")
    print(f"==> Dedoo AI: {text}")
    print("")
    engine.say(text=text)
    engine.runAndWait()

def get_user_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening....")
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source, 0, 5)

    try:
        query = recognizer.recognize_google(audio, language="en").lower()
        print("You said:", query)
        return query
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Request failed: {e}")
        return None

def handle_user_intent(user_input):
    words_to_check = ["time", "today", "what is the time", "what is your name", "name", "who are you"]
    if any(word in user_input.lower() for word in words_to_check):
        now = datetime.datetime.now().strftime("%I:%M %p")
        today = datetime.date.today().strftime("%d/%m/%Y")
        if "time" in user_input.lower():
            speak(f"Current time in India is {now}")
        elif "today" in user_input.lower():
            speak(f"Today's date is {today}")
        else:
            speak("My name is Dedoo AI. Developed by Omkar Khandare using Gemini API")

    elif "weather" in user_input.lower() and ("current" in user_input.lower() or "today" in user_input.lower()):
        # Extract city name from user input (assuming simple format)
        city_name = user_input.lower().split("in")[-1].strip()
        # Use a weather API (replace with your preferred API and API key)
        api_key = "YOUR OPENWAETHER API KEY"  # Replace with your API key
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            # Extract weather information (modify based on API response structure)
            temperature = data["main"]["temp"]
            weather_description = data["weather"][0]["description"]
            speak(f"The current weather in {city_name} is {temperature} degrees Celsius with {weather_description}.")
        else:
            speak(f"Sorry, I couldn't find weather information for {city_name}.")

    elif "day" in user_input.lower() and "date" in user_input.lower():
        # Extract date from user input using regular expression
        date_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', user_input)
        if date_match:
            day, month, year = map(int, date_match.groups())
            # Calculate day of the week
            day_of_week = datetime.datetime(year, month, day).strftime('%A')
            speak(f"The day on {day}/{month}/{year} is {day_of_week}.")
        else:
            speak("Sorry, I couldn't understand the date.")

    elif not user_input.lower() in ["exit", "goodbye","bye", "quit","stop","bye-bye"]:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(user_input, stream=True, generation_config=genai.types.GenerationConfig(
            candidate_count=1,
            stop_sequences=['.'],
            max_output_tokens=40,
            top_p=0.6,
            top_k=5,
            temperature=0.8))
        for chunk in response:
            print("_" * 80)
            speak(chunk.text)

    else:
        speak("Goodbye! It was nice talking to you")
        exit(0)

def main():
    speak("Hello Omkar! How can I assist you?")
    while True:
        user_input = get_user_input()
        if user_input:
            handle_user_intent(user_input)

if __name__ == "__main__":
    main()
