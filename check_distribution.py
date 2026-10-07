import sqlite3
import os

db = sqlite3.connect(os.path.join(os.path.dirname(__file__), "backend", "app", "db", "bizflow.db"))
db.row_factory = sqlite3.Row

print("--- VERIFIED LEADS BY CATEGORY ---")
for row in db.execute("SELECT intent_category, count(*) as c FROM leads WHERE lead_box = 'verified' GROUP BY intent_category"):
    print(f"  {row['intent_category']}: {row['c']}")

print("\n--- GENERAL DISCUSSIONS BY CATEGORY ---")
for row in db.execute("SELECT intent_category, count(*) as c FROM leads WHERE lead_box = 'general' GROUP BY intent_category"):
    print(f"  {row['intent_category']}: {row['c']}")

print("\n--- GENERAL DISCUSSIONS BY COMMUNITY (Top 20) ---")
for row in db.execute("SELECT community, intent_category, count(*) as c FROM leads WHERE lead_box = 'general' GROUP BY community ORDER BY c DESC LIMIT 20"):
    print(f"  r/{row['community']} ({row['intent_category']}): {row['c']}")
