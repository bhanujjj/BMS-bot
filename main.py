import asyncio
import requests
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os

# 🔧 Load environment variables
load_dotenv()

# 🎯 CONFIG
BMS_URL = "https://in.bookmyshow.com/movies/mumbai/f1-the-movie-4dx/buytickets/ET00450715/20250723"
TARGET_CINEMA = "PVR: Infiniti, Malad Mumbai"
CHECK_INTERVAL = 840  # 14 minutes (Render Free tier safe)

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_WHATSAPP_NUMBER = os.getenv("FROM_WHATSAPP_NUMBER")
TO_WHATSAPP_NUMBER = os.getenv("TO_WHATSAPP_NUMBER")

# ✅ Send WhatsApp Alert
async def send_whatsapp_alert():
    print("✅ Sending WhatsApp alert...")
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
    payload = {
        "From": FROM_WHATSAPP_NUMBER,
        "To": TO_WHATSAPP_NUMBER,
        "Body": (
            "🎬 F1 Tickets Alert!\n\n"
            f"✅ {TARGET_CINEMA} (4DX) is now available!\n"
            f"🎟️ Book Now: {BMS_URL}"
        )
    }

    try:
        response = requests.post(url, data=payload, auth=(TWILIO_SID, TWILIO_AUTH_TOKEN))
        print("📩 Twilio Response:", response.status_code)
        if response.status_code == 201:
            print("✅ WhatsApp message sent successfully!")
        else:
            print("⚠️ Failed to send WhatsApp message:", response.text)
    except Exception as e:
        print("❌ Exception while sending WhatsApp message:", str(e))

# 🔍 Check if target cinema is available
async def check_tickets():
    print("🌐 Launching browser...")
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            java_script_enabled=True,
            locale="en-US"
        )

        await context.add_init_script("""Object.defineProperty(navigator, 'webdriver', {get: () => undefined})""")
        page = await context.new_page()

        try:
            print("🌐 Opening BMS page...")
            await page.goto(BMS_URL, timeout=60000)
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(5000)

            print(f"🔍 Looking for cinema: {TARGET_CINEMA}")
            content = await page.content()

            if TARGET_CINEMA.lower() in content.lower():
                print("✅ Target cinema found!")
                await send_whatsapp_alert()
                return True
            else:
                print("❌ Cinema not found in page.")
                return False

        except Exception as e:
            print(f"❌ Error during check: {str(e)}")
            return False
        finally:
            await browser.close()

# 🔁 Main Loop
async def run_bot():
    while True:
        print("\n⏳ Checking again...")
        found = await check_tickets()
        if found:
            break
        print(f"⏰ Waiting {CHECK_INTERVAL} seconds before next check...\n")
        await asyncio.sleep(CHECK_INTERVAL)

# 🚀 Start Bot
if __name__ == "__main__":
    asyncio.run(run_bot())