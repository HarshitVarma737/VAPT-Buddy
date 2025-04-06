import streamlit as st
import time
import sys
import os
import base64

# ✅ Ensure `set_page_config` is the first Streamlit command
st.set_page_config(page_title="Automated VAPT Tool", page_icon="🛡️", layout="wide")

# Ensure backend module is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

try:
    from vapt_tool import aggregate_results
except ModuleNotFoundError:
    st.error("❌ Backend module 'vapt_tool' not found. Ensure 'backend' directory contains '__init__.py'.")
    st.stop()

# Define scan types
scan_types = {
    "nmap": ["Service Detection", "Aggressive Scan", "Ping Scan", "UDP Scan", "OS Detection"],
    "sqlmap": ["Basic Scan", "DB Enumeration", "Table Enumeration", "Column Enumeration", "Data Dump"],
    "nikto": ["Basic Scan", "Tuning Scan", "SSL Scan", "Headers Scan", "Cookies Scan"],
    "gobuster": ["Directory Scan", "DNS Subdomain Scan", "VHost Scan", "File Scan", "Recursive Scan"],
    "whatweb": ["Standard Scan", "Aggressive Scan", "Plugin Detection", "Colorized Output", "Verbose Mode"],
    "wpscan": ["Basic Scan", "Theme Detection", "Plugin Detection", "User Enumeration", "Vulnerabilities Scan"],
    "sublist3r": ["Basic Subdomain Enumeration"],
    "metasploit": ["HTTP Version Scan", "FTP Version Scan", "SMB Scan", "SSH Scan", "SNMP Scan"]
}

# ✅ Use correct paths for assets
logo_path = "/Users/harshuvarma/Documents/VAPT_Project/logo1.png"
bg_path = "/Users/harshuvarma/Documents/VAPT_Project/bg.jpg"

# Function to set background image
def set_bg(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as file:
            encoded_string = base64.b64encode(file.read()).decode()
        bg_image = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """
        st.markdown(bg_image, unsafe_allow_html=True)

# ✅ Apply background if available
if os.path.exists(bg_path):
    set_bg(bg_path)
else:
    st.warning("⚠️ Background image not found!")

# ✅ Display logo correctly
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=100)
else:
    st.sidebar.warning("⚠️ Logo image not found!")

# Sidebar Elements
st.sidebar.title("Welcome to VAPT Buddy!!")
target = st.sidebar.text_input("Enter Target (IP/URL):")
selected_tools = st.sidebar.multiselect("Select Tools to Run:", list(scan_types.keys()))
st.sidebar.markdown("---")

# ✅ Validate target input
if target and not target.startswith(("http://", "https://", "www.")) and not target.replace(".", "").isdigit():
    st.sidebar.error("⚠️ Invalid Target! Enter a valid URL or IP address.")

selected_scans = {}
for tool in selected_tools:
    selected_scans[tool] = st.sidebar.selectbox(f"Select {tool} scan type:", scan_types[tool])

st.sidebar.markdown("---")

# Main content
st.markdown("<h1 style='text-align: center;'>🛡️ Automated VAPT Tool</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>A professional vulnerability assessment & penetration testing tool.</p>", unsafe_allow_html=True)
st.markdown("---")

# ✅ Manage scan state
if "scan_running" not in st.session_state:
    st.session_state.scan_running = False

if st.session_state.scan_running:
    if st.button("🛑 Stop Scan", key="stop_scan"):
        st.session_state.scan_running = False
        st.rerun()
else:
    if st.button("▶️ Start Scan", key="start_scan"):
        if not target:
            st.error("⚠️ Please enter a valid target IP or URL!")
        elif not selected_tools:
            st.error("⚠️ Please select at least one tool to scan!")
        else:
            st.session_state.scan_running = True
            st.rerun()

# ✅ Scan Execution with smooth progress bar
if st.session_state.scan_running and target and selected_tools:
    with st.spinner("Scan in progress..."):
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i in range(100):
            if not st.session_state.scan_running:
                st.warning("Scan Stopped! ⚠️")
                break
            time.sleep(0.05)
            progress_bar.progress(i + 1)
            status_text.text(f"Progress: {i + 1}%")

        if st.session_state.scan_running:
            results = aggregate_results(target, selected_scans)
            st.success("Scan Completed Successfully! ✅")
            for tool, output in results.items():
                st.markdown(f"### 🔍 Results from **{tool}**:")
                st.code(output, language="bash")
            st.session_state.scan_running = False

# ✅ Footer
st.markdown(
    """
    <div style="width: 100%; background-color: rgba(0, 0, 0, 0.8); color: white; text-align: center; padding: 15px; font-size: 14px; margin-top: 40px; border-top: 1px solid #444;">
        © 2025 Automated VAPT Tool by Harshit Varma. All rights reserved. <br/> Made with love in 🇮🇳 | <a href="https://yourwebsite.com/about" target="_blank">About the Team</a>
    </div>
    """,
    unsafe_allow_html=True,
)