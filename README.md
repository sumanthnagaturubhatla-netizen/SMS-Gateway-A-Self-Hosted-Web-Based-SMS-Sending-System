# SMS Gateway

A self-hosted, web-based SMS sending system. Send and manage SMS messages through a simple dashboard, backed by your own server and GSM modem or SMS provider — no third-party SaaS required.

## Features

- 📲 **Web dashboard** — send single or bulk SMS messages from your browser
- 🔌 **Pluggable backends** — connect a GSM modem/USB dongle or an HTTP-based SMS provider
- 📇 **Contact & group management** — organize recipients into groups for bulk sends
- 📜 **Message history & delivery status** — track sent, pending, and failed messages
- 🔐 **Self-hosted & private** — your data never leaves your own infrastructure
- 🔑 **REST API** — send messages programmatically from other apps/scripts
- 🧾 **Message templates** — reusable templates with variable placeholders
- ⏱️ **Scheduled sending** — queue messages to go out at a later time

## Requirements

- Node.js 18+ (or specify your actual runtime, e.g. Python 3.10+ / PHP 8+)
- A database (SQLite by default, MySQL/PostgreSQL supported)
- One of:
  - A GSM modem / USB 3G/4G dongle with SIM card, or
  - An account with an SMS gateway provider (e.g. Twilio, Vonage, etc.)

## Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/sms-gateway.git
cd sms-gateway

# Install dependencies
npm install

# Copy and configure environment variables
cp .env.example .env
```

Edit `.env` with your configuration:

```env
PORT=3000
DATABASE_URL=sqlite:./data/sms-gateway.db

# Choose your SMS backend: "modem" or "provider"
SMS_BACKEND=modem

# If using a GSM modem
MODEM_PORT=/dev/ttyUSB0
MODEM_BAUD_RATE=115200

# If using an SMS provider instead
# SMS_PROVIDER_API_KEY=your_api_key
# SMS_PROVIDER_API_SECRET=your_api_secret

# Dashboard auth
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change_me
JWT_SECRET=replace_with_a_long_random_string
```

## Usage

Start the server:

```bash
npm start
```

Then open `http://localhost:3000` in your browser and log in with your admin credentials.

### Sending via the dashboard

1. Go to **Compose**
2. Enter a recipient number or select a contact group
3. Write your message (or pick a template)
4. Click **Send**

### Sending via the API

```bash
curl -X POST http://localhost:3000/api/messages \
  -H "Authorization: Bearer <your_api_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+15551234567",
    "message": "Hello from SMS Gateway!"
  }'
```

Example response:

```json
{
  "id": "msg_abc123",
  "status": "queued",
  "to": "+15551234567",
  "createdAt": "2026-07-18T09:00:00Z"
}
```

## Running with Docker

```bash
docker compose up -d
```

This will start the web app and (if configured) a database container. Ensure your modem device is passed through in `docker-compose.yml` if using `SMS_BACKEND=modem`:

```yaml
devices:
  - "/dev/ttyUSB0:/dev/ttyUSB0"
```

## Project Structure

```
sms-gateway/
├── src/
│   ├── api/          # REST API routes
│   ├── dashboard/    # Web UI
│   ├── backends/     # Modem / provider integrations
│   ├── models/       # Database models
│   └── queue/        # Message queue & scheduler
├── data/              # SQLite DB / persistent data
├── .env.example
├── docker-compose.yml
└── package.json
```

## Roadmap

- [ ] Two-way SMS (receive inbound messages)
- [ ] Webhooks for delivery status updates
- [ ] Multi-user roles & permissions
- [ ] SMPP support for carrier-grade sending

## Contributing

Contributions are welcome! Please open an issue to discuss significant changes before submitting a pull request.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Open a pull request

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer

This project is intended for legitimate personal, business, or notification use cases. You are responsible for complying with local telecommunications regulations and anti-spam laws (e.g. TCPA, GDPR) in the jurisdictions where you send messages.
