# Server Log Analyzer

A full-stack web application for analyzing HTTP server logs. It parses log files and displays request activity, errors, endpoint performance, and latency metrics through a dashboard.

## Features

- Upload and analyze server log files
- Live log monitoring with WebSockets
- Supports JSON, Nginx/Apache, and custom log formats
- Tracks HTTP status codes and error rates
- Shows endpoint-level performance
- Calculates average, P50, P95, P99, and max latency
- Displays request and status code charts
- Detects slow requests and server errors

## Tech Stack

- **Backend:** Python, FastAPI
- **Frontend:** HTML, CSS, JavaScript
- **Charts:** Chart.js
- **Real-Time Updates:** WebSockets

## Setup

Clone the repository:

```bash
git clone https://github.com/AadiDaksh/server-log-analyzer.git
cd server-log-analyzer
```

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
pip install -r requirements.txt
```

Run the application:

```bash
uvicorn backend.app:app --reload
```

Open `http://127.0.0.1:8000` in your browser.

## Testing

Run the tests with:

```bash
python -m unittest discover tests
```

## Project Structure

```text
server-log-analyzer/
├── backend/
│   ├── parsers/
│   ├── analyzer.py
│   ├── app.py
│   └── live_monitor.py
├── frontend/
├── logs/
├── tests/
├── requirements.txt
└── README.md
```

## Future Improvements

- Monitor logs from other applications
- Configurable live log sources
- Filtering and searching logs
- Support for additional log formats