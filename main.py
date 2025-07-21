import time
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
from dotenv import load_dotenv
import os

# ✅ Load credentials from .env
load_dotenv()

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_WHATSAPP_NUMBER = os.getenv("FROM_WHATSAPP_NUMBER")
TO_WHATSAPP_NUMBER = os.getenv("TO_WHATSAPP_NUMBER")

MOVIE_URL = "https://in.bookmyshow.com/mumbai/movies/f1-the-movie/ET00403839"
BOOKING_URL = "https://in.bookmyshow.com/movies/mumbai/f1-the-movie/ET00403839"

def send_whatsapp_alert():
    print("✅ Sending WhatsApp alert...")
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
    payload = {
        "From": FROM_WHATSAPP_NUMBER,
        "To": TO_WHATSAPP_NUMBER,
        "Body": (
            "🎬 F1 Tickets Alert!\n\n"
            "✅ PVR: Infiniti, Malad (4DX) is now available!\n"
            f"🎟️ Book Now: {BOOKING_URL}"
        )
    }
    response = requests.post(url, data=payload, auth=(TWILIO_SID, TWILIO_AUTH_TOKEN))
    print("📩 Response:", response.status_code)
    if response.status_code != 201:
        print("⚠️ Failed to send WhatsApp message:", response.text)

def check_show():
    print("🌐 Checking BMS movie page...")
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(MOVIE_URL, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch page, status: {response.status_code}")
        return False

    soup = BeautifulSoup(response.text, "html.parser")
    page_text = soup.get_text()

    # 🔍 Check for date and theater format
    if "24 Jul" in page_text and "PVR: Infiniti, Malad" in page_text and "4DX" in page_text:
        print("✅ Show FOUND!")
        return True
    else:
        print("🔁 Show not live yet.")
        return False

# 🔁 Main loop
if __name__ == "__main__":
    while True:
        print("\n⏳ Checking again...")
        if check_show():
            send_whatsapp_alert()
            break
        time.sleep(300)  # Retry every 5 minutes