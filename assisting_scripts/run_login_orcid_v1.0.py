import http.server, socketserver, threading, requests, json, webbrowser, time

# === CONFIGURE YOUR ORCID APP DETAILS HERE ===
CLIENT_ID = "YOUR_ORCID_CLIENT_ID"
CLIENT_SECRET = "YOUR_ORCID_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:8000/callback"
TOKEN_URL = "https://orcid.org/oauth/token"
AUTH_URL = f"https://orcid.org/oauth/authorize?client_id={CLIENT_ID}&response_type=code&scope=/authenticate&redirect_uri={REDIRECT_URI}"

auth_code = None

class ORCIDHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        if "/callback" in self.path:
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)
            auth_code = query.get("code", [None])[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write("<h2>✅ ORCID login successful! You can close this window.</h2>".encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def start_server():
    with socketserver.TCPServer(("localhost", 8000), ORCIDHandler) as httpd:
        httpd.handle_request()  # wait for 1 request then exit

def main():
    global auth_code
    threading.Thread(target=start_server, daemon=True).start()

    print("🔑 Opening ORCID login page...")
    webbrowser.open(AUTH_URL)

    # wait until auth_code is set by callback
    while auth_code is None:
        time.sleep(0.1)

    # exchange code for token
    r = requests.post(TOKEN_URL, data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    })
    if r.status_code == 200:
        data = r.json()
        with open("orcid_result.json", "w") as f:
            json.dump(data, f, indent=2)
        print("✅ ORCID login complete:", data.get("orcid"))
    else:
        print("❌ Failed to exchange ORCID code:", r.text)
        with open("orcid_result.json", "w") as f:
            json.dump({"error": r.text}, f, indent=2)

if __name__ == "__main__":
    main()