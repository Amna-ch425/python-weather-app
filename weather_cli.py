filename="history.json"
import requests
import json
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not API_KEY:
    print("Error: OPENWEATHER_API_KEY environment variable not set.")
    exit(1)



def get_weather(city: str) -> dict:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

def save_history(city: str, data: dict, filename="history.json"):
    entry = {
        "city": city,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data
    }
    try:
        history = json.load(open(filename))
    except (FileNotFoundError, json.JSONDecodeError):
        history = []
    history.append(entry)
    with open(filename, "w") as f:
        json.dump(history, f, indent=2)

def load_history(filename="history.json"):
    try:
        return json.load(open(filename))
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def display_weather(info: dict):
    name = info.get("name")
    weather = info["weather"][0]["description"].capitalize()
    temp = info["main"]["temp"]
    humidity = info["main"]["humidity"]
    print(f"\nWeather for {name}:")
    print(f"  Condition: {weather}")
    print(f"  Temperature: {temp:.1f}°C")
    print(f"  Humidity: {humidity}%\n")

def main():
    args = sys.argv[1:]

    if args and args[0].lower() == "--history":
        hist = load_history()
        if not hist:
            print("No history found.")
        else:
            print("\nLast 5 Searches:")
            for item in hist[-5:]:
                ts = item["timestamp"]
                city = item["city"]
                print(f"{ts} UTC — {city}")
        return

    if not args:
        city = input("Enter a city name: ").strip()
    else:
        city = " ".join(args)

    if not city:
        print("No city provided. Exiting.")
        return

    try:
        info = get_weather(city)
        display_weather(info)
        save_history(city, info)
    except requests.HTTPError as e:
        print(f"Error: Could not retrieve weather for '{city}'. ({e})")

if __name__ == "__main__":
    main()
