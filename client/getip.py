import socket
import ipaddress
from scapy.all import ARP, Ether, srp

def get_local_ip_range():
    host_name = socket.gethostname()
    local_ip = socket.gethostbyname(host_name)
    # Determine the local network's IP range (assuming a subnet mask of 255.255.255.0)
    ip_network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
    return str(ip_network)

def get_connected_devices():
    # Create an ARP request packet to get the list of devices in the specified IP range
    ip_range=get_local_ip_range()
    arp_request = ARP(pdst=ip_range)
    #for ipV6
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcast Ethernet frame
    # Combine Ether and ARP packets
    packet = ether/arp_request
    # Send the packet and receive the response
    result = srp(packet, timeout=3, verbose=0)[0]
    devices_list = []
    for sent, received in result:
        devices_list.append(received.psrc)

    return devices_list


