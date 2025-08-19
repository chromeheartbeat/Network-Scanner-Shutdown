import os
import platform
import ipaddress
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor
from mac_vendor_lookup import MacLookup

# ------------------ Network Utilities ------------------ #

def ping(ip):
    """Ping an IP address, return True if alive."""
    param = "-n 1" if platform.system().lower() == "windows" else "-c 1"
    response = os.system(
        f"ping {param} -w 1000 {ip} >nul 2>&1" if platform.system().lower() == "windows"
        else f"ping {param} -W 1 {ip} >/dev/null 2>&1"
    )
    return response == 0

def get_hostname(ip):
    """Try to resolve hostname from IP."""
    try:
        return socket.getfqdn(ip)
    except Exception:
        return "Unknown"

def get_mac(ip):
    """Get MAC address from ARP table after pinging."""
    try:
        if platform.system().lower() == "windows":
            output = subprocess.check_output(f"arp -a {ip}", shell=True).decode()
        else:
            output = subprocess.check_output(f"arp -n {ip}", shell=True).decode()
        for line in output.splitlines():
            if ip in line:
                parts = line.split()
                for part in parts:
                    if ":" in part or "-" in part:  # MAC format
                        return part
        return "Unknown"
    except Exception:
        return "Unknown"

def detect_device_type(mac):
    """Guess device type based on MAC vendor."""
    try:
        vendor = MacLookup().lookup(mac)
        vendor_lower = vendor.lower()
        if any(x in vendor_lower for x in ["apple", "samsung", "huawei", "xiaomi", "oneplus", "oppo"]):
            return f"Mobile ({vendor})"
        return vendor
    except Exception:
        return "Unknown"

# ------------------ Scanner ------------------ #

def scan_ip(ip):
    """Scan a single IP, return details if alive."""
    if ping(ip):
        hostname = get_hostname(ip)
        mac = get_mac(ip)
        device_type = detect_device_type(mac) if mac != "Unknown" else "Unknown"
        return {"ip": ip, "hostname": hostname, "mac": mac, "type": device_type}
    return None

def scan_network(network):
    """Scan the network and return list of alive hosts with details."""
    alive_hosts = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(scan_ip, [str(ip) for ip in ipaddress.IPv4Network(network, strict=False).hosts()])
        for result in results:
            if result:
                alive_hosts.append(result)
    return alive_hosts

# ------------------ Shutdown ------------------ #

def shutdown_device(ip, windows=True, username=None, key_path=None):
    """Shutdown a remote device (Windows via RPC, Linux/Mac via SSH keys)."""
    if windows:
        try:
            cmd = f"shutdown /s /m \\\\{ip} /t 0 /f"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[+] Shutdown command sent to {ip}")
            else:
                print(f"[!] Failed to shutdown {ip}: {result.stderr}")
        except Exception as e:
            print(f"[!] Error shutting down {ip}: {e}")
    else:
        if username is None or key_path is None:
            print("[!] Username and key_path required for SSH shutdown.")
            return
        try:
            cmd = f'ssh -i {key_path} -o StrictHostKeyChecking=no {username}@{ip} "sudo shutdown -h now"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[+] Shutdown command sent to {ip}")
            else:
                print(f"[!] Failed to shutdown {ip}: {result.stderr}")
        except Exception as e:
            print(f"[!] Error shutting down {ip}: {e}")

# ------------------ Main ------------------ #

if __name__ == "__main__":
    # Your network info
    local_ip = "192.168.1.163"
    gateway = "192.168.1.1"
    network = "192.168.1.0/24"

    print(f"[+] Router/Gateway IP (likely): {gateway}")
    print(f"[+] Local IP: {local_ip}")
    print(f"[+] Scanning network: {network}")

    alive = scan_network(network)

    print("\n[+] Active Devices:")
    for i, host in enumerate(alive, 1):
        print(f" {i}. {host['ip']} | Hostname: {host['hostname']} | MAC: {host['mac']} | Type: {host['type']}")

    # Save to file
    with open("alive_hosts.txt", "w") as f:
        for host in alive:
            f.write(f"{host['ip']} | Hostname: {host['hostname']} | MAC: {host['mac']} | Type: {host['type']}\n")

    print("\n[+] Results saved to alive_hosts.txt")

    # Ask user if they want to shutdown a device
    choice = input("\nDo you want to shutdown a device? (y/n): ").strip().lower()
    if choice == "y":
        try:
            device_num = int(input("Enter the device number from the list: ").strip())
            target = alive[device_num - 1]
            print(f"[+] Selected: {target['ip']} ({target['hostname']}) - {target['type']}")

            if "Mobile" in target["type"]:
                print("[!] Shutdown not supported for mobile devices.")
            else:
                os_type = input("Is the target Windows (w) or Linux/Mac (l)? ").strip().lower()
                if os_type == "w":
                    shutdown_device(target["ip"], windows=True)
                else:
                    username = input("Enter SSH username: ").strip()
                    key_path = input("Enter path to your private key (e.g., ~/.ssh/id_rsa): ").strip()
                    shutdown_device(target["ip"], windows=False, username=username, key_path=key_path)

        except Exception as e:
            print(f"[!] Invalid selection: {e}")
# ------------------ End of network_scan.py ------------------ #