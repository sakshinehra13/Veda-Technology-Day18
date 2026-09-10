import streamlit as st
import re
from collections import deque
from datetime import datetime

# ==========================================
# 1. CORE LOG MONITORING CLASS
# ==========================================
class LogMonitor:
    def __init__(self, threshold=3, time_window=60, pattern=r"ERROR|CRITICAL|FAIL"):
        self.threshold = threshold
        self.time_window = time_window
        self.pattern = re.compile(pattern, re.IGNORECASE)
        
    def evaluate(self, log_line, error_timestamps):
        """Evaluates a log line against the pattern and threshold rules."""
        current_time = datetime.now()
        triggered = False
        
        # Check if pattern matches
        if self.pattern.search(log_line):
            error_timestamps.append(current_time)
            
        # Remove timestamps outside the sliding time window
        while error_timestamps and (current_time - error_timestamps[0]).total_seconds() > self.time_window:
            error_timestamps.popleft()
            
        # Check if error frequency crosses threshold
        if len(error_timestamps) >= self.threshold:
            triggered = True
            
        return triggered, len(error_timestamps)

# ==========================================
# 2. STREAMLIT WEB APP INTERFACE
# ==========================================
st.set_page_config(page_title="Log Monitoring & Alert System", page_icon="🚨", layout="wide")

st.title("🚨 Log Monitoring and Alert System")
st.markdown("**Task 18:** Monitor log files for error patterns and trigger automated alerts when thresholds are crossed.")

# Sidebar Configuration Panel
st.sidebar.header("⚙️ Configuration Panel")
threshold = st.sidebar.slider("Error Threshold (Count)", min_value=1, max_value=20, value=3)
time_window = st.sidebar.slider("Time Window (Seconds)", min_value=10, max_value=300, value=60)
pattern = st.sidebar.text_input("Regex Error Pattern", value="ERROR|CRITICAL|FAIL")

# Initialize Session States
if "logs" not in st.session_state:
    st.session_state.logs = []
if "alerts" not in st.session_state:
    st.session_state.alerts = []
if "error_timestamps" not in st.session_state:
    st.session_state.error_timestamps = deque()

# Instantiate Log Monitor
monitor = LogMonitor(threshold=threshold, time_window=time_window, pattern=pattern)

# Layout Columns
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Live Log Simulation & Input")
    user_log = st.text_input("Enter log entry manually:", placeholder="e.g., Database connection timed out")
    
    if st.button("Submit Log Line"):
        if user_log:
            timestamped_log = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {user_log}"
            st.session_state.logs.append(timestamped_log)
            
            triggered, count = monitor.evaluate(timestamped_log, st.session_state.error_timestamps)
            if triggered:
                alert_msg = f"ALERT: Threshold crossed! {count} errors detected within {time_window}s."
                if alert_msg not in st.session_state.alerts:
                    st.session_state.alerts.append(alert_msg)

    st.markdown("---")
    st.write("Or simulate preset log events:")
    c1, c2, c3 = st.columns(3)
    
    if c1.button("Send Info Log"):
        log = f"[{datetime.now().strftime('%H:%M:%S')}] INFO: User successfully authenticated."
        st.session_state.logs.append(log)
        monitor.evaluate(log, st.session_state.error_timestamps)
        
    if c2.button("Send Warning Log"):
        log = f"[{datetime.now().strftime('%H:%M:%S')}] WARNING: Memory usage reached 85%."
        st.session_state.logs.append(log)
        monitor.evaluate(log, st.session_state.error_timestamps)
        
    if c3.button("Send Error Log"):
        log = f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: Failed to execute SQL query transaction."
        st.session_state.logs.append(log)
        triggered, count = monitor.evaluate(log, st.session_state.error_timestamps)
        if triggered:
            alert_msg = f"ALERT: Threshold crossed! {count} errors detected within {time_window}s."
            if alert_msg not in st.session_state.alerts:
                st.session_state.alerts.append(alert_msg)

    st.subheader("📜 Console Log Stream History")
    log_display = "\n".join(st.session_state.logs[-10:]) if st.session_state.logs else "No logs recorded yet."
    st.text_area("Log Output", value=log_display, height=200, disabled=True)

with col2:
    st.subheader("🚨 Alert Dashboard")
    st.metric(label="Errors in Current Window", value=len(st.session_state.error_timestamps))
    
    if st.session_state.alerts:
        for alert in reversed(st.session_state.alerts[-5:]):
            st.error(alert)
    else:
        st.success("System Stable. No threshold breaches.")
        
    if st.button("Clear History & Reset"):
        st.session_state.logs = []
        st.session_state.alerts = []
        st.session_state.error_timestamps.clear()
        st.rerun()