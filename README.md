# Network Troubleshooting Toolkit

A Python-based network diagnostics application built with Streamlit. It helps users perform basic network connectivity checks and view diagnostic results through a simple web interface.

**Live Demo:** https://network-troubleshooting-toolkit.streamlit.app/

**GitHub Repository:** https://github.com/sahilkashyap263/Network_Diagnotic_python_script

---

## Features

- **DNS Lookup:** Resolves hostnames and retrieves IPv4 and IPv6 addresses.
- **Ping Test:** Checks basic network reachability using the operating system's ping utility.
- **TCP Port Check:** Tests whether a TCP connection can be established to a specified host and port.
- **HTTP Check:** Sends an HTTP HEAD request and displays the response status.
- **Diagnostic History:** Stores previous diagnostic results locally using SQLite.
- **Streamlit Dashboard:** Provides a simple interface for running and viewing network checks.
- **Demo Mode:** Allows users to explore the application without performing live network checks.

## Technology Stack

- Python 3.10+
- Streamlit
- Pandas
- SQLite
- Socket Programming
- DNS Resolution
- HTTP Requests
- Unit Testing

## Project Structure

```text
network-troubleshooting-toolkit/
│
├── app.py
├── network_checks.py
├── storage.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
│
└── tests/
    └── test_network_checks.py
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/sahilkashyap263/Network_Diagnotic_python_script.git
```

### 2. Open the project folder

```bash
cd Network_Diagnotic_python_script
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## Running Tests

Run the following command from the project root directory:

```bash
python -m unittest discover -s tests -v
```

## Live Checks and Demo Mode

The application supports a configuration option called `ENABLE_LIVE_CHECKS`.

- When enabled, the application can perform live network diagnostics from the machine running the application.
- When disabled, the application uses demo behavior instead of performing live checks.

For local testing, configure the environment variable in PowerShell:

```powershell
$env:ENABLE_LIVE_CHECKS="true"
streamlit run app.py
```

For demo mode:

```powershell
$env:ENABLE_LIVE_CHECKS="false"
streamlit run app.py
```

**Important:** On a cloud-hosted deployment, live checks run from the cloud server, not from the visitor's personal computer. Live checks should remain disabled by default on a public deployment.

## Deployment

This application can be deployed using Streamlit Community Cloud.

General deployment steps:

1. Push the project to GitHub.
2. Sign in to Streamlit Community Cloud.
3. Connect your GitHub repository.
4. Select `app.py` as the application entry point.
5. Deploy the application.

Live demo: https://network-troubleshooting-toolkit.streamlit.app/

## Limitations

- Ping results depend on operating system support and network configuration.
- Some networks block ICMP traffic.
- Some web servers do not support HTTP HEAD requests.
- A successful TCP connection does not guarantee that the application running on that port is healthy.
- SQLite history is stored locally and may not persist across cloud application restarts.

## Security and Responsible Use

This toolkit is designed for basic troubleshooting and educational purposes.

- Test only systems and networks you own or have permission to troubleshoot.
- Avoid running checks against systems without authorization.
- Public deployments should use demo mode by default.
- The application is not intended to perform vulnerability scanning or security testing.

## Resume Project Description

**Network Troubleshooting Toolkit | Python, Streamlit, SQLite**

- Developed a Python-based network diagnostics application with a Streamlit interface.
- Implemented DNS lookup, ICMP ping, TCP port connectivity checks, and HTTP status checks.
- Integrated SQLite to maintain local diagnostic history.
- Used modular Python code and unit tests to improve maintainability and reliability.
- Deployed the application using Streamlit Community Cloud.

## Interview Explanation

This project demonstrates my understanding of basic networking concepts and Python programming.

I developed a troubleshooting toolkit that helps diagnose common connectivity problems. It performs DNS resolution, ping tests, TCP port connectivity checks, and HTTP response checks.

I used Python socket programming for network connectivity, Streamlit for the user interface, and SQLite for storing diagnostic history. I also included unit tests to verify important functions.

The project helped me understand how DNS, ICMP, TCP, and HTTP work together during network communication.

---

**Author:** Sahil Kashyap

**GitHub:** https://github.com/sahilkashyap263