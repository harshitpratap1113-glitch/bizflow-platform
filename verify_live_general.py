import urllib.request
import json

url = "https://bizflow-platform.vercel.app/api/leadradar/general"
req = urllib.request.Request(url, headers={"User-Agent": "BizFlowTester/2.0"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    leads = data.get("general_leads", [])
    print(f"[*] TOTAL CASUAL DISCUSSIONS ON LIVE VERCEL: {len(leads)}")
    cats = {}
    for l in leads:
        c = l.get("intent_category") or "General"
        cats[c] = cats.get(c, 0) + 1
    print("[*] BREAKDOWN BY CATEGORY ON LIVE:")
    for k, v in cats.items():
        print(f"   - {k}: {v}")
