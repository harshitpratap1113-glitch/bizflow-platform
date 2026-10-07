import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))
from app.modules.leadradar.live_crawler import ALL_TARGET_COMMUNITIES

print("============================================================")
print("[*] BIZFLOW LEADRADAR: MULTI-INDUSTRY COMMUNITY REGISTRY")
print("============================================================")
print(f"[OK] Total Monitored Communities: {len(ALL_TARGET_COMMUNITIES)}")

categories = {}
for c in ALL_TARGET_COMMUNITIES:
    cat = c[2]
    categories[cat] = categories.get(cat, 0) + 1

print("\n--- Industry Breakdown ---")
for cat, count in sorted(categories.items()):
    print(f"  * {cat:30}: {count} Communities")
print("============================================================")
