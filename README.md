# Self-Hosted Web-Based SMS Sending System 📱💬

A self-hosted, web-based SMS Gateway application that turns any Android smartphone into a programmable SMS transmitter. This system offers a cost-effective alternative to paid SMS APIs by bridging a web control panel on a PC directly to a phone's SIM card over a local Wi-Fi network.

---

## 📂 Repository Structure

The project is structured as follows:

```text
.
├── README.md               # This root documentation file
└── messenger/              # The Django project folder containing all backend/client code
    ├── manage.py
    ├── requirements.txt    # Project Python dependencies
    ├── android_gateway/    # Client daemon for Android Termux integration
    │   └── sms_gateway.py
    ├── chat/               # App handling messaging, views, models, and WebSocket connections
    └── config/             # Django project configuration settings
```

---

## 🚀 Key Features

* **Django Web Dashboard:** Modern, intuitive web dashboard to send messages, manage logs, monitor transmission states, and view details/errors.
* **Dual-Integration Support:**
  * **Simple SMS Gateway App:** Instantly connect to the Android app hosting a local web server at `http://<phone-ip>:8080` over Wi-Fi (No cables or terminal setups required).
  * **Termux Daemon (`sms_gateway.py`):** Periodically polls the server's API (`/api/pending-sms/`) using an API key and dispatches them locally using `termux-sms-send`.
* **Robust Status Tracking:** Logs message status values (`Pending`, `Sending`, `Sent`, `Failed`) with error capturing, sending times, and transmission retry attempts.
* **API Security:** Secure communication between the client daemon and the server via custom header API keys (`X-API-Key`).

---

## 🛠️ Technology Stack

* **Server/Backend:** Python (Django Web Framework)
* **Client Daemon:** Python, `curl`, `Termux` + `Termux:API` (for Android side)
* **Database:** SQLite
* **Frontend:** HTML5, CSS3, JavaScript

---

## ⚙️ Setup & Installation

### Server Setup (PC / Server)

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/sumanthnagaturubhatla-netizen/SMS-Gateway-A-Self-Hosted-Web-Based-SMS-Sending-System.git
   cd SMS-Gateway-A-Self-Hosted-Web-Based-SMS-Sending-System/messenger
   ```
2. **Set Up & Activate Virtual Environment:**
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Settings:**
   Open `config/settings.py` and set your preferred `SMS_GATEWAY_URL` or configuration key.
5. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```
6. **Run Development Server:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
   *(Note: Binding to `0.0.0.0` ensures the server is reachable by the Android device on the same local network).*

---

## 📲 Client Configuration (Android Device)

### Option A: Using the "Simple SMS Gateway" App
1. Install **Simple SMS Gateway** (or equivalent local gateway app) on your Android device.
2. Turn on the server inside the app (ensure it is green/running).
3. Ensure both the Android device and your PC are connected to the **same Wi-Fi network**.
4. Configure the server IP and port (e.g., `http://<phone-ip>:8080`) in the Django admin dashboard or `settings.py`.

### Option B: Using Termux (Advanced Command Line Client)
1. Install **Termux** and the **Termux:API** app on your Android device.
2. Open Termux and run the following setup commands:
   ```bash
   pkg update && pkg upgrade
   pkg install termux-api python
   ```
3. Copy `android_gateway/sms_gateway.py` to your phone.
4. Open the script and edit configuration variables:
   ```python
   SERVER_URL = "http://<YOUR_PC_IP>:8000"
   API_KEY = "your-secret-key-change-this-2024"
   POLL_INTERVAL = 10
   ```
5. Run the background daemon script in Termux:
   ```bash
   python sms_gateway.py
   ```
