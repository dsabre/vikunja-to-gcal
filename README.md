# Vikunja to GCal

Fetches today's pending tasks from [Vikunja](https://vikunja.io/) and schedules them as sequential events in Google Calendar, starting from the current time.

## How it works

1. **Fetch tasks** — Queries the Vikunja API for tasks that are not done and whose due date is before or equal today, sorted by priority and due date.
2. **Filter** — Keeps only tasks whose description contains a `duration_minutes:<value>` field (minimum duration is 15 minutes).
3. **Schedule** — Creates Google Calendar events one after another, starting from now. Each event begins where the previous one ended. Minimum event duration is 15 minutes.

## Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)
- A running Vikunja instance with API access
- A Google Cloud project with the Calendar API enabled

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/dsabre/vikunja-to-gcal
cd vikunja-to-gcal
uv sync
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```dotenv
# Timezone used for scheduling and datetime formatting
TZ=Europe/Rome

# Vikunja API base URL (e.g. https://your-domain.com/api/v1)
VIKUNJA_BASE_URL=...
# Vikunja API token (generate it from your Vikunja profile settings)
VIKUNJA_TOKEN=...

# Google Calendar ID where events will be created (use "primary" for the default calendar)
GOOGLE_CALENDAR_ID=...
```

### 3. Set up Google Calendar credentials

- Go to the [Google Cloud Console](https://console.cloud.google.com/)
- Enable the **Google Calendar API**
- Create an **OAuth 2.0 Client ID** (type: Desktop app)
- Download the credentials file and save it as `credentials.json` in the project root

On first run, a browser window will open for OAuth authentication. A `token.json` file will be saved locally to avoid re-authenticating on subsequent runs.

## Usage

```bash
uv run main.py
```

## Task format in Vikunja

For a task to be picked up, its description must contain a `duration_minutes` string in description field:

```
duration_minutes:45
```

Tasks without this field are ignored. If the value is less than 15, it is rounded up to 15 minutes.