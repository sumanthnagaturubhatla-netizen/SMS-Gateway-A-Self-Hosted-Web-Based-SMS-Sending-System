Self-Hosted Web-Based SMS Sending System 📱💬
A self-hosted, web-based SMS Gateway application that turns any Android smartphone into a programmable SMS transmitter. This system offers a cost-effective alternative to paid SMS APIs by bridging a web control panel on a PC directly to a phone's SIM card over a local Wi-Fi network.

It supports two modes of operation:

Direct HTTP Server Mode: Interacts directly with the "Simple SMS Gateway" app running a web server on the phone.
Termux:API Client Mode: Runs a lightweight background daemon on the Android device via Termux to poll the server for pending SMS and send them via termux-sms-send.
🚀 Key Features
Django Web Dashboard: Modern, intuitive web dashboard to send messages, manage logs, monitor transmission states, and view details/errors.
Dual-Integration Support:
Simple SMS Gateway App: Instantly connect to the Android app hosting a local web server at http://<phone-ip>:8080 over Wi-Fi (No cables or terminal setups required).
Termux Daemon (sms_gateway.py): Periodically polls the server's API (/api/pending-sms/) using an API key and dispatches them locally using termux-sms-send.
Robust Status Tracking: Logs message status values (Pending, Sending, Sent, Failed) with error capturing, sending times, and transmission retry attempts.
API Security: Secure communication between the client daemon and the server via custom header API keys (X-API-Key).
🛠️ Technology Stack
Server/Backend: Python (Django Web Framework)
Client Daemon: Python, curl, Termux + Termux:API (for Android side)
Database: SQLite
Frontend: HTML5, CSS3, JavaScript
⚙️ Setup & Installation
Server Setup (PC / Server)
Activate Virtual Environment:
cd E:\djangoproject\messenger
.\venv\Scripts\Activate.ps1
Install Dependencies:
pip install -r requirements.txt
Configure Settings: Open config/settings.py and set your preferred SMS_GATEWAY_URL or configuration key.
Run Migrations:
python manage.py migrate
Run Development Server:
python manage.py runserver 0.0.0.0:8000
(Note: Binding to 0.0.0.0 ensures the server is reachable by the Android device on the same local network).
📲 Client Configuration (Android Device)
Option A: Using the "Simple SMS Gateway" App
Install Simple SMS Gateway (or equivalent local gateway app) on your Android device.
Turn on the server inside the app (ensure it is green/running).
Ensure both the Android device and your PC are connected to the same Wi-Fi network.
Configure the server IP and port (e.g., http://<phone-ip>:8080) in the Django admin dashboard or settings.py.
Option B: Using Termux (Advanced Command Line Client)
Install Termux and the Termux:API app on your Android device.
Open Termux and run the following setup commands:
pkg update && pkg upgrade
pkg install termux-api python
Copy android_gateway/sms_gateway.py to your phone.
Open the script and edit configuration variables:
SERVER_URL = "http://<YOUR_PC_IP>:8000"
API_KEY = "your-secret-key-change-this-2024"
POLL_INTERVAL = 10
Run the background daemon script in Termux:
python sms_gateway.py
📊 Database Schema Details
SMS: Keeps record of each SMS transaction:
sender_number: Number of the originator.
receiver_number: Destination phone number.
message: Text message content.
status: Current status (Pending, Sending, Sent, Failed).
attempts: Number of retry attempts.
error_message: Logs exceptions or network failures.
sent_at: Timestamp showing when it was successfully delivered.
