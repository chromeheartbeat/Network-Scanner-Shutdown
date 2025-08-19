🛰️ Network Scanner & Remote Shutdown Tool

A Python-based tool to scan your local network, detect connected devices, identify whether they are PCs, servers, or mobile devices, and optionally remotely shut down PCs/servers.
Mobile devices (Android/iOS) and most IoT devices (smart TVs, printers, cameras) are detected but marked as not shutdown-capable for security reasons.

✨ Features

Detects all active devices on your subnet.

Displays IP, hostname, MAC address, and vendor/device type.

Identifies mobile devices (Apple, Samsung, Huawei, etc.) and flags them.

Supports remote shutdown for:

Windows PCs via shutdown /m (requires admin rights).

Linux/Mac via SSH with key-based authentication.

Saves results to alive_hosts.txt.

⚠️ Important Notes

🔑 Admin rights required to shut down PCs.

🔐 For Linux/Mac shutdown, configure SSH keys (no passwords).

📱 Mobile and IoT devices cannot be remotely shut down (unless managed by MDM).

🚨 Use responsibly — only on networks/devices you own or manage.

📦 Installation

Clone this repository:

git clone https://github.com/yourusername/network-scanner-shutdown.git
cd network-scanner-shutdown


Install required Python packages:

pip install -r requirements.txt

Requirements

Python 3.7+

Dependencies:

mac-vendor-lookup

psutil (optional if you extend)

⚙️ Usage

Run the script:

python network_scan.py


The tool will:

Detect your local IP and network.

Ping all devices in the subnet.

Display IP | Hostname | MAC | Device Type.

Save results into alive_hosts.txt.

After scanning, you’ll be prompted:

Do you want to shutdown a device? (y/n):


Select a device number. If it’s a PC/server:

For Windows: Sends shutdown via RPC.

For Linux/Mac: You’ll be asked for:

SSH username

Path to your private key (e.g., ~/.ssh/id_rsa)

🔑 SSH Key Setup (Linux/Mac Shutdown)

Generate SSH key (if not already done):

ssh-keygen -t rsa -b 4096


Copy your public key to the target machine:

ssh-copy-id username@target_ip


Test login (should not ask for password):

ssh username@target_ip


In the script, when asked, provide the same username and key_path.

📌 Example Output
[+] Active Devices:
 1. 10.125.131.1   | Hostname: router.local   | MAC: 00:11:22:33:44:55 | Type: Router
 2. 10.125.131.20  | Hostname: printer.office | MAC: 3c:52:82:9a:1f:2b | Type: HP
 3. 10.125.131.42  | Hostname: laptop-john    | MAC: a0:b1:c2:d3:e4:f5 | Type: Dell
 4. 10.125.131.55  | Hostname: iPhone.local   | MAC: 28:cf:e9:xx:xx:xx | Type: Mobile (Apple)
 5. 10.125.131.60  | Hostname: android-12345  | MAC: 88:32:9b:xx:xx:xx | Type: Mobile (Samsung)


Attempting to shutdown a mobile device will display:

[!] Shutdown not supported for mobile devices.

📜 License

This project is licensed under the MIT License.
Use at your own risk and only on authorized networks.
