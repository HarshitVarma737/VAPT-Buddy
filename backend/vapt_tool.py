import subprocess
import shutil
import os
import re
import json
import concurrent.futures
from dotenv import load_dotenv
import streamlit as st
from streamlit_chat import message

# Load environment variables
load_dotenv()

def run_command(command):
    """Executes a system command and returns the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return f"⚠️ Command Execution Error: {str(e)}"

# VAPT Tool Functions
def check_tool(tool):
    """Check if a tool is installed."""
    return shutil.which(tool) is not None

def detect_vulnerabilities(output):
    """Parse tool output to detect possible vulnerabilities."""
    vuln_patterns = {
        "🔴 CRITICAL": [r"SQL INJECTION", r"CVE-\d{4}-\d+", r"EXPLOIT AVAILABLE", r"RCE DETECTED"],
        "🟡 WARNING": [r"OUTDATED", r"WEAK CIPHER", r"UNPATCHED", r"PRIVILEGE ESCALATION"],
        "🟢 INFO": [r"OPEN PORT", r"DETECTED SERVICE", r"RUNNING VERSION"]
    }

    found_vulns = []
    for severity, patterns in vuln_patterns.items():
        for pattern in patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            if matches:
                found_vulns.append({"severity": severity, "details": matches})
    
    return found_vulns

def run_vapt_tool(command, timeout=60):
    """Run a shell command and parse for vulnerabilities."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        output = result.stdout if result.stdout else result.stderr
        return {"output": output, "vulnerabilities": detect_vulnerabilities(output)}
    except subprocess.TimeoutExpired:
        return {"output": "⏳ Timeout: Command took too long!", "vulnerabilities": []}
    except Exception as e:
        return {"output": f"⚠️ Exception: {str(e)}", "vulnerabilities": []}

def run_nmap(target, scan_type):
    if not check_tool("nmap"):
        return {"output": "❌ Nmap is not installed!", "vulnerabilities": []}

    scans = {
        "Service Detection": "-sV --top-ports 50 -T4",
        "Aggressive Scan": "-A --host-timeout 30s",
        "Ping Scan": "-sn",
        "UDP Scan": "-sU --top-ports 30 -T4",
        "OS Detection": "-O --max-retries 1"
    }
    return run_vapt_tool(f"sudo nmap {scans.get(scan_type, '-sV --top-ports 50 -T4')} {target}", timeout=45)

def aggregate_results(target, tool_scans):
    """Run selected VAPT tools concurrently."""
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            "Nmap": executor.submit(run_nmap, target, tool_scans.get("nmap", ""))
        }
        for tool, future in futures.items():
            results[tool] = future.result()
    return results