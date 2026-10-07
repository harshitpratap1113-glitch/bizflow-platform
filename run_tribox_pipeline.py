import os
import sys

sys.path.insert(0, os.path.abspath("backend"))

from app.db.database import init_db, get_db
from app.modules.leadradar.live_crawler import run_live_ingestion

print("1. Initializing Database Schema...")
init_db()

print("2. Running Tri-Box Massive Concurrent Ingestion across 45+ Communities...")
new_count = run_live_ingestion(sub_count=45)
print(f"Ingestion Finished! Fresh items inserted: {new_count}")

conn = get_db()
cursor = conn.cursor()

cursor.execute("SELECT count(*) FROM leads WHERE is_spam = 0 AND (lead_box = 'verified' OR (lead_box IS NULL AND intent_score >= 70))")
verified = cursor.fetchone()[0]

cursor.execute("SELECT count(*) FROM leads WHERE is_spam = 0 AND lead_box = 'general'")
general = cursor.fetchone()[0]

cursor.execute("SELECT count(*) FROM leads WHERE is_spam = 1 OR lead_box = 'spam'")
spam = cursor.fetchone()[0]

print("\n--- TRI-BOX RADAR LIVE METRICS ---")
print(f"🌟 Box 1: Verified Buyer Leads (Kaam Ki Leads): {verified}")
print(f"💬 Box 2: Casual Stream Box (General Discussions): {general}")
print(f"🛑 Box 3: Level-10 Spam Quarantine Vault: {spam}")
print(f"📊 Total Ingested Items in Radar: {verified + general + spam}")
conn.close()
