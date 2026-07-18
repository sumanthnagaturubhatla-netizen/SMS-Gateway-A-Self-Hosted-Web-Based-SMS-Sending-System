import subprocess
import json
import time
import sys

# ============================================
# CONFIGURATION — EDIT THESE VALUES
# ============================================
SERVER_URL = "http://192.168.1.100:8000"  # ← Change to your PC's IP address
API_KEY = "your-secret-key-change-this-2024"  # ← Must match Django settings
POLL_INTERVAL = 10  # seconds between checks
# ============================================

HEADERS_GET = f'-H "X-API-Key: {API_KEY}"'
HEADERS_POST = f'-H "X-API-Key: {API_KEY}" -H "Content-Type: application/json"'


def log(msg):
    """Print timestamped log message."""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")


def fetch_pending_sms():
    """Fetch pending SMS from Django server."""
    try:
        cmd = f'curl -s {HEADERS_GET} "{SERVER_URL}/api/pending-sms/"'
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=15
        )

        if result.returncode != 0:
            log(f"❌ Failed to connect to server: {result.stderr}")
            return []

        data = json.loads(result.stdout)

        if isinstance(data, dict) and "error" in data:
            log(f"❌ API Error: {data['error']}")
            return []

        return data

    except json.JSONDecodeError:
        log(f"❌ Invalid response from server")
        return []
    except subprocess.TimeoutExpired:
        log("❌ Connection timed out")
        return []
    except Exception as e:
        log(f"❌ Error fetching SMS: {e}")
        return []


def send_sms_via_termux(phone_number, message):
    """Send SMS using Termux:API (uses the phone's SIM card)."""
    try:
        cmd = [
            "termux-sms-send",
            "-n", phone_number,
            message
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            return True, ""
        else:
            return False, result.stderr.strip() or "Unknown error"

    except subprocess.TimeoutExpired:
        return False, "SMS send timed out"
    except FileNotFoundError:
        return False, "termux-sms-send not found. Install Termux:API app and termux-api package."
    except Exception as e:
        return False, str(e)


def update_status(sms_id, status, error_message=""):
    """Report SMS status back to Django server."""
    try:
        payload = json.dumps({
            "id": sms_id,
            "status": status,
            "error_message": error_message
        })

        cmd = f"""curl -s -X POST {HEADERS_POST} -d '{payload}' "{SERVER_URL}/api/update-status/" """
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=15
        )

        if result.returncode == 0:
            response = json.loads(result.stdout)
            return response.get("success", False)

        return False

    except Exception as e:
        log(f"⚠️  Could not update status for SMS #{sms_id}: {e}")
        return False


def process_pending_sms():
    """Main processing loop — fetch, send, report."""
    pending = fetch_pending_sms()

    if not pending:
        return 0

    log(f"📬 Found {len(pending)} pending SMS")

    sent_count = 0

    for sms in pending:
        sms_id = sms.get("id")
        receiver = sms.get("receiver_number", "")
        message = sms.get("message", "")

        log(f"📤 Sending SMS #{sms_id} to {receiver}...")

        # Mark as "Sending"
        update_status(sms_id, "Sending")

        # Send via SIM card
        success, error = send_sms_via_termux(receiver, message)

        if success:
            log(f"✅ SMS #{sms_id} sent successfully to {receiver}")
            update_status(sms_id, "Sent")
            sent_count += 1
        else:
            log(f"❌ SMS #{sms_id} failed: {error}")
            update_status(sms_id, "Failed", error)

        # Small delay between SMS to avoid carrier throttling
        time.sleep(2)

    return sent_count


def main():
    """Entry point — runs the polling loop."""
    print("=" * 50)
    print("  📩 SMS Gateway — Android Bridge")
    print("=" * 50)
    print(f"  Server:   {SERVER_URL}")
    print(f"  Interval: {POLL_INTERVAL}s")
    print("=" * 50)
    print()

    # Test connection first
    log("🔗 Testing connection to server...")
    test = fetch_pending_sms()
    if test is not None:
        log("✅ Connected to server successfully!")
    else:
        log("⚠️  Could not connect. Check SERVER_URL and make sure Django is running.")

    print()
    log("🔄 Starting polling loop... (Ctrl+C to stop)")
    print()

    total_sent = 0

    try:
        while True:
            count = process_pending_sms()
            total_sent += count

            if count > 0:
                log(f"📊 Session total: {total_sent} SMS sent")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print()
        log(f"🛑 Gateway stopped. Total SMS sent this session: {total_sent}")
        sys.exit(0)


if __name__ == "__main__":
    main()
