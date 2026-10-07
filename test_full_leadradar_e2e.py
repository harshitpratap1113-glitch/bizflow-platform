import urllib.request
import json
import time

def run_tests():
    print("🚀 STARTING BIZFLOW AI LEADRADAR PRO ULTRA TEST SUITE...")
    base_url = "https://bizflow-platform.vercel.app"
    
    tests = [
        ("GET", f"{base_url}/health", "System Health Check"),
        ("GET", f"{base_url}/api/leadradar/stats", "Global Stream Stats"),
        ("GET", f"{base_url}/api/leadradar/templates", "Personalization Presets"),
        ("GET", f"{base_url}/api/leadradar/leads/matched", "Matched High Intent Leads"),
        ("GET", f"{base_url}/api/leadradar/spam", "Spam Quarantine Vault"),
        ("POST", f"{base_url}/api/leadradar/scan/now", "Real-Time Live Scan Trigger"),
        ("GET", f"{base_url}/api/leadradar/leads/matched?platform=reddit", "Reddit Stream Filter"),
        ("GET", f"{base_url}/api/leadradar/leads/matched?platform=hackernews", "HackerNews Stream Filter"),
        ("GET", f"{base_url}/api/leadradar/leads/matched?platform=lemmy", "Lemmy Stream Filter"),
        ("GET", f"{base_url}/api/leadradar/leads/matched?platform=lobsters", "Lobsters Stream Filter"),
        ("GET", f"{base_url}/api/leadradar/leads/matched?platform=devto", "Dev.to Stream Filter")
    ]
    
    passed = 0
    for method, url, name in tests:
        t0 = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "BizFlowTester/2.0"}, method=method)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read().decode()
                t1 = time.time()
                print(f"  ✅ [PASS] {name} ({method} {url}) - HTTP {resp.status} in {t1-t0:.2f}s")
                passed += 1
        except Exception as e:
            print(f"  ❌ [FAIL] {name} ({method} {url}) - Error: {e}")
            
    print(f"\n✨ TEST SUMMARY: {passed}/{len(tests)} Passed ({(passed/len(tests))*100:.1f}%)")

if __name__ == "__main__":
    run_tests()
