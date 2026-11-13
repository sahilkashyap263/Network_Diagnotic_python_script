"""Core network diagnostic checks for the Network Troubleshooting Toolkit.

These checks perform one user-requested lookup/connection at a time. They are
intended for troubleshooting systems you own or have permission to test.
"""

from __future__ import annotations

import platform
import re
import socket
import subprocess
import time
import ssl
import certifi
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from urllib3 import request


@dataclass
class CheckResult:
    name: str
    status: str  # PASS, FAIL, or WARN
    summary: str
    details: str
    latency_ms: float | None = None
    checked_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _result(
    name: str,
    status: str,
    summary: str,
    details: str,
    started: float | None = None,
) -> CheckResult:
    elapsed = (time.perf_counter() - started) * 1000 if started is not None else None
    return CheckResult(
        name=name,
        status=status,
        summary=summary,
        details=details,
        latency_ms=round(elapsed, 2) if elapsed is not None else None,
        checked_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )


def validate_host(host: str) -> str:
    """Normalize and validate a hostname or IP address (not a URL)."""
    normalized = host.strip().strip("[]")
    if not normalized:
        raise ValueError("Enter a hostname or IP address.")
    if any(ch.isspace() for ch in normalized) or "/" in normalized or "\\" in normalized:
        raise ValueError("Enter only a hostname or IP address, without a URL path.")
    if len(normalized) > 253:
        raise ValueError("Hostname is too long.")
    return normalized


def dns_lookup(host: str, timeout: float = 4.0) -> CheckResult:
    """Resolve a hostname to IPv4/IPv6 addresses."""
    started = time.perf_counter()
    try:
        host = validate_host(host)
        # getaddrinfo uses the operating system resolver. The timeout is
        # enforced at the UI/process level in normal local use; resolver-level
        # timeouts are platform-specific.
        records = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
        addresses = sorted({record[4][0] for record in records})
        if not addresses:
            return _result("DNS lookup", "FAIL", "No addresses returned", f"No A/AAAA records were returned for {host}.", started)
        address_lines = "\n".join(f"• {address}" for address in addresses)
        return _result("DNS lookup", "PASS", f"Resolved {host} to {len(addresses)} address(es)", address_lines, started)
    except (ValueError, socket.gaierror, OSError) as exc:
        return _result("DNS lookup", "FAIL", f"Could not resolve {host!r}", str(exc), started)


def ping_host(host: str, timeout_seconds: int = 4) -> CheckResult:
    """Send one ICMP echo request using the OS ping utility."""
    started = time.perf_counter()
    try:
        host = validate_host(host)
        system = platform.system().lower()
        if system == "windows":
            command = ["ping", "-n", "1", "-w", str(timeout_seconds * 1000), host]
        elif system == "darwin":
            command = ["ping", "-c", "1", "-W", str(timeout_seconds * 1000), host]
        else:
            command = ["ping", "-c", "1", "-W", str(timeout_seconds), host]

        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds + 2,
            check=False,
        )
        output = (completed.stdout or "") + (completed.stderr or "")
        output = output.strip()
        if completed.returncode == 0:
            match = re.search(r"time[=<]\s*([0-9.]+)\s*ms", output, re.IGNORECASE)
            latency = float(match.group(1)) if match else None
            result = _result(
                "Ping",
                "PASS",
                f"{host} replied to ICMP echo",
                output[-700:] if output else "Ping completed successfully.",
                started,
            )
            if latency is not None:
                result.latency_ms = round(latency, 2)
            return result

        return _result(
            "Ping",
            "FAIL",
            f"No ping reply from {host}",
            (output[-700:] if output else "The ping command returned a non-zero exit code.")
            + "\nNote: some networks and hosts block ICMP; this alone does not prove the host is offline.",
            started,
        )
    except FileNotFoundError:
        return _result("Ping", "WARN", "Ping utility not found", "Install/enable the operating system ping utility, or use the DNS and TCP checks instead.", started)
    except subprocess.TimeoutExpired:
        return _result("Ping", "FAIL", f"Ping timed out for {host}", f"No response within approximately {timeout_seconds} seconds. ICMP may be filtered.", started)
    except (ValueError, OSError) as exc:
        return _result("Ping", "FAIL", f"Could not ping {host!r}", str(exc), started)


def tcp_port_check(host: str, port: int, timeout: float = 3.0) -> CheckResult:
    """Attempt one TCP connection to a specific host and port."""
    started = time.perf_counter()
    try:
        host = validate_host(host)
        port = int(port)
        if not 1 <= port <= 65535:
            raise ValueError("Port must be between 1 and 65535.")
        with socket.create_connection((host, port), timeout=timeout):
            pass
        return _result(
            "TCP port check",
            "PASS",
            f"TCP connection to {host}:{port} succeeded",
            f"A TCP connection was established on port {port}.",
            started,
        )
    except (ValueError, OSError, OverflowError) as exc:
        return _result(
            "TCP port check",
            "FAIL",
            f"TCP connection to {host}:{port} failed",
            f"{type(exc).__name__}: {exc}\nCheck the hostname, port, firewall rules, and whether the service is listening.",
            started,
        )


def http_check(url: str, timeout: float = 5.0) -> CheckResult:
    """Make a lightweight HTTP HEAD request and report the response code."""
    started = time.perf_counter()
    try:
        parsed = urlparse(url.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("Enter a complete URL beginning with http:// or https://")

        request = Request(
            url.strip(),
            method="HEAD",
            headers={"User-Agent": "NetworkTroubleshootingToolkit/1.0"},
        )
        try:
            ssl_context = ssl.create_default_context(cafile=certifi.where())

            with urlopen(request, timeout=timeout, context=ssl_context) as response:
                code = response.status
                reason = getattr(response, "reason", "")
        except HTTPError as exc:
            # An HTTP error response still proves that the web server replied.
            code = exc.code
            reason = exc.reason

        if 200 <= code < 500:
            status = "PASS"
            summary = f"HTTP server responded with {code}"
        else:
            status = "WARN"
            summary = f"HTTP server returned {code}"
        return _result(
            "HTTP check",
            status,
            summary,
            f"URL: {url.strip()}\nHTTP status: {code} {reason}\nA 4xx response still confirms that an HTTP server was reached; inspect the URL or access permissions.",
            started,
        )
    except (ValueError, URLError, TimeoutError, OSError) as exc:
        return _result("HTTP check", "FAIL", "Could not get an HTTP response", f"{type(exc).__name__}: {exc}", started)


def run_diagnostics(
    host: str,
    port: int,
    url: str,
    selected_checks: set[str],
) -> list[CheckResult]:
    """Run only the checks selected by the user."""
    results: list[CheckResult] = []
    if "DNS" in selected_checks:
        results.append(dns_lookup(host))
    if "Ping" in selected_checks:
        results.append(ping_host(host))
    if "TCP" in selected_checks:
        results.append(tcp_port_check(host, port))
    if "HTTP" in selected_checks:
        results.append(http_check(url))
    return results
