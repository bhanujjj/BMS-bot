const { chromium } = require("playwright");
const dotenv = require("dotenv");
const twilio = require("twilio");

dotenv.config();

const BMS_URL =
  "https://in.bookmyshow.com/movies/mumbai/f1-the-movie-4dx/buytickets/ET00450715/20250723";
const TARGET_CINEMA = "PVR: Infiniti, Malad Mumbai";
const CHECK_INTERVAL = 14 * 60 * 1000; // 14 min in ms

const client = twilio(process.env.TWILIO_SID, process.env.TWILIO_AUTH_TOKEN);

// ✅ Send WhatsApp alert
async function sendWhatsAppAlert() {
  console.log("✅ Sending WhatsApp alert...");

  try {
    const message = await client.messages.create({
      from: process.env.FROM_WHATSAPP_NUMBER,
      to: process.env.TO_WHATSAPP_NUMBER,
      body: `🎬 F1 Tickets Alert!\n\n✅ ${TARGET_CINEMA} (4DX) is now available!\n🎟️ Book Now: ${BMS_URL}`,
    });

    console.log("✅ WhatsApp message sent! SID:", message.sid);
  } catch (err) {
    console.error("❌ Failed to send WhatsApp message:", err.message);
  }
}

// 🔍 Check if target cinema is available
async function checkTickets() {
  console.log("🌐 Launching browser...");

  const browser = await chromium.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });

  const context = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    viewport: { width: 1280, height: 720 },
    locale: "en-US",
  });

  const page = await context.newPage();

  try {
    console.log("🌐 Navigating to BMS...");
    await page.goto(BMS_URL, { timeout: 60000, waitUntil: "networkidle" });
    await page.waitForTimeout(5000); // wait for DOM elements

    const content = await page.content();

    if (content.toLowerCase().includes(TARGET_CINEMA.toLowerCase())) {
      console.log("✅ Target cinema found!");
      await sendWhatsAppAlert();
      return true;
    } else {
      console.log("❌ Cinema not found on page.");
      return false;
    }
  } catch (err) {
    console.error("❌ Error checking tickets:", err.message);
    return false;
  } finally {
    await browser.close();
  }
}

// 🔁 Loop
async function runBot() {
  while (true) {
    console.log("\n🔁 Checking for tickets...");
    const found = await checkTickets();
    if (found) break;

    console.log(`⏱ Waiting ${CHECK_INTERVAL / 1000 / 60} minutes...`);
    await new Promise((res) => setTimeout(res, CHECK_INTERVAL));
  }
}

runBot();