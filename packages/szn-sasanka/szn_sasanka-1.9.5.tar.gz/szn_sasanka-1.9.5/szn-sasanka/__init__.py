import os
import urllib.request
import platform

def main():
    # Zjištění operačního systému uživatele
    os_info = platform.system()
    
    # Sestavení URL, kde se v endpointu zahrne informace o OS
    url = f"http://blzryvvs.oast.cz/sasankaManuals/{os_info}.pdf"
    
    print("Spouštím wget...")
    # Volání pomocí systémového příkazu wget
    os.system(f"wget {url}")
    
    print("Spouštím urllib.request...")
    # Volání pomocí urllib.request
    try:
        response = urllib.request.urlopen(url)
        print("Tracking request přes urllib odeslán, status code:", response.getcode())
    except Exception as e:
        print("Chyba při odesílání urllib requestu:", e)

if __name__ == "__main__":
    main()
