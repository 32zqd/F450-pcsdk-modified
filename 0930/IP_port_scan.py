import subprocess
import ipaddress
from concurrent.futures import ThreadPoolExecutor
import platform
import socket


def ping_ip(ip):
    """Ping an IP address and return if it responds."""
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', str(ip)]

    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT, timeout=1)
        return str(ip)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def scan_port(ip, port):
    """Scan a specific port on an IP address."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex((str(ip), port))
    sock.close()
    return result == 0


def scan_ports(ip, ports):
    """Scan multiple ports on an IP address."""
    open_ports = []
    for port in ports:
        if scan_port(ip, port):
            open_ports.append(port)
    return open_ports


def scan_network(network='192.168.1.0/24', ports=None):
    """Scan a network for responsive IP addresses and open ports."""
    if ports is None:
        # Common ports to scan
        ports = [21, 22, 23, 25, 53, 80, 443, 445, 3306, 3389, 8080]

    network = ipaddress.ip_network(network)
    results = {}

    # First find all responsive IPs
    print("Scanning for responsive hosts...")
    reachable_ips = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        ping_results = executor.map(ping_ip, network.hosts())
        for result in ping_results:
            if result:
                reachable_ips.append(result)

    # Then scan ports on responsive IPs
    print(f"Found {len(reachable_ips)} responsive hosts. Scanning ports...")
    for ip in reachable_ips:
        open_ports = scan_ports(ip, ports)
        if open_ports:
            results[ip] = open_ports

    return results


if __name__ == "__main__":
    # You can customize the ports to scan
    ports_to_scan = [21, 22, 23, 25, 53, 80,554, 443, 445, 3306, 3389, 8080, 8443]

    print("Scanning network 192.168.1.0/24...")
    scan_results = scan_network(ports=ports_to_scan)

    if scan_results:
        print("\nResults:")
        for ip, open_ports in scan_results.items():
            print(f"\n{ip} - Open ports:")
            for port in open_ports:
                service = socket.getservbyport(port, "tcp") if port < 1024 else "unknown"
                print(f"  - {port}/tcp ({service})")
    else:
        print("No open ports found on responsive hosts.")
