# Network Troubleshooting Toolkit

A small Python + Streamlit application for basic network troubleshooting. It provides four focused checks:

1. **DNS lookup** — resolves a hostname to IPv4/IPv6 addresses.
2. **Ping** — sends one ICMP echo request using the operating system's `ping` utility.
3. **TCP port check** — attempts one TCP connection to a selected port.
4. **HTTP check** — sends a lightweight HTTP `HEAD` request and reports the response code.

Live results are saved to a local SQLite database and shown in the diagnostic history table.

## Important: local checks vs hosted demo

Network checks run from the machine hosting the Python process. Run this app locally to troubleshoot your own laptop/network. A cloud-hosted public demo can only test connectivity from the cloud server, not from each visitor's device.

For that reason, live checks are **disabled by default**. The app displays clearly labelled sample results in demo mode. Do not enable live probes on a public deployment unless you have added suitable access controls and abuse protections.

## Requirements

- Python 3.10 or newer
- `pip`
- The operating system's `ping` utility for the Ping feature

## Run locally

### 1. Create and activate a virtual environment

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Enable live checks and start the app

**Windows PowerShell**

```powershell
$env:ENABLE_LIVE_CHECKS="1"
python -m streamlit run app.py
```

**macOS / Linux**

```bash
ENABLE_LIVE_CHECKS=1 python -m streamlit run app.py
```

Open the local address printed in the terminal (usually `http://localhost:8501`).

To run the sample-data demo instead, leave `ENABLE_LIVE_CHECKS` unset.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Deploy a safe public demo

1. Push this project to a GitHub repository.
2. In Streamlit Community Cloud, create an app from that repository and select `app.py` as the entry point.
3. Keep `ENABLE_LIVE_CHECKS` unset (or set it to `0`) so the deployed app remains in sample-data demo mode.

The public demo is for showing the interface and workflow. Use the local mode for actual diagnostics from your own network.

## Limitations

- ICMP may be blocked by a firewall even when DNS, TCP or HTTP works.
- A successful TCP check confirms that a connection was accepted; it does not prove that the application behind the port is functioning correctly.
- The HTTP check uses `HEAD`; some websites do not support it or may return different results for automated requests.
- DNS response timing includes local resolver/cache behavior.
- This is a learning/portfolio project, not a replacement for enterprise monitoring or an incident-management platform.

## Suggested resume description

**Network Troubleshooting Toolkit | Python, Streamlit, Socket Programming, SQLite**

- Developed a Python-based diagnostic dashboard to check DNS resolution, ICMP reachability, TCP port connectivity and HTTP endpoint responses.
- Used Python sockets and subprocess calls to perform connectivity checks and summarize common failure conditions.
- Added a Streamlit interface and SQLite-backed history to review previous diagnostic results.

Only include these bullets after you have run the app, tested the checks and can explain how each one works.

## Interview explanation

"I built this project to practise first-level network troubleshooting. I start with DNS to confirm name resolution, use ping as a basic reachability signal, test a specific TCP port to check whether a service accepts connections, and make an HTTP request to inspect the application response. I compare the results rather than relying on ping alone, because ICMP can be filtered. The app records live check results in SQLite so I can review what happened."
