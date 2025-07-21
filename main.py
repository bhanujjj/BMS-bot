import time
from playwright.sync_api import sync_playwright
import requests
from twilio.rest import Client
from dotenv import load_dotenv
import subprocess
import os

# Automatically install Chromium if not already installed
if not os.path.exists("/root/.cache/ms-playwright"):
    subprocess.run(["playwright", "install", "chromium"])

# ✅ Twilio credentials
load_dotenv()  # Load from .env

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_WHATSAPP_NUMBER = os.getenv("FROM_WHATSAPP_NUMBER")
TO_WHATSAPP_NUMBER = os.getenv("TO_WHATSAPP_NUMBER")    # Your number

def send_whatsapp_alert():
    print("✅ Sending WhatsApp alert...")
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
    payload = {
        "From": FROM_WHATSAPP_NUMBER,
        "To": TO_WHATSAPP_NUMBER,
        "Body": (
            "🎬 F1 Tickets Alert!\n\n"
            "✅ PVR: Infiniti, Malad (4DX) is now available!\n"
            "🎟️ Book Now: https://in.bookmyshow.com/movies/mumbai/f1-the-movie/ET00403839"
        )
    }
    response = requests.post(url, data=payload, auth=(TWILIO_SID, TWILIO_AUTH_TOKEN))
    print("📩 Response:", response.status_code)
    if response.status_code != 201:
        print("⚠️ Failed to send WhatsApp message:", response.text)

def check_show():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print("🌐 Visiting movie page...")
            page.goto("https://in.bookmyshow.com/movies/mumbai/f1-the-movie/ET00403839", timeout=60000)

            print("🎟️ Clicking 'Book Tickets'...")
            page.click("text=Book Tickets", timeout=10000)
            page.wait_for_timeout(3000)

            print("📅 Clicking '24 JUL'...")
            try:
                page.click("text=24 JUL", timeout=5000)
            except:
                print("❌ 24 July not available yet.")
                return False

            print("🔍 Scanning show listings...")
            content = page.content()

            if "PVR: Infiniti, Malad" in content and "4DX" in content:
                print("✅ Show FOUND!")
                return True
            else:
                print("🔁 Show not live yet.")
                return False

        except Exception as e:
            print("❌ Error during check:", str(e))
            return False
        finally:
            browser.close()

# 🔁 Main loop
if __name__ == "__main__":
    while True:
        print("\n⏳ Checking again...")
        if check_show():
            send_whatsapp_alert()
            break
        time.sleep(300)  # 5 minutes