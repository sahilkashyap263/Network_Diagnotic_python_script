from __future__ import annotations

import os
from datetime import datetime

import pandas as pd
import streamlit as st

from network_checks import CheckResult, run_diagnostics
from storage import clear_history, initialize_db, read_history, save_results

st.set_page_config(
    page_title="Network Troubleshooting Toolkit",
    page_icon="🌐",
    layout="wide",
)

LIVE_CHECKS_ENABLED = os.getenv("ENABLE_LIVE_CHECKS", "0").strip().lower() in {"1", "true", "yes"}

st.markdown(
    """
    <style>
      .main-title {font-size: 2.1rem; font-weight: 750; letter-spacing: -0.04em;}
      .sub-title {color: #8b949e; margin-top: -0.7rem;}
      div[data-testid="stMetric"] {background: rgba(128,128,128,.07); padding: 12px 14px; border-radius: 12px;}
      .small-note {font-size: .86rem; color: #8b949e;}
    </style>
    """,
    unsafe_allow_html=True,
)

initialize_db()

st.markdown('<div class="main-title">🌐 Network Troubleshooting Toolkit</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">A lightweight diagnostic console for DNS, reachability, TCP services and HTTP endpoints.</div>', unsafe_allow_html=True)
st.write("")

if LIVE_CHECKS_ENABLED:
    st.success("Live diagnostic mode is enabled. Checks run from the computer/server running this app.")
else:
    st.info("Demo mode is active. The public demo displays sample diagnostic output; enable live checks when running locally.")

with st.sidebar:
    st.header("About this project")
    st.caption("Built with Python, Streamlit, sockets, subprocess, urllib and SQLite.")
    st.divider()
    st.subheader("What each check does")
    st.markdown(
        "- **DNS:** resolves a hostname to IP addresses.\n"
        "- **Ping:** sends one ICMP echo request.\n"
        "- **TCP:** tries one connection to a selected port.\n"
        "- **HTTP:** sends a lightweight HEAD request and reads the status code."
    )
    st.divider()
    st.caption("Use this tool only on systems and services you own or are authorized to troubleshoot.")

st.subheader("Run diagnostics")
with st.form("diagnostics_form"):
    col_a, col_b = st.columns([2, 1])
    with col_a:
        host = st.text_input("Target hostname or IP", value="example.com", help="Example: example.com or 1.1.1.1")
    with col_b:
        port = st.number_input("TCP port", min_value=1, max_value=65535, value=443, step=1)
    url = st.text_input("Website URL", value="https://example.com", help="Used by the HTTP check")
    st.markdown("**Choose checks**")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        do_dns = st.checkbox("DNS lookup", value=True)
    with c2:
        do_ping = st.checkbox("Ping", value=True)
    with c3:
        do_tcp = st.checkbox("TCP port", value=True)
    with c4:
        do_http = st.checkbox("HTTP response", value=True)
    submitted = st.form_submit_button("▶ Run diagnostics", type="primary", use_container_width=True)

if submitted:
    selected = {name for name, enabled in [("DNS", do_dns), ("Ping", do_ping), ("TCP", do_tcp), ("HTTP", do_http)] if enabled}
    if not selected:
        st.warning("Select at least one check.")
    elif not host.strip():
        st.warning("Enter a target hostname or IP address.")
    elif not LIVE_CHECKS_ENABLED:
        now = datetime.now().astimezone().isoformat(timespec="seconds")
        demo_map = {
            "DNS": CheckResult("DNS lookup", "PASS", "Resolved example.com to 2 address(es)", "• 93.184.216.34\n• 2606:2800:220:1:248:1893:25c8:1946", 18.4, now),
            "Ping": CheckResult("Ping", "PASS", "example.com replied to ICMP echo", "Demo response: 24 ms\nSample data only; no ICMP packet was sent.", 24.0, now),
            "TCP": CheckResult("TCP port check", "PASS", f"TCP connection to example.com:{int(port)} succeeded", "Sample connection result; no TCP connection was opened.", 32.7, now),
            "HTTP": CheckResult("HTTP check", "PASS", "HTTP server responded with 200", f"URL: {url}\nSample HTTP status: 200 OK\nNo web request was sent.", 45.2, now),
        }
        st.session_state["latest_results"] = [demo_map[key] for key in ["DNS", "Ping", "TCP", "HTTP"] if key in selected]
        st.session_state["demo_results"] = True
    else:
        with st.spinner("Running selected network checks..."):
            results = run_diagnostics(host, int(port), url, selected)
        save_results(results)
        st.session_state["latest_results"] = results
        st.session_state["demo_results"] = False

results: list[CheckResult] = st.session_state.get("latest_results", [])
if results:
    st.divider()
    st.subheader("Latest results")
    if st.session_state.get("demo_results"):
        st.caption("These are illustrative sample results, not live measurements.")
    passed = sum(r.status == "PASS" for r in results)
    failed = sum(r.status == "FAIL" for r in results)
    warnings = sum(r.status == "WARN" for r in results)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Checks run", len(results))
    m2.metric("Passed", passed)
    m3.metric("Failed", failed)
    m4.metric("Warnings", warnings)

    for result in results:
        icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}.get(result.status, "ℹ️")
        with st.expander(f"{icon} {result.name} — {result.summary}", expanded=True):
            left, right = st.columns([3, 1])
            with left:
                st.write(result.details)
            with right:
                if result.latency_ms is not None:
                    st.metric("Elapsed / reported time", f"{result.latency_ms:.2f} ms")
                st.caption(result.checked_at)

st.divider()
st.subheader("Diagnostic history")
history = read_history(limit=30)
if history:
    history_df = pd.DataFrame(history)
    history_df = history_df.rename(
        columns={
            "checked_at": "Timestamp (UTC)",
            "check_name": "Check",
            "status": "Status",
            "summary": "Summary",
            "details": "Details",
            "latency_ms": "Elapsed (ms)",
        }
    )
    st.dataframe(history_df, use_container_width=True, hide_index=True)
    if st.button("Clear local history"):
        clear_history()
        st.rerun()
else:
    st.caption("No live checks saved yet. Results from demo mode are intentionally not stored.")

st.caption("Note: Ping can fail even when a service is healthy because ICMP is sometimes filtered. Compare DNS, TCP and HTTP results before concluding that a host is down.")
