import asyncio
import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import init_db, get_db
from app.modules.leadradar.scanner import scanner

async def main():
    print("[*] Initializing LeadRadar SQLite Database...")
    await init_db()
    
    print("[*] Executing Live Social Intent Scan across Reddit & HackerNews...")
    res = await scanner.run_full_scan()
    print("\n" + "="*70)
    print(f"[✓] Scan Completed Successfully: {res}")
    print("="*70)
    
    db = await get_db()
    cursor = await db.execute("""
        SELECT id, source, author, title, intent_score, category, ai_suggested_reply 
        FROM leads 
        ORDER BY intent_score DESC 
        LIMIT 5
    """)
    top_leads = await cursor.fetchall()
    
    print(f"\n🔥 TOP 5 HIGH-INTENT BUYER LEADS DISCOVERED LIVE:\n")
    for idx, lead in enumerate(top_leads, 1):
        print(f"#{idx} [{lead['intent_score']}% INTENT] ({lead['category']}) - {lead['source']} by u/{lead['author']}")
        print(f"   Title: {lead['title']}")
        print(f"   Suggested Reply: {lead['ai_suggested_reply'][:120]}...\n")
    
    await db.close()

if __name__ == "__main__":
    asyncio.run(main())
