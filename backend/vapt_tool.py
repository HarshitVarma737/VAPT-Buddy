import subprocess
import shutil
import os
import re
import json
import concurrent.futures
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return f"⚠️ Command Execution Error: {str(e)}"

def check_tool(tool):
    return shutil.which(tool) is not None

def detect_vulnerabilities(output):
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
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            "Nmap": executor.submit(run_nmap, target, tool_scans.get("nmap", ""))
        }
        for tool, future in futures.items():
            results[tool] = future.result()
    return results

def query_huggingface(prompt):
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt
    }
    try:
        response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0 and 'generated_text' in result[0]:
                return result[0]['generated_text']
            else:
                return str(result)
        else:
            return f"❌ API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"❌ Exception: {str(e)}"
