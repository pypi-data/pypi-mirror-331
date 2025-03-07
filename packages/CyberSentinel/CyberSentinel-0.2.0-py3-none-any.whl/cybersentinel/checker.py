import requests
import socket
import ssl
import time

def check_website_status(url):
    """Check if the website is online and measure response time."""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=5)
        response_time = round((time.time() - start_time) * 1000, 2)  # in ms
        return response.status_code == 200, response_time
    except requests.exceptions.RequestException:
        return False, None

def check_ssl_certificate(url):
    """Check if the website has a valid SSL certificate."""
    try:
        hostname = url.replace('https://', '').replace('http://', '').split('/')[0]
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                return True  # If no exception, SSL is valid
    except Exception:
        return False

def main():
    url = input("Enter website URL (including https:// or http://): ")
    
    print("\nChecking website status...")
    is_online, response_time = check_website_status(url)
    if is_online:
        print(f"✅ Website {url} is ONLINE")
        print(f"⏳ Response Time: {response_time}ms")
    else:
        print(f"❌ Website {url} is OFFLINE")
        return
    
    print("\nChecking SSL certificate...")
    if check_ssl_certificate(url):
        print("🔒 SSL Certificate: VALID")
    else:
        print("🚨 SSL Certificate: INVALID or MISSING")
    from cybersentinel.malware_check import check_malware
    # Inside your main function (after SSL check)
    print("\nChecking for malware and phishing threats...")
    malware_status = check_malware(url)

    if malware_status:
     print("⚠️ WARNING: The website is flagged as MALICIOUS!")
    else:
     print("✅ The website is SAFE.")
     
if __name__ == "__main__":
    main()


from cybersentinel.malware_check import check_malware

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: cybersentinel <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    print("🔍 Checking website security...\n")
    
    # Call Malware & Phishing Detection
    result = check_malware(url)
    print(result)




